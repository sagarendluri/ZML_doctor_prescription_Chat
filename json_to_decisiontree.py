from beyondllm import source,retrieve,embeddings,llms,generator
import os
from getpass import getpass
from beyondllm.vectordb import ChromaVectorDb
import json
from graphviz import Digraph
import streamlit as st
from beyondllm.llms import AzureOpenAIModel
from beyondllm.embeddings import AzureAIEmbeddings

endpoint_url = st.secrets.azure_embeddings_credentials.ENDPOINT_URL
azure_key = st.secrets.azure_embeddings_credentials.AZURE_KEY
api_version = st.secrets.azure_embeddings_credentials.API_VERSION
deployment_name = st.secrets.azure_embeddings_credentials.DEPLOYMENT_NAME
BASE_URL = st.secrets.azure_embeddings_credentials.BASE_URL
# DEPLOYMENT_NAME = st.secrets.azure_embeddings_credentials.DEPLOYMENT_NAME
API_KEY = st.secrets.azure_embeddings_credentials.API_KEY

os.environ["PATH"] += os.pathsep + "/usr/local/Cellar/graphviz/2.49.3/bin/dot"

def json_to_decision_tree(json_data, graph=None, parent_name=None, node_name=None):
    if graph is None:
        graph = Digraph(format='png')
        graph.attr('node', shape='box')

    if isinstance(json_data, dict):
        for key, value in json_data.items():
            if isinstance(value, dict):
                new_node_name = f'{node_name}_{key}' if node_name else key
                graph.node(new_node_name, key)
                if parent_name:
                    graph.edge(parent_name, new_node_name)
                json_to_decision_tree(value, graph, new_node_name, new_node_name)
            else:
                leaf_node_name = f'{node_name}_{key}' if node_name else key
                graph.node(leaf_node_name, f'{key}: {value}', shape='ellipse')
                if parent_name:
                    graph.edge(parent_name, leaf_node_name)
    return graph


st.title("Chat with document")

st.text("Enter API Key")

# api_key = st.text_input("API Key:", type="password")
# os.environ['OPENAI_API_KEY'] = api_key
st.success("API Key entered successfully!")

st.caption("Upload a PDF document to get information from the document.")
uploaded_file = st.file_uploader("Choose a PDF file", type='pdf')
submit=st.button("Submit")
if submit:

    question = "Give Decision taken in the document"
    system_prompt = '''You are a business analyst with extensive knowledge of legal documents and regulatory documentation. Your expertise is in helping people understand and extract key information from such documents. Your task is to extract the rules and exceptions in a way that enables the creation of a decision tree, facilitating integration into the proper flow.
    Legal Document Context: {context}
    Response Structure:
    Please provide the extracted information in JSON format to help create the decision tree. The JSON should include the following:
    Start with a question.
    Provide possible answers
    For each answer, specify the outcome, including any relevant status and references.
    for option no provide one more question and do the same steps of above

    Additional Instructions:
    Analyze the entire document to identify all relevant rules and exceptions.
    Ensure that the descriptions of rules and exceptions are clear and concise.
    Include relevant dates, jurisdictions, and specific regulations where applicable.
    Structure the questions and answers to facilitate the creation of a logical decision tree or workflow.
    If the regulation mentions specific products, territories, or operations, include them in the appropriate sections.
    Aim to simplify legal language while maintaining accuracy and intent.
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
        # vectordb = ChromaVectorDb(collection_name="my_persistent_collection", persist_directory="./db/chroma/")
     
        llm = AzureOpenAIModel(model="gpt4",azure_key = API_KEY,deployment_name="gpt-4-32k" ,endpoint_url=BASE_URL,model_kwargs={"max_tokens":512,"temperature":0.1})
        pipeline = generator.Generate(question=question, system_prompt=system_prompt, retriever=retriever, llm=llm)
        response = pipeline.call()

        # Convert JSON data to decision tree diagram
        json_tree = json_to_decision_tree(response)
        json_tree.render('decision_tree')

        with open("decision_tree.png", "rb") as file:
            btn = st.download_button(
                    label="Download image",
                    data=file,
                    file_name="decision_tree.png",
                    mime="image/png"
                )
