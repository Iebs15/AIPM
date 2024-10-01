import pandas as pd
import torch
import pickle
import networkx as nx
import backend.drugrepurposing.Config as conf

def save_graph(Graph, filename):
    # # Ensure directory exists
    # os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'wb') as f:
        pickle.dump(Graph, f, pickle.HIGHEST_PROTOCOL)
    print(f"Graph saved at {filename}")

def load_graph(filename):
    with open(filename, 'rb') as f:
        G = pickle.load(f)
    print(f"Graph loaded from {filename}.")
    return G


# Functions for the enhanced models (Task 2)

def compute_laplacian_matrix(W):
    """
    Computes the Laplacian matrix L from the weighted adjacency matrix W.
    
    Parameters:
        W: The weighted adjacency matrix.
        
    Returns:
        L: The Laplacian matrix.
    """
    D = torch.diag(W.sum(dim=1))
    L = D - W
    return L

def compute_weight_matrix(graph, sigma=1.0, device='cpu'):
    """
    Computes the weighted adjacency matrix W using a Gaussian similarity function with PyTorch and CUDA.
    
    Parameters:
        graph: A networkx graph object representing the drug network.
        sigma: Parameter controlling the width of the Gaussian function.
        
    Returns:
        weight_matrix: The weighted adjacency matrix W as a torch tensor.
    """
    # Get node vectors and convert them to a PyTorch tensor
    nodes_list = list(graph.nodes())
    node_vectors = torch.tensor([graph.nodes[node]['vector'] for node in nodes_list], device=device)
    
    # Compute pairwise distances using broadcasting
    diff = node_vectors.unsqueeze(1) - node_vectors.unsqueeze(0)
    dist_matrix = torch.sum(diff ** 2, dim=-1)
    
    # Apply Gaussian similarity function
    weight_matrix = torch.exp(-dist_matrix / (2 * sigma**2))
    
    # Set weights to 0 where there are no edges
    adjacency_matrix = torch.tensor(nx.to_numpy_array(graph, nodelist=nodes_list), device=device)
    weight_matrix = weight_matrix * adjacency_matrix
    
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
    W = compute_weight_matrix(graph)
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
    print(f"Checking for disconnected node: {disconnected_node}")
    # found_in_graphs = False

    anchor_set = set()
    for ext_graph in external_graphs:
        if disconnected_node in ext_graph:
            # found_in_graphs = True
            neighbors = set(ext_graph.neighbors(disconnected_node))
            if neighbors not in set(nodes):
                continue
            else:
                anchor_set.update(neighbors)
        # else:
            #print(f"Not found in graph {i}")

    return anchor_set

def validate_set(anchor_set, connected_set):
    """
    Validates the anchor set based on the connected set.
    
    Parameters:
        anchor_set: Set of anchor nodes.
        connected_set: Set of connected nodes.
        
    Returns:
        validation set : using formula connected_set / anchor_set
    """
    connected_set = set(connected_set)  # Ensure connected_set is a set
    return connected_set - anchor_set  # Set difference

def connect_disconnected_nodes(graph, disconnected_nodes, external_graphs, device='cpu'):
    """
    Connects disconnected nodes to the initial network based on f-scores.
    
    Parameters:
        graph: The initial drug network.
        disconnected_nodes: List of nodes that are disconnected in the initial network.
        external_graphs: List of external drug networks.
        epsilon: Performance threshold for accepting new connections.
        device: Device to run the computation ('cpu' or 'cuda').
        
    Returns:
        graph: The complemented drug network.
    """
    for node in disconnected_nodes:
        anchor_set = find_anchor_set(node, external_graphs,nodes=graph.nodes())
        if not anchor_set:
            continue
        
        anchor_indices = torch.tensor([list(graph.nodes()).index(n) for n in anchor_set], device=device)
        f_scores = ssl(graph, anchor_indices, list(graph.nodes()).index(node), device=device)

        sorted_anchors = [anchor_set[i] for i in torch.argsort(f_scores, descending=True)]

        for anchor in sorted_anchors:
            graph.add_edge(node, anchor)
            if not validate_connection(graph, anchor_set, conf.epsilon):
                graph.remove_edge(node, anchor)
                break
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
    # Perform some validation based on the graph properties

    # connected_components = list(nx.connected_components(graph))
    # validate_components = validate_set(anchor_set, connected_components)

    # Check if the new connection has improved the graph by calculating roc auc score on validation set
    # y_true = np.random.randint(0, 2, size= similarity_matrix.size)
    # y_scores = similarity_matrix.flatten()
    # auc_roc = roc_auc_score(y_true, y_scores)


    return True

def semi_supervised_learning(L, y, mu=0.1):
# Compute the f-scores using the SSL formula: f = (I + μL)−1y
    I = torch.eye(L.size(0)).double()
    f_scores = torch.inverse(I + mu * L).matmul(y)
    return f_scores
 
def drug_scoring(disease, known_drug, model_path, drug_disease):
    # Step 3: Load the model (enhanced drug network graph)
    G = load_graph(model_path)
   
    # Step 4: Validate known drugs are present in the graph and create a known drug set
    nodes = G.nodes()
    known_drugs_in_graph = [drug for drug in known_drug if drug in nodes]
 
    # Step 5: Create a set of drugs associated with the target disease from drug_disease dataset
    associated_drugs = drug_disease[drug_disease['DiseaseName'] == disease]['ChemicalID'].tolist()
 
    # Step 6: Create the semi-labeled set of drugs
    semi_labeled_set = list(nodes)

    # Create a mapping from drug names (strings) to unique indices
    drug_to_index = {drug: idx for idx, drug in enumerate(semi_labeled_set)}

    # Convert known_drugs_in_graph and associated_drugs to their corresponding indices
    known_drugs_indices = [drug_to_index[drug] for drug in known_drugs_in_graph]
    associated_drugs_indices = [drug_to_index[drug] for drug in associated_drugs]
    
    # Assuming semi_labeled_set, known_drugs_in_graph, and associated_drugs are all lists or tensors
    labels = torch.zeros(len(semi_labeled_set), dtype=torch.double)

    # Convert indices lists to tensors with the correct dtype (long)
    known_drugs_tensor = torch.tensor(known_drugs_indices, dtype=torch.long)
    associated_drugs_tensor = torch.tensor(associated_drugs_indices, dtype=torch.long)

    # Create boolean masks for known and associated drugs
    is_known_drug = torch.zeros(len(labels), dtype=torch.bool)
    is_associated_drug = torch.zeros(len(labels), dtype=torch.bool)
    
    is_known_drug[known_drugs_tensor] = True
    is_associated_drug[associated_drugs_tensor] = True

    # Apply the masks to the labels tensor
    labels[is_known_drug] = 1
    labels[is_associated_drug] = 0.8
 
    # Step 7: Compute the Laplacian matrix L
    W = compute_weight_matrix(G)
    L = compute_laplacian_matrix(W).double()
 
    # Step 7: Compute f-scores using the SSL function
    f_scores = semi_supervised_learning(L, labels)
 
    # Step 8: Sort the f-scores in descending order and get the corresponding drug names
    drug_scores = {semi_labeled_set[i]: f_scores[i].item() for i in range(len(f_scores))}
    sorted_drugs = sorted(drug_scores.items(), key=lambda item: item[1], reverse=True)
 
    return {drug:score for drug, score in sorted_drugs}

if __name__ == '__main__':

    target_disease = 'Astrocytoma'
    known_drugs = ['C534883', 'C515697', 'C496879']
    model_path = 'results/Graph/drug_protein_network_trial.gpickle'
    drug_disease = pd.read_csv(r'data\Cleansed_CTD_chemicals_diseases.csv')

    drug_ranking = drug_scoring(target_disease, known_drugs, model_path, drug_disease)
    print(f"Ranked drugs for {target_disease}: {drug_ranking}")