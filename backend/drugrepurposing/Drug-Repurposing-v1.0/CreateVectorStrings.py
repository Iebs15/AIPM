import pandas as pd
import numpy as np
import backend.drugrepurposing.Config as conf
import zlib
import pickle
import os

def compress_data(data):
    return zlib.compress(pickle.dumps(data))

def process_file(input_csv_path, new_column_names):
    print(f"Processing file: {input_csv_path}")

    # Load data with specified columns, handling errors
    try:
        df = pd.read_csv(input_csv_path, usecols=new_column_names)
    except ValueError as e:
        print(f"Error loading columns for {input_csv_path}: {e}")
        return

    # Check for essential column 'ChemicalID'
    if 'ChemicalID' not in df.columns:
        print(f"Missing essential column 'ChemicalID' in {input_csv_path}. Skipping this file.")
        return

    # Define ID columns to process
    valid_ids = ("GeneID", "DiseaseID", "PathwayID", "GOTermID", "PhenotypeID")
    id_columns = [col for col in df.columns if col in valid_ids]
    # un_list = df[id_columns].unique()
    # print(f"ID columns found: {un_list}")
    if not id_columns:
        print(f"No ID columns found in {input_csv_path}. Skipping this file.")
        return

    # Initialize data structures for interaction counts
    interaction_counts = {}
    unique_ids = {}
    index_maps = {}

    for col in id_columns:
        unique_ids[col] = df[col].unique()
        index_maps[col] = {id_val: idx for idx, id_val in enumerate(unique_ids[col])}
        interaction_counts[col] = {chem_id: np.zeros(len(unique_ids[col]), dtype=int) for chem_id in df['ChemicalID'].unique()}

    # Count interactions
    for _, row in df.iterrows():
        chem_id = row['ChemicalID']
        for col in id_columns:
            if pd.notna(row[col]):
                id_val = row[col]
                if id_val in index_maps[col]:  # Ensure ID value exists in map
                    id_idx = index_maps[col][id_val]
                    interaction_counts[col][chem_id][id_idx] += 1

    # Save output data for each ID column
    for col in id_columns:
        output_data = [{
            'ChemicalID': chem_id,
            'IDs': '|'.join(map(str, unique_ids[col])),
            'vector': compress_data(counts),
            'vector_str': '|'.join(map(str, counts))
        } for chem_id, counts in interaction_counts[col].items()]

        output_df = pd.DataFrame(output_data)
        output_filename = os.path.join(r'results\vector_str_data', os.path.basename(input_csv_path))
        output_df.to_csv(output_filename, index=False)
        print(f"Compressed file for {col} saved as '{output_filename}'.")

# Process files based on configuration
for input_csv_path in conf.path_list:
    new_column_names = {
        conf.chem_protien_csv_path: conf.new_column_names_protien,
        conf.chem_disease_csv_path: conf.new_column_names_disease,
        conf.chem_pathways_csv_path: conf.new_column_names_pathways,
        conf.chem_gene_csv_path: conf.new_column_names_gene,
        conf.chem_pheno_csv_path: conf.new_column_names_Phenoterm
    }.get(input_csv_path, [])

    if new_column_names:
        process_file(input_csv_path, new_column_names)
    else:
        print(f"No column configuration found for {input_csv_path}. Skipping file.")
