"""
CLI script to reset (wipe) the ChromaDB vector store.
Usage: python scripts/reset_vectorstore.py
WARNING: This deletes ALL indexed gazette data.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.retrieval.vectorstore import reset_collection
from loguru import logger

if __name__ == "__main__":
    confirm = input("WARNING: This will delete all indexed gazettes. Type 'yes' to confirm: ")
    if confirm.strip().lower() == "yes":
        reset_collection()
        logger.info("Vector store reset complete.")
    else:
        logger.info("Reset cancelled.")
