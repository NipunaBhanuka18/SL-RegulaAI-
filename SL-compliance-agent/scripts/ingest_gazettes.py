import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ingestion.loader import load_all_pdfs
from app.ingestion.chunker import chunk_documents
from app.ingestion.embedder import get_embedder
from app.retrieval.vectorstore import VectorStoreManager

def main():
    print("Loading PDFs...")
    docs = load_all_pdfs("data/gazettes/")
    print(f"Loaded {len(docs)} pages.")
    
    print("Chunking documents...")
    chunks = chunk_documents(docs)
    print(f"Created {len(chunks)} chunks.")
    
    print("Initializing embedder and vector store...")
    embedder = get_embedder()
    vsm = VectorStoreManager(embedder)
    
    print("Adding chunks to vector store...")
    vsm.add_chunks(chunks)
    print("Ingestion complete.")

if __name__ == "__main__":
    main()
