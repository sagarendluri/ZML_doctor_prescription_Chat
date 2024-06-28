from beyondllm import source,retrieve,embeddings,llms,generator
import os
from getpass import getpass
from beyondllm.vectordb import ChromaVectorDb
import json
from graphviz import Digraph
import streamlit as st
from beyondllm.llms import AzureOpenAIModel
from beyondllm.embeddings import AzureAIEmbeddings
import subprocess
import os 
from Scripts.Json_to_tree import create_decision_tree_image
print('current PATH',os.environ['PATH']) 

process=subprocess.Popen(['which dot'], shell=True,
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE)

out, err = process.communicate()
errcode = process.returncode

print(out, err, errcode) 

gv_path=''.join(out.decode().strip().rsplit('/',maxsplit=1)[:-1])

if gv_path:
    os.environ['PATH']=os.environ['PATH']+':'+ gv_path

endpoint_url = st.secrets.azure_embeddings_credentials.ENDPOINT_URL
azure_key = st.secrets.azure_embeddings_credentials.AZURE_KEY
api_version = st.secrets.azure_embeddings_credentials.API_VERSION
deployment_name = st.secrets.azure_embeddings_credentials.DEPLOYMENT_NAME
BASE_URL = st.secrets.azure_embeddings_credentials.BASE_URL
# DEPLOYMENT_NAME = st.secrets.azure_embeddings_credentials.DEPLOYMENT_NAME
API_KEY = st.secrets.azure_embeddings_credentials.API_KEY
st.title("Chat with document")

st.text("Enter API Key")

# api_key = st.text_input("API Key:", type="password")
# os.environ['OPENAI_API_KEY'] = api_key
st.success("API Key entered successfully!")

st.caption("Upload a PDF document to get information from the document.")
uploaded_file = st.file_uploader("Choose a PDF file", type='pdf')
submit=st.button("Get the data")
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
        # vectordb = ChromaVectorDb(collection_name="my_persistent_collection", persist_directory="./db/chroma/")
     
        llm = AzureOpenAIModel(model="gpt4",azure_key = API_KEY,deployment_name="gpt-4-32k" ,endpoint_url=BASE_URL,model_kwargs={"max_tokens":512,"temperature":0.1})
        pipeline = generator.Generate(question=question, system_prompt=system_prompt, retriever=retriever, llm=llm)
        response = pipeline.call()

        
        output_path = create_decision_tree_image(response)
        print(f"Decision tree image saved at: {output_path}")
        
        import streamlit as st
        with st.chat_message(""):
            st.write("")
            st.image('2decision_tree.png', caption='tree from json')
