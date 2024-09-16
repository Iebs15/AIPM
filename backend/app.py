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
    model_path = os.path.join(base_path, '../backend/drugrepurposing/Drug-Repurposing-v1.0/results/Graph/drug_protein_network_trial.gpickle')
    drug_disease_path = os.path.join(base_path, '../backend/drugrepurposing/Drug-Repurposing-v1.0/data/Cleansed_CTD_chemicals_diseases.csv')

    # Read the CSV file using the constructed path
    drug_disease = pd.read_csv(drug_disease_path)

    # Use the utility function to calculate the drug scores
    drug_ranking = ut.drug_scoring(target_disease, known_drugs, model_path, drug_disease)

    # Return the ranked drugs as a JSON response
    print(drug_ranking)
    return jsonify(drug_ranking)

if __name__ == '__main__':
    app.run(debug=True)
