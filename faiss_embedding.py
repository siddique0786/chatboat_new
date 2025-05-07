from langchain_core.documents import Document
import os
import pandas as pd
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader, TextLoader, UnstructuredWordDocumentLoader, JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import requests
import json
from dotenv import load_dotenv
load_dotenv()
 
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
# Define paths
DATA_PATH = 'data/'
DB_FAISS_PATH = 'faissdb/'
 
def load_excel_files(DATA_PATH):
    """Custom loader for Excel files."""
    documents = []
    for root, _, files in os.walk(DATA_PATH):
        for file in files:
            if file.endswith(".xlsx") or file.endswith(".xls"):
                file_path = os.path.join(root, file)
                # Read the Excel file
                df = pd.read_excel(file_path)
                # Convert each row in the Excel to a document
                for _, row in df.iterrows():
                    documents.append(Document(page_content=row.to_string(), metadata={"source": file_path}))
    return documents
 
 
def get_api_info():
    url = ("https://iserve.cats4u.ai:47102/web/webservices/rest.php?version=1.0&json_data={%20%22operation%22:%20%22core/get%22,%20%22class%22:%20%22Incident%22,%20%22key%22:%20%22SELECT%20Incident%20WHERE%20start_date%20%3E=%272024-06-27%2012:53:14%27%20AND%20start_date%20%3C=%20%272024-11-27%2016:55:00%27%20%22,%20%22output_fields%22:%20%22*%22%20}")
    # response = requests_wrapper.get(base_url)
    auth = (USERNAME, PASSWORD)  
    documents = []
    # Make the POST request
    response = requests.api.get(url, auth=auth)
    
    if not response:
        print("Empty response===============================")
        return "Failed to retrieve the data."
 
    data = response.json()
    with open("api_filter_data.json", 'w') as file:
        file.write(json.dumps(data, indent=4))
    print("status code =============",(response.status_code))
    # print("type=============",(data))
    if isinstance(data, list):
        for item in data:
            documents.append(
                Document(
                    page_content=str(item)
                )
            )
    elif isinstance(data, dict):
        documents.append(
            Document(
                page_content=str(data)
            )
        )
    print(type(documents))
    
    return documents
 
 
 
 
def create_vector_db():
    if not os.path.exists(DATA_PATH):
        print(f"Data path '{DATA_PATH}' does not exist.")
        return
 
    # Define loaders for other file types
    pdf_loader = DirectoryLoader(DATA_PATH, glob='*.pdf', loader_cls=PyPDFLoader)
    txt_loader = DirectoryLoader(DATA_PATH, glob='*.txt', loader_cls=TextLoader)
    docx_loader = DirectoryLoader(DATA_PATH, glob='*.docx', loader_cls=UnstructuredWordDocumentLoader)
 
    # Load documents from each file type
    pdf_documents = pdf_loader.load()
    txt_documents = txt_loader.load()
    docx_documents = docx_loader.load()
    json_documents = get_api_info()
    excel_documents = load_excel_files(DATA_PATH)
    print("=======pdf_documents=========",type(pdf_documents))
    print("=======txt_documents=========",type(txt_documents))
    print("=========docx_documents=======",type(docx_documents))
    print("=======json_documents=========",type(json_documents))
    print("=======excel_documents=========",type(excel_documents))
 
    # Combine all documents
    all_documents = pdf_documents + txt_documents + docx_documents + json_documents + excel_documents
 
    if not all_documents:
        print("No documents found. Ensure there are valid files in the specified directory.")
        return
 
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    texts = text_splitter.split_documents(all_documents)
 
    # #Initialize embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )
 
    # embeddings=OpenAIEmbeddings(
    #     model="text-embedding-3-large"
    # )
    
 
    # Create FAISS vector database
    db = FAISS.from_documents(texts, embeddings)
 
    # Save the database locally
    os.makedirs(os.path.dirname(DB_FAISS_PATH), exist_ok=True)
    db.save_local(DB_FAISS_PATH)
    print(f"Vector database saved at '{DB_FAISS_PATH}'")
 
if __name__ == "__main__":
    create_vector_db()
 
