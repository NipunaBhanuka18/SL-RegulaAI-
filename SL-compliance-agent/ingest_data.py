import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres.vectorstores import PGVector

# Load environment variables from .env file
load_dotenv()

# Configuration
DATA_DIRECTORY = "./data/gazettes"
COLLECTION_NAME = "sri_lanka_tax_law"
DB_URL = os.getenv("DATABASE_URL")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def main():
    print("[STARTING BATCH DATA INGESTION]")
    print(f"Scanning target directory: {DATA_DIRECTORY}")

    # 1. Validate Directory and Load PDFs
    if not os.path.exists(DATA_DIRECTORY):
        print(f"Error: The directory '{DATA_DIRECTORY}' does not exist.")
        return

    loader = PyPDFDirectoryLoader(DATA_DIRECTORY)
    raw_documents = loader.load()
    
    if not raw_documents:
        print(f"No PDF documents found inside '{DATA_DIRECTORY}'.")
        return
        
    print(f"Successfully read {len(raw_documents)} raw pages from the directory.")

    # 2. Execute Semantic Text Splitting
    print("Chopping documents into overlapping chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_documents(raw_documents)
    print(f"Created {len(chunks)} distinct text chunks.")

    # 3. Metadata Standardization Pass
    print("Formatting citation metadata fields...")
    for chunk in chunks:
        # Extract the raw source file path (e.g., 'data/gazettes/IRD_VAT_Amendment_2026.pdf')
        raw_source = chunk.metadata.get("source", "")
        if raw_source:
            # Extract just the clean file name without extension for UI rendering
            clean_filename = Path(raw_source).stem
            # Explicitly inject 'gazette' and 'title' keys so the backend logic resolves them instantly
            chunk.metadata["gazette"] = clean_filename
            chunk.metadata["title"] = clean_filename

    # 4. Initialize Vector Embedding Engine
    print(f"Loading embedding model: {EMBEDDING_MODEL}...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    # 5. Establish Vector DB Connection and Stream Records
    print("Streaming vectors to database...")
    try:
        vector_store = PGVector(
            embeddings=embeddings,
            collection_name=COLLECTION_NAME,
            connection=DB_URL,
            use_jsonb=True,
        )
        
        # Batch upload to database
        vector_store.add_documents(chunks)
        print("[INGESTION COMPLETE]")
        print(f"Database collection '{COLLECTION_NAME}' has been successfully synchronized.")
        
    except Exception as e:
        print(f"Critical error during database upload: {str(e)}")

if __name__ == "__main__":
    main()