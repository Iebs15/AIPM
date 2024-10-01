import numpy as np
import pandas as pd
import networkx as nx
from sklearn.metrics.pairwise import cosine_similarity
import backend.drugrepurposing.Config as conf
from sklearn.metrics import roc_auc_score 
from pyvis.network import Network
import backend.drugrepurposing.Utilities as ut
import os


# Load the data
df = pd.read_csv(r"results\vector_str_data\Cleansed_CTD_chem_gene_ixns.csv")


# Apply the parsing function to the 'Protein_vector' column
df['encoding_vector'] = df['vector_str'].apply(lambda x:np.array(list(map(float, x.split('|')))))


# Check if any vector is empty
empty_vectors = df['encoding_vector'][df['encoding_vector'].apply(lambda x: x.size == 0)]
# print(f"Number of empty vectors: {len(empty_vectors)}")
if not empty_vectors.empty:
    print("Sample empty vectors:")
    print(empty_vectors.head())
    
# Convert the list of vectors into a NumPy array
# Filter out any empty vectors
drug_vectors = np.array([v for v in df['encoding_vector'] if v.size > 0])

# Check if the vectors have been correctly parsed and have the same length
if len(drug_vectors) == 0:
    raise ValueError("No valid vectors found. Please check the 'Protein_vector' column data.")

# vector_lengths = [len(v) for v in drug_vectors] # for double checking the length of vector 
# print(f"Vector lengths: {set(vector_lengths)}")  # Should show a single length if all vectors are consistent

# Create a DataFrame from the drug vectors
drug_data_df = pd.DataFrame(drug_vectors)
# print(f"Drug DataFrame Shape: {drug_data_df.shape}")

# print(drug_data_df.head())

# Extract ChemicalID values
chemical_ids = df['ChemicalID'].iloc[df['encoding_vector'].index[df['encoding_vector'].apply(lambda x: x.size > 0)]].tolist()

# print(chemical_ids)

# Compute cosine similarity matrix
similarity_matrix = cosine_similarity(drug_data_df)

# print("Similarity Metrics:")
# print(similarity_matrix)
# print(similarity_matrix.shape)
# print(similarity_matrix[0].shape)

# # Assuming ground truth labels (y_true) and similarity scores (y_scores) exist
# y_true = np.random.randint(0, 2, size= similarity_matrix.size)
# y_scores = similarity_matrix.flatten()

# # Calculate AUC-ROC
# auc_roc = roc_auc_score(y_true, y_scores)
# threshold = auc_roc  # Store the AUC-ROC in the variable 'threshold'
# print(f"AUC-ROC: {threshold}")


def create_graph(df, similarity_matrix):
    G = nx.Graph()

    # Add nodes with ChemicalID as node identifiers
    for _, row in df.iterrows():
        chemical_id = row['ChemicalID']
        # print(chemical_id)
        vector_str = row['encoding_vector']
        # print(vector_str)
        G.add_node(chemical_id, vector=vector_str)

    # Create a list of all edges with their similarity values
    edges = []
    for i in range(len(df)):
        for j in range(i + 1, len(df)):
            weight = similarity_matrix[i, j]
            if weight > conf.protein_threshold:  # Ensure positive similarity
                chemical_id_i = df.iloc[i]['ChemicalID']
                chemical_id_j = df.iloc[j]['ChemicalID']
                edges.append((chemical_id_i, chemical_id_j, weight))

    # Create a graph from the edges
    G.add_weighted_edges_from(edges)

    return G


# Create the graph
G = create_graph(df, similarity_matrix)

# Find connected components
connected_comp = list(nx.connected_components(G))
largest_cc = max(connected_comp, key=len)
num_connected_drugs = len(largest_cc)
num_disc_drugs = len(df) - num_connected_drugs

print("num_connected_drugs", num_connected_drugs)
print("num_disc_drugs", num_disc_drugs)

# Give the graph a name
G.name = 'Drug Interactions Network'

# Obtain general information of graph
print('Number of nodes', len(G.nodes))
print('Number of edges', len(G.edges))
print('Average degree', sum(dict(G.degree).values()) / len(G.nodes))

# Get graph density
density = nx.density(G)
print("Network density:", density)

# Save the graph
print("Saving a graph.....")
os.makedirs(conf.graph_result, exist_ok=True)

graph_filename = "drug_protein_network_trial.gpickle"
result = os.path.join(conf.graph_result, graph_filename)
ut.save_graph(Graph=G, filename=result)

#Load the graph 
print("Loading a graph.....")
G = ut.load_graph(filename=result)

# print vector of nodes
# print(G.nodes.data())
print(G.nodes.data()['C025205']['vector'])

def draw_and_save_graph_pyvis(G, filename):
    net = Network(notebook=True, height="750px", width="100%", bgcolor="#ffffff", font_color="black")
    
    # Add nodes
    for node in G.nodes(data=True):
        net.add_node(node[0], label=node[0])
    
    # Add edges
    for edge in G.edges(data=True):
        net.add_edge(edge[0], edge[1], weight=edge[2].get('weight', 1))
    
    # Customize the layout and appearance
    net.force_atlas_2based()
    
    # Save the graph as an HTML file
    net.save_graph(filename)

# # Save the graph as an HTML file
draw_and_save_graph_pyvis(G, r"results\visualize\drug_protein_network_trial.html")

print("Graph saved as HTML.")

