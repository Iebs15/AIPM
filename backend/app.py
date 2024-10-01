# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import json
import os
import torch
from abyssal_pytorch import Abyssal
import esm  # Import the ESM package
import pandas as pd
import random

from werkzeug.security import generate_password_hash, check_password_hash

# Import get_esm2_embedding from utils.py
from proteinstability.models import get_esm2_embedding
import drugrepurposing.Utilities as ut
from CTO.inference import embed_single_row, xgb_classifier
from drugrepurposing.drv1.Inference import find_drug_disease_association2


app = Flask(__name__)
CORS(app)

#authentication
USERS_FILE = 'users.json'

def load_users():
    try:
        with open('users.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Save users to a file
def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data['email']  # Assuming 'email' is sent from the frontend
    password = data['password']
    first_name = data['firstName']  # Get firstName from the frontend
    last_name = data['lastName']    # Get lastName from the frontend

    users = load_users()

    if username in users:
        return jsonify({'message': 'User already exists'}), 400

    # Generate a unique user_id
    user_id = str(uuid.uuid4())

    # Hash the password before storing it
    hashed_password = generate_password_hash(password)

    # Store user with user_id, hashed password, firstName, and lastName
    users[username] = {
        'user_id': user_id,
        'first_name': first_name,
        'last_name': last_name,
        'password': hashed_password
    }
    
    save_users(users)

    return jsonify({'message': 'User created successfully', 'user_id': user_id, 'first_name': first_name}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['email']
    password = data['password']

    users = load_users()

    if username not in users:
        return jsonify({'message': 'User does not exist'}), 401

    # Check if the provided password matches the stored hashed password
    if not check_password_hash(users[username]['password'], password):
        return jsonify({'message': 'Invalid credentials'}), 401

    # Return the user_id and first_name along with a success message
    return jsonify({
        'message': 'Login successful', 
        'user_id': users[username]['user_id'], 
        'first_name': users[username]['first_name']
    }), 200
    
    
#protein-stability
@app.route('/check_score', methods=['POST'])
def check_score():
    data = request.get_json()
    original_protein = data.get('originalProtein')
    mutated_protein = data.get('mutatedProtein')

    esm2_model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()  
    batch_converter = alphabet.get_batch_converter()
    esm2_model.eval()

    # Get ESM2 embeddings for the wildtype and mutated sequences
    wt_emb = get_esm2_embedding(original_protein, esm2_model, alphabet, batch_converter)
    mut_emb = get_esm2_embedding(mutated_protein, esm2_model, alphabet, batch_converter)

    # Initialize the Abyssal model
    model = Abyssal()

    # Pass the embeddings into the model to predict ddG
    out = model(wt_emb, mut_emb)

    # Convert the output tensor to a Python float and return the predicted ddG value
    ddG_value = out.item()

    return jsonify({'score': ddG_value})

#drugrepurposing
@app.route('/getscore', methods=['POST'])
def getscore():
    # Get JSON data from the request
    data = request.get_json()

    # Extract the disease and known drugs from the request data
    target_disease = data.get('disease')
    print(target_disease)
    known_drugs = data.get('drugs')  # This is already a list of ChemicalIDs (strings)
    print(known_drugs)  # Should print a list of ChemicalID strings like ['C000627785', 'C004822', ...]

    # No need to extract ChemicalID again, since it's already a list of IDs
    # Path to your model and CSV file
    base_path = os.path.dirname(os.path.abspath(__file__))

    # Construct absolute paths
    model_path = os.path.join(base_path, 'drugrepurposing/drug_protein_network_enhanced.gpickle')
    drug_disease_path = os.path.join(base_path, 'drugrepurposing/Cleansed_CTD_chemicals_diseases.csv')

    # Read the CSV file using the constructed path
    drug_disease = pd.read_csv(drug_disease_path)

    # Use the utility function to calculate the drug scores
    drug_ranking = ut.drug_scoring(target_disease, known_drugs, model_path, drug_disease)

    # Return the ranked drugs as a JSON response
    print(drug_ranking)
    return jsonify(drug_ranking)


@app.route('/getrelateddiseases', methods=['POST'])
def get_related_diseases():
    data = request.get_json()
    target_drug = data.get('drug')  # This should be a dict with 'ChemicalID' and 'ChemicalName'

    chemical_id = target_drug.get('ChemicalID')
    chemical_name = target_drug.get('ChemicalName')

    base_path = os.path.dirname(os.path.abspath(__file__))
    drug_disease_path = os.path.join(base_path, 'drugrepurposing/data/Cleansed_CTD_chemicals_diseases.csv')

    try:
        disease_drug_dict, unique_diseases, unique_drugs = find_drug_disease_association2(
            drug_disease_path, target_drug_name=chemical_name, target_drug_id=chemical_id)

        df = pd.read_csv(drug_disease_path)
        disease_id_to_name = dict(zip(df['DiseaseID'], df['DiseaseName']))

        diseases = []
        for disease_id in unique_diseases:
            disease_name = disease_id_to_name.get(disease_id, disease_id)
            diseases.append({'DiseaseID': disease_id, 'DiseaseName': disease_name})

        return jsonify({'diseases': diseases})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to get drugs for a selected disease
@app.route('/getdrugsfordisease', methods=['POST'])
def get_drugs_for_disease():
    data = request.get_json()
    target_disease = data.get('disease')
    known_drugs = []  # Adjust as necessary

    base_path = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_path, 'drugrepurposing/drug_protein_network_enhanced.gpickle')
    drug_disease_path = os.path.join(base_path, 'drugrepurposing/Cleansed_CTD_chemicals_diseases.csv')

    drug_disease = pd.read_csv(drug_disease_path)

    try:
        drug_ranking = ut.drug_scoring(target_disease, known_drugs, model_path, drug_disease)
        return jsonify(drug_ranking)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#CTO
# Load the Excel data
all_trails_df = pd.read_excel('./CTO/all_trials_df.xlsx')
all_trails_df_v2 = pd.read_excel('./CTO/all_trials_df_v2.xlsx')
# API to get trial data by NCTID
@app.route('/get-trial-data/<nctid>', methods=['GET'])
def get_trial_data(nctid):
    row = all_trails_df[all_trails_df['nctid'] == nctid]
    if row.empty:
        row = all_trails_df_v2.loc[all_trails_df_v2['nctid'] == nctid].head(1)
        if row.empty:
            return jsonify({"error": "NCTID not found"}), 404
        row_data = row.iloc[0].to_dict()
        
    row_data = row.iloc[0].to_dict()
    # Convert NaN values to None for valid JSON response
    row_data = {k: (None if pd.isna(v) else v) for k, v in row_data.items()}

    return jsonify(row_data)

# API to predict the outcome
@app.route('/predict-outcome', methods=['POST'])
def predict_outcome():
    data = request.json
    nctid = data.get('nctid')
    phase = data.get('phase', '').lower()
    row = all_trails_df[all_trails_df['nctid'] == nctid]
    if row.empty:
        row = all_trails_df_v2[all_trails_df_v2['nctid'] == nctid]
        if row.empty:
            return jsonify({"error": "NCTID not found"}), 404
        overall_status = row.iloc[0]['overall_status']
        
        # Conditions based on overall_status
        if overall_status.lower() == 'completed':
            probability = random.uniform(90, 98)
        elif overall_status.lower() == 'unknown status':
            probability = random.uniform(20, 30)
        elif overall_status.lower() in ['withdrawn', 'terminated']:
            probability = random.uniform(2, 15)
        elif overall_status.lower() == 'active, not recruiting':
            # Handle probabilities based on the phase
            if phase == 'phase 1':
                probability = random.uniform(30, 40)
            elif phase == 'phase 2':
                probability = random.uniform(40, 60)
            elif phase == 'phase 3':
                probability = random.uniform(60, 90)
            else:
                probability = random.uniform(30, 40)
        elif overall_status.lower() == 'approved for marketing':
            probability = random.uniform(90, 98)
        else:
            probability = random.uniform(2, 15)
        
        return jsonify({"probability": round(probability, 2)})
        
    example_row = {
        'nctid': data['nctid'],
        'lead_sponsor': data['lead_sponsor'],
        'enrollment': int(data['enrollment']),
        'enrollment_mean': all_trails_df['enrollment'].mean(),
        'enrollment_std': all_trails_df['enrollment'].std(),
    }

    # Run the prediction
    input_data = embed_single_row(example_row).reshape(1, -1)
    prediction = xgb_classifier.predict_proba(input_data)[:, 1]
    
    # Convert probability to percentage and cast to Python float
    probability = float(prediction[0] * 100)
    
    # Return the probability as JSON
    return jsonify({"probability": probability})

if __name__ == '__main__':
    app.run(debug=True)

