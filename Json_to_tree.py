import json
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_pydot import graphviz_layout
# Function to recursively build the tree graph from the JSON
def json_to_tree(data, parent=None, graph=None):
    if graph is None:
        graph = nx.DiGraph()

    if isinstance(data, dict):
        for key, value in data.items():
            node_id = f"{parent}/{key}" if parent else key
            graph.add_node(node_id, label=key)
            if parent:
                graph.add_edge(parent, node_id)
            if isinstance(value, (dict, list)):
                json_to_tree(value, node_id, graph)
            else:
                child_id = f"{node_id}/{value}"
                graph.add_node(child_id, label=value)
                graph.add_edge(node_id, child_id)
    elif isinstance(data, list):
        for index, item in enumerate(data):
            node_id = f"{parent}/{index}" if parent else str(index)
            graph.add_node(node_id, label=f"{parent.split('/')[-1]}_{index}" if parent else str(index))
            graph.add_edge(parent, node_id)
            json_to_tree(item, node_id, graph)
    else:
        node_id = f"{parent}/{data}" if parent else str(data)
        graph.add_node(node_id, label=data)
        if parent:
            graph.add_edge(parent, node_id)

    return graph

# Function to plot the tree graph
def plot_tree(graph, output_file='tree.png'):
    pos = graphviz_layout(graph, prog='dot')
    labels = nx.get_node_attributes(graph, 'label')
    plt.figure(figsize=(12, 8))
    nx.draw(graph, pos, labels=labels, with_labels=True, arrows=False, node_size=2000, node_color='lightblue', font_size=10, font_weight='bold')
    plt.savefig(output_file, format='png')
    plt.show()

