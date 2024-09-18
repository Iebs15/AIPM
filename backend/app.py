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

from werkzeug.security import generate_password_hash, check_password_hash

# Import get_esm2_embedding from utils.py
from proteinstability.models import get_esm2_embedding
import drugrepurposing.Utilities as ut
from CTO.inference import embed_single_row, xgb_classifier


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


# Load the Excel data
toy_df = pd.read_excel('./CTO/all_trials_df.xlsx')

# API to get trial data by NCTID
@app.route('/get-trial-data/<nctid>', methods=['GET'])
def get_trial_data(nctid):
    row = toy_df[toy_df['nctid'] == nctid]
    if row.empty:
        return jsonify({"error": "NCTID not found"}), 404
    row_data = row.iloc[0].to_dict()

    # Convert NaN values to None for valid JSON response
    row_data = {k: (None if pd.isna(v) else v) for k, v in row_data.items()}

    return jsonify(row_data)

# API to predict the outcome
@app.route('/predict-outcome', methods=['POST'])
def predict_outcome():
    data = request.json
    example_row = {
        'nctid': data['nctid'],
        'lead_sponsor': data['lead_sponsor'],
        'enrollment': int(data['enrollment']),
        'enrollment_mean': toy_df['enrollment'].mean(),
        'enrollment_std': toy_df['enrollment'].std(),
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

