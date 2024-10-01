import backend.drugrepurposing.Utilities as ut
import torch
import networkx as nx
import os

print("Loading Initial Drug-Protein Graph")
initial_graph_filename = "drug_protein_network_trial.gpickle"
initial_graph_path = os.path.join(r"results\Graph", initial_graph_filename)
initial_graph = ut.load_graph(filename=initial_graph_path)
print("Initial Drug-Protein Graph Loaded")

external_graphs = []
data_directory = r"results\Graph"

# List all files in the directory and load graphs that end with ".gpickle" excluding the initial graph
for file in os.listdir(data_directory):
    if file.endswith(".gpickle") and file != initial_graph_filename and file != "drug_disease_network.gpickle":
        full_path = os.path.join(data_directory, file)
        print(f"Loading graph from {full_path}...")
        graph = ut.load_graph(filename=full_path)
        external_graphs.append(graph)

print(f"Loaded {len(external_graphs)} external graphs.")

def print_graph_summary(graphs):
    for i, g in enumerate(graphs):
        print(f"Graph {i} - Nodes: {len(g.nodes())}, Edges: {len(g.edges())}")

print_graph_summary(external_graphs)


#Find the connected Nodes in the initial graph
connected_nodes = [node for node in initial_graph.nodes if len(list(initial_graph.neighbors(node))) > 0]
# print(f"Connected nodes: {connected_nodes}")

# Find the disconnected nodes in the initial graph
disconnected_nodes = [node for node in initial_graph.nodes if len(list(initial_graph.neighbors(node))) == 0]
# print(f"Disconnected nodes: {disconnected_nodes}")

# Find the number of connected and disconnected nodes in the initial graph
num_connected_nodes = len(connected_nodes)
num_disconnected_nodes = len(disconnected_nodes)

print(f"Number of connected nodes in the initial graph: {num_connected_nodes}")
print(f"Number of disconnected nodes in the initial graph: {num_disconnected_nodes}")

# Get general information of the initial graph
print('Number of nodes in the initial graph:', len(initial_graph.nodes))
print('Number of edges in the initial graph:', len(initial_graph.edges))
print('Average degree in the initial graph:', sum(dict(initial_graph.degree).values()) / len(initial_graph.nodes))

# Get the density of the initial graph
density = nx.density(initial_graph)
print("Network density of the initial graph:", density)


# total nodes in a graph
nodes = initial_graph.nodes()
# vector = nodes.data()['C025205']['vector']
# print(f"Vector of node C025205: {vector}")
# vectors = {node: data['vector'] for node, data in initial_graph.nodes(data=True)}
# print(f"Vectors of all nodes in the graph: {vectors}")



# anchor_set = ut.find_anchor_set(disconnected_nodes[3], external_graphs, nodes)
# validation_set = ut.validate_set(anchor_set, connected_nodes)
# len_validation_set = len(validation_set)
# print (f'Anchor Set: {ut.find_anchor_set(disconnected_nodes[3], external_graphs, nodes)}')
# print(f"Validation Set: {ut.validate_set(ut.find_anchor_set(disconnected_nodes[3], external_graphs, nodes), connected_nodes)}")
# print(f"Length of Validation Set: {len_validation_set}")
device = 'cuda' if torch.cuda.is_available() else 'cpu'
complemented_graph = ut.connect_disconnected_nodes(initial_graph, disconnected_nodes, external_graphs, device='cpu')

# Save the complemented graph
print("Saving enhanced graph.....")
os.makedirs(r"results\spareGraphs", exist_ok=True)
graph_filename = "drug_protein_network_enhanced.gpickle"
result = os.path.join(r"results\spareGraphs", graph_filename)
ut.save_graph(Graph=complemented_graph, filename=result)

# Load the complemented graph
print("Loading enhanced graph.....")
complemented_graph = ut.load_graph(filename=result)

# Find the connected nodes in the complemented graph
connected_nodes_enhanced = [node for node in complemented_graph.nodes if len(list(complemented_graph.neighbors(node))) > 0]
# print(f"Connected nodes in the complemented graph: {connected_nodes_enhanced}")

# Find the disconnected nodes in the complemented graph
disconnected_nodes_enhanced = [node for node in complemented_graph.nodes if len(list(complemented_graph.neighbors(node))) == 0]
# print(f"Disconnected nodes in the complemented graph: {disconnected_nodes_enhanced}")

# Find the number of connected and disconnected nodes in the complemented graph
num_connected_nodes_enhanced = len(connected_nodes_enhanced)
num_disconnected_nodes_enhanced = len(disconnected_nodes_enhanced)

print(f"Number of connected nodes in the complemented graph: {num_connected_nodes_enhanced}")
print(f"Number of disconnected nodes in the complemented graph: {num_disconnected_nodes_enhanced}")

# Get general information of the complemented graph
print('Number of nodes in the complemented graph:', len(complemented_graph.nodes))
print('Number of edges in the complemented graph:', len(complemented_graph.edges))
print('Average degree in the complemented graph:', sum(dict(complemented_graph.degree).values()) / len(complemented_graph.nodes))

# Get the density of the complemented graph
density_enhanced = nx.density(complemented_graph)
print("Network density of the complemented graph:", density_enhanced)





# target_disease = 'Astrocytoma'
# known_drugs = ['C534883', 'C515697', 'C496879']
# model_path = 'results/Graph/drug_protein_network_trial.gpickle'
# drug_disease = pd.read_csv(r'data\Cleansed_CTD_chemicals_diseases.csv')

# drug_ranking = ut.drug_scoring(target_disease, known_drugs, model_path, drug_disease)
# print(f"Ranked drugs for {target_disease}: {drug_ranking}")