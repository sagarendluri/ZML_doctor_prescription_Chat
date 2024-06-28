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

import graphviz
def json_to_dot(graph, parent_node, parent_label):
    if isinstance(parent_node, dict):
        for key, value in parent_node.items():
            if key.startswith("Question"):
                question_id = parent_label.replace(" ", "_") + "_" + key
                label_text = "\n".join(value[i:i+30] for i in range(0, len(value), 30))
                shape = 'diamond' if len(value) > 50 else 'box'
                graph.node(question_id, label_text, shape=shape, style='filled', fillcolor='lightblue')
                graph.edge(parent_label, question_id, color='black')
                json_to_dot(graph, value, question_id)
            elif key in ["Yes", "No"]:
                option_label = parent_label + "_" + key
                graph.node(option_label, key, shape='box', style='filled', fillcolor='lightgreen' if key == "Yes" else 'lightcoral')
                graph.edge(parent_label, option_label, label=key, color='black')
                json_to_dot(graph, value, option_label)
            elif key == "Result":
                result_label = parent_label + "_" + key
                result_str = f"{key}: {value}\nCouncil regulations: {parent_node['Council regulations']}"
                graph.node(result_label, result_str, shape='box', style='filled', fillcolor='lightgrey')
                graph.edge(parent_label, result_label, color='black')

def create_decision_tree_image(decision_tree_json, output_file='decision_tree'):
    # Create a new graph
    dot = graphviz.Digraph(comment='Decision Tree')

    # Add the root node
    dot.node('Root', 'Start', shape='ellipse', style='filled', fillcolor='lightyellow')

    # Build the DOT format
    json_to_dot(dot, decision_tree_json, "Root")

    # Render and save the graph
    dot.format = 'png'
    output_path = dot.render(output_file, view=False)
    return output_path
