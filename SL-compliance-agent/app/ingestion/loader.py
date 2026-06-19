import os
import glob
from langchain_community.document_loaders import PyPDFLoader

def load_all_pdfs(directory: str = "data/gazettes/"):
    documents = []
    pdf_files = glob.glob(os.path.join(directory, "*.pdf"))
    for file_path in pdf_files:
        loader = PyPDFLoader(file_path)
        documents.extend(loader.load())
    return documents
