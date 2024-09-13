import backend.drugrepurposing.Utilities as ut
import pandas as pd
import os

# load enhanced graph
print("Loading Enhanced Drug-Protein Graph")
enhanced_graph_filename = "drug_protein_network.gpickle"
enhanced_graph_path = os.path.join(r"results\Graph", enhanced_graph_filename)
enhanced_graph = ut.load_graph(filename=enhanced_graph_path)
print("Enhanced Drug-Protein Graph Loaded")

target_disease = 'Astrocytoma'
known_drugs = ['C534883', 'C515697', 'C496879']
model_path = 'results/Graph/drug_protein_network_trial.gpickle'
drug_disease = pd.read_csv(r'data\Cleansed_CTD_chemicals_diseases.csv')

drug_ranking = ut.drug_scoring(target_disease, known_drugs, model_path, drug_disease)
print(f"Ranked drugs for {target_disease}: {drug_ranking}")