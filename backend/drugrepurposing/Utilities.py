import pandas as pd
import numpy as np
import torch
import pickle
import networkx as nx
import drugrepurposing.Config as conf
import psutil

def print_memory_usage():
    """Monitor memory usage to detect memory spikes."""
    process = psutil.Process()
    mem_info = process.memory_info()
    print(f"Memory usage: {mem_info.rss / (1024 * 1024):.2f} MB")  # RSS memory in MB

def save_graph(Graph, filename):
    with open(filename, 'wb') as f:
        pickle.dump(Graph, f, pickle.HIGHEST_PROTOCOL)
    print(f"Graph saved at {filename}")

def load_graph(filename):
    with open(filename, 'rb') as f:
        G = pickle.load(f)
    print(f"Graph loaded from {filename}.")
    return G

def compute_laplacian_matrix(W):
    """Computes the Laplacian matrix L from the weighted adjacency matrix W."""
    D = torch.diag(W.sum(dim=1))
    L = D - W
    return L

def compute_weight_matrix(graph, sigma=1.0, device='cpu', batch_size=100):
    """
    Computes the weighted adjacency matrix W using a Gaussian similarity function with PyTorch and CUDA in batches.
    
    Parameters:
        graph: A networkx graph object representing the drug network.
        sigma: Parameter controlling the width of the Gaussian function.
        batch_size: Number of vectors to process at a time.
        device: The device to use for computation ('cpu' or 'cuda').
        
    Returns:
        weight_matrix: The weighted adjacency matrix W as a torch tensor.
    """
    nodes_list = list(graph.nodes())
    node_vectors_np = np.array([graph.nodes[node]['vector'] for node in nodes_list])

    # Convert to torch tensor and move to GPU if available
    node_vectors = torch.tensor(node_vectors_np, device=device, dtype=torch.float32)
    num_nodes = len(node_vectors)

    # Initialize adjacency matrix on the correct device
    adjacency_matrix = torch.tensor(nx.to_numpy_array(graph, nodelist=nodes_list), device=device, dtype=torch.float32)

    # Initialize weight matrix on the correct device
    weight_matrix = torch.zeros((num_nodes, num_nodes), device=device, dtype=torch.float32)

    # Batch processing for pairwise distances
    with torch.no_grad():  # No need to track gradients
        for i in range(0, num_nodes, batch_size):
            for j in range(0, num_nodes, batch_size):
                # Process only a small batch of rows and columns at a time
                batch_vectors_row = node_vectors[i:i + batch_size]
                batch_vectors_col = node_vectors[j:j + batch_size]

                # Compute pairwise distances in small batches
                diff_batch = batch_vectors_row.unsqueeze(1) - batch_vectors_col.unsqueeze(0)
                dist_matrix_batch = torch.sum(diff_batch ** 2, dim=-1)

                # Apply Gaussian similarity
                weight_batch = torch.exp(-dist_matrix_batch / (2 * sigma ** 2))

                # Multiply by adjacency matrix
                weight_batch *= adjacency_matrix[i:i + batch_size, j:j + batch_size]

                # Accumulate the result into the weight matrix
                weight_matrix[i:i + batch_size, j:j + batch_size] = weight_batch

                # # Free GPU memory after processing the sub-batch
                # del diff_batch, dist_matrix_batch, weight_batch
                # torch.cuda.empty_cache()

    return weight_matrix


def ssl(graph, anchor_nodes, label_node, device='cpu', mu=0.5):
    """
    Performs semi-supervised learning to compute f-scores for anchor nodes.
    
    Parameters:
        graph: The drug network (networkx graph).
        anchor_nodes: List of anchor nodes for the disconnected node.
        label_node: The disconnected node to be connected.
        device: Device to run the computation ('cpu' or 'cuda').
        mu: Regularization parameter for the Laplacian matrix.
        
    Returns:
        f_scores: The f-scores for the anchor nodes.
    """
    num_nodes = graph.number_of_nodes()

    # Compute weight matrix in batches
    W = compute_weight_matrix(graph, device=device)
    L = compute_laplacian_matrix(W)

    identity_matrix = torch.eye(num_nodes).to(device)
    y = torch.zeros(num_nodes, 1).to(device)
    y[label_node] = 1  # Label the disconnected node

    # Solve the optimization problem: f = (I + μL)^-1 y
    f_scores = torch.linalg.solve(identity_matrix + mu * L, y)

    return f_scores[anchor_nodes]

def find_anchor_set(disconnected_node, external_graphs, nodes):
    """
    Finds the anchor set for a disconnected node using external drug networks.
    
    Parameters:
        disconnected_node: Node in the initial network that is disconnected.
        external_graphs: List of external drug networks (networkx graphs).
        
    Returns:
        anchor_set: Set of candidate anchor nodes in the initial network.
    """
    anchor_set = set()
    for ext_graph in external_graphs:
        if disconnected_node in ext_graph:
            neighbors = set(ext_graph.neighbors(disconnected_node))
            # Only include neighbors that are also in the initial graph
            anchor_set.update(neighbors.intersection(nodes))
    return anchor_set

def validate_set(anchor_set, connected_set):
    """
    Validates the anchor set based on the connected set.
    
    Parameters:
        anchor_set: Set of anchor nodes.
        connected_set: Set of connected nodes.
        
    Returns:
        Validation set : connected_set / anchor_set.
    """
    connected_set = set(connected_set)  # Ensure connected_set is a set
    return connected_set - anchor_set  # Set difference

def connect_disconnected_nodes(graph, disconnected_nodes, external_graphs, device='cpu', batch_size=500):
    """
    Connects disconnected nodes to the initial network based on f-scores in batches.
    
    Parameters:
        graph: The initial drug network.
        disconnected_nodes: List of nodes that are disconnected in the initial network.
        external_graphs: List of external drug networks.
        batch_size: Number of nodes to process at a time to manage memory usage.
        device: Device to run the computation ('cpu' or 'cuda').
        
    Returns:
        graph: The complemented drug network.
    """
     # Check if CUDA is available and set device accordingly
    if device is None:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    print("Running on device for function:", device)

    # with torch.no_grad():
    initial_nodes = set(graph.nodes())  # Get the initial nodes for comparison
    
    for node in disconnected_nodes:
        anchor_set = find_anchor_set(node, external_graphs, initial_nodes)
        if not anchor_set:
            continue
        
        # Convert anchor nodes and disconnected node to indices in batches
        anchor_indices = torch.tensor([list(graph.nodes()).index(n) for n in anchor_set], device=device)
        node_index = list(graph.nodes()).index(node)

        # Compute f-scores for the node with respect to the anchor set
        f_scores = ssl(graph, anchor_indices, node_index, device=device)

        # Sort the anchors by f-scores and connect the highest-scoring anchors
        sorted_anchors = [list(anchor_set)[i] for i in torch.argsort(f_scores, descending=True)]

        for anchor in sorted_anchors:
            graph.add_edge(node, anchor)
            
            # Validate the new connection based on the epsilon parameter
            if not validate_connection(graph, anchor_set, conf.epsilon):
                graph.remove_edge(node, anchor)
                break  # Stop if connection fails validation

        # Free memory after processing the node batch
        # torch.cuda.empty_cache()

    return graph


def validate_connection(graph, anchor_set, epsilon):
    """
    Validates a new connection in the graph based on the performance threshold epsilon.
    
    Parameters:
        graph: The drug network.
        epsilon: Performance threshold for accepting new connections.
        
    Returns:
        valid: True if the new connection is valid, False otherwise.
    """
    return True  # Placeholder for validation logic

def semi_supervised_learning(L, y, mu=0.1):
    """Compute the f-scores using the SSL formula: f = (I + μL)^-1 y."""
    I = torch.eye(L.size(0), device=L.device).double()
    f_scores = torch.inverse(I + mu * L).matmul(y)
    return f_scores


def drug_scoring(disease, known_drugs, model_path, drug_disease, device='cpu'):
    """Score drugs based on semi-supervised learning (SSL)."""
    # Step 1: Load the model (enhanced drug network graph)
    G = load_graph(model_path)

    # Step 2: Validate known drugs in the graph
    nodes = G.nodes()
    known_drugs_in_graph = [drug for drug in known_drugs if drug in nodes]

    # Step 3: Get drugs associated with the target disease
    associated_drugs = drug_disease[drug_disease['DiseaseName'] == disease]['ChemicalID'].tolist()

    # Step 4: Create semi-labeled set of drugs
    semi_labeled_set = list(nodes)
    drug_to_index = {drug: idx for idx, drug in enumerate(semi_labeled_set)}

    # Step 5: Convert drugs to indices
    known_drugs_indices = [drug_to_index[drug] for drug in known_drugs_in_graph if drug in drug_to_index]
    associated_drugs_indices = [drug_to_index[drug] for drug in associated_drugs if drug in drug_to_index]

    # Create label tensor
    labels = torch.zeros(len(semi_labeled_set), dtype=torch.double, device=device)
    known_drugs_tensor = torch.tensor(known_drugs_indices, dtype=torch.long, device=device)
    associated_drugs_tensor = torch.tensor(associated_drugs_indices, dtype=torch.long, device=device)

    # Set known and associated drug labels
    labels[known_drugs_tensor] = 1
    labels[associated_drugs_tensor] = 0.8

    # Step 6: Compute Laplacian matrix L
    W = compute_weight_matrix(G, device=device)
    L = compute_laplacian_matrix(W).double()

    # Ensure L is on the correct device
    L = L.to(device)

    # Step 7: Perform semi-supervised learning (SSL)
    f_scores = semi_supervised_learning(L, labels)

    # Step 8: Convert f-scores to percentages and apply threshold
    f_scores_percentage = f_scores * 100  # Convert scores to percentages

    # Create a dictionary of drug scores
    drug_scores = {semi_labeled_set[i]: f_scores_percentage[i].item() for i in range(len(f_scores))}

    # Set the threshold (60%)
    threshold = 70

    # Filter out drugs below the threshold
    # filtered_drug_scores = {drug: score for drug, score in drug_scores.items() if score >= threshold}

    # Sort the filtered drugs
    sorted_drugs = sorted(drug_scores.items(), key=lambda item: item[1], reverse=True)

    # Format the scores as percentages
    formatted_drug_scores = {drug: f"{int(score)}%" for drug, score in sorted_drugs}

    return formatted_drug_scores


if __name__ == '__main__':
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Monitor memory usage before and after drug scoring
    print_memory_usage()
    
    target_disease = 'Astrocytoma'
    known_drugs = ['C534883', 'C515697', 'C496879']
    model_path = 'results/Graph/drug_protein_network_trial.gpickle'
    drug_disease = pd.read_csv(r'data/Cleansed_CTD_chemicals_diseases.csv')

    drug_ranking = drug_scoring(target_disease, known_drugs, model_path, drug_disease, device=device)
    
    print(f"Ranked drugs for {target_disease}: {drug_ranking}")
    
    print_memory_usage()
