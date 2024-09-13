import os

#directory containing all the CSV files
data_directory = r"data"

#function to get the path of all the CSV files dynamically
def get_file_path(file_name):
    return os.path.join(data_directory, file_name)

# Paths to the CSV files
chem_protien_csv_path = get_file_path(r"Cleansed_CTD_chem_gene_ixns.csv")
chem_disease_csv_path = get_file_path(r"Cleansed_CTD_chemicals_diseases.csv")
chem_pathways_csv_path = get_file_path(r"Cleansed_CTD_chem_pathways_enriched.csv")
chem_gene_csv_path = get_file_path(r"Cleansed_CTD_chem_go_enriched.csv")
chem_pheno_csv_path = get_file_path(r"Cleansed_CTD_pheno_term_ixns.csv")

# Storing paths in a list
path_list = [
    chem_protien_csv_path,
    chem_disease_csv_path,
    chem_pathways_csv_path,
    chem_gene_csv_path,
    chem_pheno_csv_path
]

# print(path_list[0])
# Define the new column names
# For Chem_genes
new_column_names_protien = [
    "ChemicalName", "ChemicalID", "GeneSymbol", "GeneID", "GeneForms",
    "Organism", "OrganismID", "Interaction", "InteractionActions"
]

# For Chem_diseases
new_column_names_disease = [
    "ChemicalName", "ChemicalID", "DiseaseName", "DiseaseID", "DirectEvidence",
    "InferenceGeneSymbol", "InferenceScore"
]

# For Chem_pathways
new_column_names_pathways = [
    "ChemicalName", "ChemicalID", "PathwayName", "PathwayID",
    "PValue", "CorrectedPValue", "TargetMatchQty", "TargetTotalQty",
    "BackgroundMatchQty", "BackgroundTotalQty"
]

# For Chem_go
new_column_names_gene = [
    "ChemicalName", "ChemicalID", "Ontology", "GOTermName",
    "GOTermID", "HighestGOLevel", "PValue", "CorrectedPValue",
    "TargetMatchQty", "TargetTotalQty", "BackgroundMatchQty", "BackgroundTotalQty"
]

# For Phenoterm
new_column_names_Phenoterm = [
    "ChemicalName", "ChemicalID", "PhenotypeName", "PhenotypeID", "CoMentionedTerms", "Organism",
    "OrganismID","Interaction","InteractionActionsAnatomyTerms","InferenceGeneSymbols"
]

# To Store result
graph_result = r"results\Graph"

# checking the similarity matrix for edges in the graphS
threshold = 0.33

protein_threshold = 0.05 # for drug-protien
GO_threshold = 0.1 # for drug-gene
pathway_threshold = 0.4 # for drug-pathway
disease_threshold = 0.23 # for drug-disease
phenotype_threshold = 0.98 # for drug-phenotype
epsilon = 1e-9