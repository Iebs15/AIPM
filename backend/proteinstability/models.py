# utils.py
import torch
import esm

def get_esm2_embedding(sequence, model, alphabet, batch_converter):
    data = [("protein", sequence)]
    batch_labels, batch_strs, batch_tokens = batch_converter(data)
    with torch.no_grad():
        results = model(batch_tokens, repr_layers=[33], return_contacts=False)
    token_representations = results["representations"][33]
    
    # Average all tokens (excluding special tokens) to get the embedding for the sequence
    sequence_embedding = token_representations[0, 1:len(sequence)+1].mean(0)
    return sequence_embedding.unsqueeze(0)
