import os
from typing import List
from langchain_chroma import Chroma
from langchain_core.documents import Document
from app.schemas.document import DocumentChunk

class VectorStoreManager:
    def __init__(self, embedder):
        self.persist_directory = "data/vectorstore/"
        os.makedirs(self.persist_directory, exist_ok=True)
        self.vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=embedder
        )
        
    def add_chunks(self, chunks: List[DocumentChunk]):
        documents = []
        for chunk in chunks:
            doc = Document(
                page_content=chunk.content,
                metadata=chunk.metadata.model_dump()
            )
            documents.append(doc)
        if documents:
            self.vectorstore.add_documents(documents)
            
    def get_retriever(self):
        return self.vectorstore.as_retriever()
