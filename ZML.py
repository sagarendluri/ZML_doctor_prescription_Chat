import os
import streamlit as st
from beyondllm import source, retrieve, embeddings, llms, generator
from beyondllm.embeddings import AzureAIEmbeddings
from beyondllm.llms import AzureOpenAIModel
from beyondllm import source
import base64
import os
pdf = [ ]
pdf_paths = "/Doctor_prescription_files/"

pdfs = ['Doctor_prescription_files/Prescription_1.pdf']#, 'Doctor_prescription_files/Prescription_3.pdf', 'Doctor_prescription_files/Prescription_2.pdf']
# dir = os.walk(pdf_paths)
# for root, dir,files  in dir:
#     for file in files:
#         if file.endswith('.pdf'):
#             paths = pdf_paths + file
#             pdf.append(paths)


# DEPLOYMENT_NAME= os.environ['DEPLOYMENT_NAME']
# auth_header_encoded = base64.b64decode(f"{DEPLOYMENT_NAME}".encode("ascii"))
# auth_header = f"Basic{auth_header_encoded.decode('ascii')}"
deployment_name = os.getenv("DEPLOYMENT_NAME")
print(f"deployment_key:{deployment_name}")

