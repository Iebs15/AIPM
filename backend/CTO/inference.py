# import pandas as pd
# import numpy as np
# import pickle

# # Load embedding functions
# def load_nctid2molecule_embedding_dict():
#     with open('data/nctid2molecule_embedding_dict.pkl', 'rb') as pickle_file:
#         return pickle.load(pickle_file)

# def load_nctid2disease_embedding_dict():
#     with open('data/nctid2disease_embedding_dict.pkl', 'rb') as pickle_file:
#         return pickle.load(pickle_file)

# def load_sponsor2embedding_dict():
#     with open('data/sponsor2embedding_dict.pkl', 'rb') as pickle_file:
#         return pickle.load(pickle_file)

# def load_nctid2protocol_embedding_dict():
#     with open('data/nctid_2_protocol_embedding_dict.pkl', 'rb') as pickle_file:
#         return pickle.load(pickle_file)

# def embed_single_row(row):
#     nctid2molecule_embedding_dict = load_nctid2molecule_embedding_dict()
#     nctid2protocol_embedding_dict = load_nctid2protocol_embedding_dict()
#     nctid2disease_embedding_dict = load_nctid2disease_embedding_dict()
#     sponsor2embedding_dict = load_sponsor2embedding_dict()

#     h_m = nctid2molecule_embedding_dict[row['nctid']]
#     h_p = nctid2protocol_embedding_dict[row['nctid']]
#     h_d = nctid2disease_embedding_dict[row['nctid']]
#     h_s = sponsor2embedding_dict[row['lead_sponsor']]
#     enrollment = (row['enrollment'] - row['enrollment_mean']) / row['enrollment_std']
#     h_e = np.array([enrollment])

#     return np.hstack([h_m, h_p, h_d, h_s, h_e])

# # Load the trained model
# with open('xgboost_model.pkl', 'rb') as model_file:
#     xgb_classifier = pickle.load(model_file)

# # Example input row (replace with actual data)
# example_row = {
#     'nctid': 'NCT00000378',  # Replace with actual NCTID
#     'lead_sponsor': 'New York State Psychiatric Institute',  # Replace with actual sponsor
#     'enrollment': 110,  # Replace with actual enrollment
#     'enrollment_mean': 260.422736,  # Replace with dataset enrollment mean
#     'enrollment_std': 1263.848645,   # Replace with dataset enrollment std
# }

# # Embed the input row and run inference
# input_data = embed_single_row(example_row)
# input_data = input_data.reshape(1, -1)  # Reshape for single sample prediction
# prediction = xgb_classifier.predict_proba(input_data)[:, 1]

# print(f"Prediction for input: {prediction[0]:.3f}")


import pandas as pd
import numpy as np
import pickle
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, 'xgboost_model.pkl')
molecule_embedding_path = os.path.join(current_dir, 'nctid2molecule_embedding_dict.pkl')
disease_embedding_path = os.path.join(current_dir, 'nctid2disease_embedding_dict.pkl')
sponsor_embedding_path = os.path.join(current_dir, 'sponsor2embedding_dict.pkl')
protocol_embedding_path = os.path.join(current_dir, 'nctid_2_protocol_embedding_dict.pkl')

# Load the molecule embedding dictionary
def load_nctid2molecule_embedding_dict():
    with open(molecule_embedding_path, 'rb') as pickle_file:
        return pickle.load(pickle_file)

# Load the disease embedding dictionary
def load_nctid2disease_embedding_dict():
    with open(disease_embedding_path, 'rb') as pickle_file:
        return pickle.load(pickle_file)

# Load the sponsor embedding dictionary
def load_sponsor2embedding_dict():
    with open(sponsor_embedding_path, 'rb') as pickle_file:
        return pickle.load(pickle_file)

# Load the protocol embedding dictionary
def load_nctid2protocol_embedding_dict():
    with open(protocol_embedding_path, 'rb') as pickle_file:
        return pickle.load(pickle_file)
# Load embedding functions
# def load_nctid2molecule_embedding_dict():
#     with open('../CTO/nctid2molecule_embedding_dict.pkl', 'rb') as pickle_file:
#         return pickle.load(pickle_file)
    
# def load_nctid2molecule_embedding_dict():
#     with open(molecule_embedding_path, 'rb') as pickle_file:
#         return pickle.load(pickle_file)


def embed_single_row(row):
    nctid2molecule_embedding_dict = load_nctid2molecule_embedding_dict()
    nctid2protocol_embedding_dict = load_nctid2protocol_embedding_dict()
    nctid2disease_embedding_dict = load_nctid2disease_embedding_dict()
    sponsor2embedding_dict = load_sponsor2embedding_dict()

    h_m = nctid2molecule_embedding_dict[row['nctid']]
    h_p = nctid2protocol_embedding_dict[row['nctid']]
    h_d = nctid2disease_embedding_dict[row['nctid']]
    h_s = sponsor2embedding_dict[row['lead_sponsor']]
    enrollment = (row['enrollment'] - row['enrollment_mean']) / row['enrollment_std']
    h_e = np.array([enrollment])

    return np.hstack([h_m, h_p, h_d, h_s, h_e])

# Load the trained model
# with open('xgboost_model.pkl', 'rb') as model_file:
#     xgb_classifier = pickle.load(model_file)
with open(model_path, 'rb') as model_file:
    xgb_classifier = pickle.load(model_file)