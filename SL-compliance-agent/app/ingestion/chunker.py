import os
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.schemas.document import DocumentChunk, GazetteMetadata

def chunk_documents(documents) -> List[DocumentChunk]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunked_docs = splitter.split_documents(documents)
    
    result = []
    for doc in chunked_docs:
        source_file = doc.metadata.get("source", "Unknown")
        page_num = doc.metadata.get("page", 0)
        
        gazette_number = os.path.basename(source_file)
        
        metadata = GazetteMetadata(
            gazette_number=gazette_number,
            page=page_num,
            category="General"
        )
        
        result.append(DocumentChunk(
            content=doc.page_content,
            metadata=metadata
        ))
        
    return result
