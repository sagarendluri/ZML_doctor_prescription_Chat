import os
import streamlit as st
from beyondllm import source, retrieve, embeddings, llms, generator
from beyondllm.embeddings import AzureAIEmbeddings
from beyondllm.llms import AzureOpenAIModel
from beyondllm import source
import os
pdf = [ ]
pdf_paths = "/Doctor_prescription_files/"

pdfs = ['Doctor_prescription_files/Prescription_1.pdf', 'Doctor_prescription_files/Prescription_3.pdf', 'Doctor_prescription_files/Prescription_2.pdf']
# dir = os.walk(pdf_paths)
# for root, dir,files  in dir:
#     for file in files:
#         if file.endswith('.pdf'):
#             paths = pdf_paths + file
#             pdf.append(paths)
embed_model = AzureAIEmbeddings(
    endpoint_url="https://marketplace.openai.azure.com/",
    azure_key="d6d9522a01c74836907af2f3fd72ff85",
    api_version="2024-02-01",
    deployment_name="text-embed-marketplace"
)
BASE_URL = "https://gpt-res.openai.azure.com/"
DEPLOYMENT_NAME= "gpt-4-32k" 
API_KEY = "a20bc67dbd7c47ed8c978bbcfdacf930"

# question = "what is the Bobby Jackson condition?"
# def llmmodels(question):
data = source.fit(path=pdfs, dtype="pdf",chunk_size=512,chunk_overlap=20)
# text_embedding = embed_model.embed_text(str(data))
retriever = retrieve.auto_retriever(data,embed_model=embed_model,type="normal",top_k=4)
llm = AzureOpenAIModel(model="gpt4",azure_key = API_KEY,deployment_name="gpt-4-32k" ,endpoint_url=BASE_URL,model_kwargs={"max_tokens":512,"temperature":0.1})



option = st.selectbox( 'Please Select the Patient name?', ('Bobby Jackson', 'Leslie Terry','Danny Smith'))
question = st.text_input("Enter your question")
# question = "what is the Bobby Jackson condition?"
submit=st.button("Get the data")
if submit:
    print(question)
    pipeline = generator.Generate(question=question, retriever=retriever, llm=llm)
    response = pipeline.call()
    st.write(response)
    



