
# Function to recursively build the tree graph from the JSON
def json_to_dot(graph, node_id, parent_node, parent_label):
            if isinstance(parent_node, dict):
                for key, value in parent_node.items():
                    if key.startswith("Question"):
                        question_id = f"{node_id}_{key}"
                        label_text = "\n".join(value[i:i+30] for i in range(0, len(value), 30))
                        shape = 'diamond' if len(value) > 50 else 'box'
                        graph.node(question_id, label_text, shape=shape, style='filled', fillcolor='lightblue')
                        graph.edge(parent_label, question_id, color='black')
                        json_to_dot(graph, question_id, value, question_id)
                    elif key in ["Yes", "No"]:
                        option_label = f"{node_id}_{key}"
                        graph.node(option_label, key, shape='box', style='filled', fillcolor='lightgreen' if key == "Yes" else 'lightcoral')
                        graph.edge(parent_label, option_label, label=key, color='black')
                        json_to_dot(graph, option_label, value, option_label)
                    elif key == "Result":
                        result_label = f"{node_id}_{key}"
                        result_str = f"{key}: {value}\nCouncil regulations: {parent_node['Council regulations']}"
                        graph.node(result_label, result_str, shape='box', style='filled', fillcolor='lightgrey')
                        graph.edge(parent_label, result_label, color='black')


def json_to_tree_image(graph, parent_node, parent_label):
            if isinstance(parent_node, dict):
                for key, value in parent_node.items():
                    if key.startswith("Question"):
                        question_id = parent_label.replace(" ", "_") + "_" + key
                        label_text = "\n".join(value[i:i+30] for i in range(0, len(value), 30))
                        node = pydot.Node(question_id, label=label_text, shape='box', style='filled', fillcolor='lightblue')
                        graph.add_node(node)
                        edge = pydot.Edge(parent_label, question_id)
                        graph.add_edge(edge)
                        json_to_tree_image(graph, value, question_id)
                    elif key in ["Yes", "No"]:
                        option_label = parent_label + "_" + key
                        node = pydot.Node(option_label, label=key, shape='box', style='filled', fillcolor='lightgreen' if key == "Yes" else 'lightcoral')
                        graph.add_node(node)
                        edge = pydot.Edge(parent_label, option_label)
                        graph.add_edge(edge)
                        json_to_tree_image(graph, value, option_label)
                    elif key == "Result":
                        result_label = parent_label + "_" + key
                        result_str = f"{key}: {value}\nCouncil regulations: {parent_node['Council regulations']}"
                        node = pydot.Node(result_label, label=result_str, shape='box', style='filled', fillcolor='lightgrey')
                        graph.add_node(node)
                        edge = pydot.Edge(parent_label, result_label)
                        graph.add_edge(edge)

