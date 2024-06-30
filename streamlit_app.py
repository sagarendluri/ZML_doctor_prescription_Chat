import os
import json
import pydot
import subprocess
import streamlit as st
from getpass import getpass
from beyondllm.llms import AzureOpenAIModel
from beyondllm.embeddings import AzureAIEmbeddings
from beyondllm import source,retrieve,embeddings,llms,generator
# Script of json to tree using pydot module
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
endpoint_url = st.secrets.azure_embeddings_credentials.ENDPOINT_URL
azure_key = st.secrets.azure_embeddings_credentials.AZURE_KEY
api_version = st.secrets.azure_embeddings_credentials.API_VERSION
deployment_name = st.secrets.azure_embeddings_credentials.DEPLOYMENT_NAME
BASE_URL = st.secrets.azure_embeddings_credentials.BASE_URL
# DEPLOYMENT_NAME = st.secrets.azure_embeddings_credentials.DEPLOYMENT_NAME
API_KEY = st.secrets.azure_embeddings_credentials.API_KEY
st.title("Respectus decision tree generator")


# api_key = st.text_input("API Key:", type="password")
# os.environ['OPENAI_API_KEY'] = api_key


uploaded_file = st.file_uploader("Choose a PDF file", type='pdf')
submit=st.button("Generate results")
if submit:

    question = "Give Decision taken in the document"
    system_prompt = '''You are a business analyst with extensive knowledge of legal documents and regulatory documentation.
    Your expertise is in helping people understand and extract key information from such documents. 
    Your task is to extract the rules and exceptions in a way that enables the creation of a decision tree, facilitating integration into the proper flow.
    Legal Document Context: {context}
    Response Structure:
    Create a decision tree in JSON format based on the following structure:

    Write a question and question should be two response like yes or no. if yes it has fallowing answers or other question 
        - If Yes, the result should be: "Not restricted" additional -Council regulations: provide dates and articles if possible.
        - If No, proceed to the next question2.( by giving some link to the next question not direct to next question)

    2. Next question based on the previous question outcome.
        - If Yes, the result should be: "Not restricted" additional -Council regulations: provide dates and articles if possible.
        - If No, proceed to the next question.
    In simple terms - flow chat if conditons.
    [Continue this structure for as many questions as needed, ensuring each question branches into Yes/No answers and provides appropriate results based on the Council regulations.]
    Please continue this format for as many questions as needed, ensuring each question follows the same structure.
    Output is the JSON response follow this pattern: Do not change everytime Json output

    This is JSON output Example, add more questions in this formate only. 
    {
        "Question1": ,
        "Yes": {
            "Result": ,
            "Council regulations": 
        },
        "No": {
            "Question2": ,
            "Yes": {
                "Result":,
                "Council regulations": 
            },
            "No": {
                "Question3": ,
                "Yes": {
                    "Result": ,
                    "Council regulations":
                },
                "No": {
                    "Result": ,
                    "Council regulations": 
                }
            }
        }
    }
    Additional Instructions:
    
    Analyze the entire document to identify all relevant rules and exceptions.
    Ensure that the descriptions of rules and exceptions are clear and concise.
    Include relevant dates, jurisdictions, and specific regulations where applicable.
    Structure the questions and answers to facilitate the creation of a logical decision tree or workflow.
    If the regulation mentions specific products, territories, or operations, include them in the appropriate sections.
    Aim to simplify legal language while maintaining accuracy and intent.
    [Provide your answer in JSON form. Reply with only the answer in JSON form and include no other commentary]:
    Provide your answer in JSON form. Reply with only the answer in JSON form and include no other commentary
    Return Valid Json to create Tree 
    '''


    if uploaded_file is not None and question:
        save_path = "./uploaded_files"
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        file_path = os.path.join(save_path, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
      
        data = source.fit(file_path, dtype="pdf", chunk_size=1024, chunk_overlap=0)
        embed_model = AzureAIEmbeddings(
              endpoint_url = endpoint_url,
              azure_key = azure_key,
              api_version= api_version,
              deployment_name=deployment_name
          )

        retriever = retrieve.auto_retriever(data, embed_model, type="normal", top_k=4)
        llm = AzureOpenAIModel(model="gpt4",azure_key = API_KEY,deployment_name="gpt-4-32k" ,endpoint_url=BASE_URL,model_kwargs={"max_tokens":512,"temperature":0.1})
        pipeline = generator.Generate(question=question, system_prompt=system_prompt, retriever=retriever, llm=llm)
        decision_tree_json = pipeline.call()
        response = json.loads(decision_tree_json)
        # Function to recursively create nodes and edges in the grap
        # Create a new graph
        # Create a new directed graph

        
        graph = pydot.Dot(graph_type='digraph')
        
        # Add the root node
        root_node = pydot.Node('Root', label='Start', shape='ellipse', style='filled', fillcolor='lightyellow')
        graph.add_node(root_node)
        
        # Build the graph from the JSON structure
        json_to_tree_image(graph, response, "Root")
        
        # Save the graph as a PNG image
        graph.write_png(uploaded_file.name+'_tree.png')
        
        # # Display the graph
        # from PIL import Image
        # img = Image.open(uploaded_file.name+'_tree.png')
        # img.show()

        with open("uploaded_file.name+'_tree.png'", "rb") as file:
            btn = st.download_button(
                    label="Download image",
                    data=file,
                    file_name="uploaded_file.name+'_tree.png'",
                    mime="image/png"
                  )
        with st.chat_message(""):
            st.write("")
            st.image(uploaded_file.name+'_tree.png', caption="tree_from_json")
