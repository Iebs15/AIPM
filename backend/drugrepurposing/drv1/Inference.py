# import backend.drugrepurposing.Utilities as ut
# import pandas as pd
# import os

# # load enhanced graph
# print("Loading Enhanced Drug-Protein Graph")
# enhanced_graph_filename = "drug_protein_network.gpickle"
# enhanced_graph_path = os.path.join(r"results\Graph", enhanced_graph_filename)
# enhanced_graph = ut.load_graph(filename=enhanced_graph_path)
# print("Enhanced Drug-Protein Graph Loaded")

# target_disease = 'Astrocytoma'
# known_drugs = ['C534883', 'C515697', 'C496879']
# model_path = 'results/Graph/drug_protein_network_trial.gpickle'
# drug_disease = pd.read_csv(r'data\Cleansed_CTD_chemicals_diseases.csv')

# drug_ranking = ut.drug_scoring(target_disease, known_drugs, model_path, drug_disease)
# print(f"Ranked drugs for {target_disease}: {drug_ranking}")


import drugrepurposing.Utilities  as ut
import pandas as pd
import os
 
# load enhanced graph
print("Loading Enhanced Drug-Protein Graph")
enhanced_graph_filename = "drug_protein_network_trial.gpickle"
enhanced_graph_path = os.path.join(r"results\Graph\small", enhanced_graph_filename)
enhanced_graph = ut.load_graph(filename=enhanced_graph_path)
print("Enhanced Drug-Protein Graph Loaded")
 
# def find_drug_disease_association2(excel_path, target_drug_name):
#     # Check if the file exists
#     if not os.path.exists(excel_path):
#         raise FileNotFoundError(f"The file at '{excel_path}' does not exist.")
   
#     # Load the Excel file into a pandas DataFrame
#     try:
#         df = pd.read_csv(excel_path)
#     except Exception as e:
#         raise ValueError(f"Error loading file: {e}")
   
#     # Ensure the required columns exist
#     required_columns = {'ChemicalName', 'ChemicalID', 'DiseaseID'}
#     if not required_columns.issubset(df.columns):
#         raise ValueError(f"The required columns {required_columns} are missing from the Excel file.")
   
#     # Normalize ChemicalName column for case-insensitive comparison
#     df['ChemicalName'] = df['ChemicalName'].str.lower()
 
#     # Find the ChemID for the target drug (case-insensitive)
#     target_drug_row = df[df['ChemicalName'] == target_drug_name.lower()]
#     if target_drug_row.empty:
#         raise ValueError(f"Drug '{target_drug_name}' not found in the dataset.")
   
#     # Extract the ChemicalID for the target drug
#     target_chem_id = target_drug_row['ChemicalID'].values[0]
 
#     # Find the unique DiseaseIDs associated with the target drug
#     associated_diseases = df[df['ChemicalID'] == target_chem_id]['DiseaseID'].unique()
 
#     if len(associated_diseases) == 0:
#         return {}, set(), set()  # No associated diseases or drugs found
   
#     # Precompute a dictionary mapping DiseaseID to associated drugs to reduce redundant DataFrame filtering
#     disease_drug_dict = {}
#     for disease_id in associated_diseases:
#         associated_drugs = df[df['DiseaseID'] == disease_id]['ChemicalName'].unique().tolist()
#         if len(associated_drugs) > 1 and associated_drugs not in disease_drug_dict.values():
#             disease_drug_dict[disease_id] = associated_drugs
   
#     # Extract unique diseases and drugs
#     unique_diseases = set(associated_diseases)
#     unique_drugs = {drug for drugs in disease_drug_dict.values() for drug in drugs}
 
#     return disease_drug_dict, unique_diseases, unique_drugs
 
 
def find_drug_disease_association2(excel_path, target_drug_name=None, target_drug_id=None):
    # Check if the file exists
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"The file at '{excel_path}' does not exist.")
   
    # Load the CSV file into a pandas DataFrame
    try:
        df = pd.read_csv(excel_path)
    except Exception as e:
        raise ValueError(f"Error loading file: {e}")
   
    # Ensure the required columns exist
    required_columns = {'ChemicalName', 'ChemicalID', 'DiseaseID'}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"The required columns {required_columns} are missing from the Excel file.")
   
    # Normalize ChemicalName column for case-insensitive comparison
    df['ChemicalName'] = df['ChemicalName'].str.lower()

    if target_drug_id:
        target_drug_row = df[df['ChemicalID'] == target_drug_id]
    elif target_drug_name:
        target_drug_row = df[df['ChemicalName'] == target_drug_name.lower()]
    else:
        raise ValueError("Either target_drug_name or target_drug_id must be provided.")
 
    if target_drug_row.empty:
        raise ValueError(f"Drug '{target_drug_name or target_drug_id}' not found in the dataset.")
   
    # Extract the ChemicalID for the target drug
    target_chem_id = target_drug_row['ChemicalID'].values[0]

    # Find the unique DiseaseIDs associated with the target drug
    associated_diseases = df[df['ChemicalID'] == target_chem_id]['DiseaseID'].unique()

    if len(associated_diseases) == 0:
        return {}, set(), set()  # No associated diseases or drugs found
   
    # Precompute a dictionary mapping DiseaseID to associated drugs
    disease_drug_dict = {}
    for disease_id in associated_diseases:
        associated_drugs = df[df['DiseaseID'] == disease_id]['ChemicalName'].unique().tolist()
        if len(associated_drugs) > 1 and associated_drugs not in disease_drug_dict.values():
            disease_drug_dict[disease_id] = associated_drugs
   
    # Extract unique diseases and drugs
    unique_diseases = set(associated_diseases)
    unique_drugs = {drug for drugs in disease_drug_dict.values() for drug in drugs}

    return disease_drug_dict, unique_diseases, unique_drugs


disease_drug_dict, unique_diseases, unique_drugs = find_drug_disease_association2(r'data\small\Cleansed_CTD_chemicals_diseases.csv', '10074-G5')
 
target_disease = 'Astrocytoma'
known_drugs = unique_drugs
 
model_path = 'results\Graph\small\drug_protein_network_trial.gpickle'
drug_disease = pd.read_csv(r'data\small\Cleansed_CTD_chemicals_diseases.csv')
 
drug_ranking = ut.drug_scoring(target_disease, known_drugs, model_path, drug_disease)
print(f"Ranked drugs for {target_disease}: {drug_ranking}")