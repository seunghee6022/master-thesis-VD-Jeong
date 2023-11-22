import networkx as nx
import matplotlib.pyplot as plt
import json
import numpy as np
import pandas as pd
from collections import OrderedDict
# import pygraphviz as pgv
from networkx.drawing.nx_agraph import graphviz_layout
import pandas as pd
import os


def validate_all_nodes_in_total_cwe_id_list(total_cwe_id_list_dir, node_path_dir):
    cnt =0
    # Sample DataFrame
    total_cwe_id_list_df = pd.read_csv(total_cwe_id_list_dir)
    print(total_cwe_id_list_df.head(3))

    # Sample JSON object
    with open(node_path_dir, 'r') as f:
         node_data = json.load(f)
   
    print(node_data.keys())
    # Check and print values in the DataFrame that are not in the JSON keys
    for value in total_cwe_id_list_df['0']:
        if str(value) not in node_data.keys():
            print(value)
            cnt+=1
    if cnt:
        print(f"Total cnt for cwe id not in hierarchy tree nodes:{cnt}")
    else:
        print("All cwe ids are correctly included in the hierarchy tree nodes!")


def sort_dict(node_levels):
    # Sort dictionary by keys
    sorted_by_key = OrderedDict(sorted(node_levels.items()))

    return sorted_by_key

def set_uid_to_dimension(graph):
    all_uids = nx.topological_sort(graph)
    topo_sorted_uids = list(all_uids)
    uid_to_dimension = {
            uid: dimension for dimension, uid in enumerate(topo_sorted_uids)
        }
    return uid_to_dimension

# def find_hierarchy(paths_dict_data, max_level=None):
#     hierarchy = {}
#     for key, path in paths_dict_data.items():
#         items = path.split('-')
#         if key in items:
#             level = len(items)
#             # If max_level is set, only store nodes with hierarchy level less than or equal to max_level
#             if max_level is None or level <= max_level:
#                 hierarchy[int(key)] = level
#     return hierarchy


def create_graph_from_json(paths_dict_data, max_depth=None):
    
    G = nx.DiGraph()

    def add_path_to_graph(path):
        nodes = list(map(int, path.split('-')))
        if max_depth:
            max_level = min(max_depth, len(nodes) - 1)
            for i in range(max_level):
                G.add_edge(nodes[i], nodes[i+1])
        else:
            for i in range(len(nodes) - 1):
                G.add_edge(nodes[i], nodes[i+1])

    # Add edges from the paths in the JSON data
    for key, paths_list in paths_dict_data.items():
        for path in paths_list:
            add_path_to_graph(path)
            
    return G


def save_tree_graph_png(paths_file, fig_title, file_name, figsize=(20, 10), node_size=2000, font_size=20, width=5):
    with open(paths_file, 'r') as f:
        paths_dict_data = json.load(f)
    
    max_depth = None
    graph = create_graph_from_json(paths_dict_data, max_depth)

    plt.figure(figsize=figsize)
    pos = graphviz_layout(graph, prog='dot')  # Use the Graphviz layout
    # print("pos\n",pos)
    # pos = {node: (x * scale_factor_x, y * scale_factor_y) for node, (x, y) in pos.items()}
    # print("pos\n",pos)
    # nx.draw(graph, pos=pos, with_labels=True, node_size=700, node_color="skyblue",font_size=10, width=2)
    nx.draw(graph, pos=pos, with_labels=True, node_size=node_size, node_color="skyblue",font_size=font_size, width=width)
    # Set the title for the figure
    # plt.title("Directed Acyclic Graph for CWE Hierarchy after CWE Reassignment")
    # plt.title("Directed Acyclic Graph for Original CWE Hierarchy")
    plt.title(fig_title)
    # Save the plot as an image (e.g., PNG, JPEG, PDF)
    # plt.savefig("figures/original_DAG.png")
    plt.savefig(f"figures/{file_name}.png")
   

    plt.show()



if __name__ == "__main__":
    print(os.getcwd())
    # total_cwe_id_list_dir='data_preprocessing/preprocessed_datasets/total_cwe_id_list.csv'
    # node_path_dir='datasets_/graph_all_paths.json'
    # validate_all_nodes_in_total_cwe_id_list(total_cwe_id_list_dir, node_path_dir)
    # Create graph from JSON
    # paths_file = 'data_preprocessing/preprocessed_datasets/debug_datasets/graph_original_paths.json'
    # paths_file = 'data_preprocessing/preprocessed_datasets/debug_datasets/graph_all_paths.json'
    paths_file = 'data_preprocessing/preprocessed_datasets/debug_datasets/graph_assignedcwe_paths.json'
    fig_title = "Directed Acyclic Graph for CWE Hierarchy after CWE Reassignment"
    file_name = "reassigned_cwe_DAG"
    save_tree_graph_png(paths_file=paths_file, fig_title=fig_title, file_name=file_name, figsize=(20, 10), node_size=2000, font_size=20, width=5)

    paths_file = 'data_preprocessing/preprocessed_datasets/debug_datasets/graph_assignedcwe_paths_new.json'
    fig_title = "Directed Acyclic Graph for CWE Hierarchy after CWE Reassignment"
    file_name = "reassigned_cwe_DAG_new"
    save_tree_graph_png(paths_file=paths_file, fig_title=fig_title, file_name=file_name, figsize=(20, 10), node_size=2000, font_size=20, width=5)

    paths_file = 'data_preprocessing/preprocessed_datasets/debug_datasets/graph_original_paths.json'
    fig_title = "Directed Acyclic Graph for Original CWE Hierarchy (w/o Artificial Root)"
    file_name = "original_DAG_"
    save_tree_graph_png(paths_file=paths_file, fig_title=fig_title, file_name=file_name, figsize=(30, 10), node_size=700, font_size=10, width=2)
    
    paths_file = 'data_preprocessing/preprocessed_datasets/debug_datasets/graph_all_paths.json'
    fig_title = "Directed Acyclic Graph for CWE Hierarchy (w Artificial Root)"
    file_name = "DAG_"
    save_tree_graph_png(paths_file=paths_file, fig_title=fig_title, file_name=file_name, figsize=(30, 10), node_size=700, font_size=10, width=2)

#     # Example of using the classifier
#     input_dim = 10
#     embedding_dim = 5 #232 num of total nodes (not target nodes)

#     uid_to_dimension = set_uid_to_dimension(G)
#     print("uid_to_dimension",len(uid_to_dimension), uid_to_dimension)

#     prediction_target_uids = [int(key) for key in paths_dict_data.keys()]
#     print("prediction_target_uids",len(prediction_target_uids), prediction_target_uids)

#     # feature_batch = []
#     # ground_truth = []
#     # loss = classifier.loss(feature_batch, ground_truth)


    