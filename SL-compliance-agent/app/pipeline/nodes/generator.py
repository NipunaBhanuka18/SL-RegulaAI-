from langchain_groq import ChatGroq
from app.pipeline.graph.state import AgentState
from app.pipeline.prompts import GENERATOR_PROMPT
from pydantic import BaseModel, Field
from typing import List

class Citation(BaseModel):
    gazette: str
    page: str

class FinalResponse(BaseModel):
    answer: str
    citations: List[Citation]

def generate_answer(state: AgentState) -> dict:
    question = state["question"]
    documents = state.get("documents", [])

    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    structured_llm = llm.with_structured_output(FinalResponse)

    # Format the documents into a single string with their metadata
    context_parts = []
    for doc in documents:
        doc_text = getattr(doc, 'content', getattr(doc, 'page_content', str(doc)))
        metadata = getattr(doc, 'metadata', None)
        
        # Safe attribute extraction from the Pydantic GazetteMetadata object
        gazette = getattr(metadata, 'gazette_number', "Unknown Gazette")
        page = getattr(metadata, 'page', "Unknown Page")
        
        context_parts.append(f"Content: {doc_text}\nSource: [Gazette: {gazette}, Page: {page}]\n")
    
    context_str = "\n".join(context_parts)

    # The safe string replacement logic
    prompt = GENERATOR_PROMPT.replace("{query}", question).replace("{context}", context_str)
    
    response = structured_llm.invoke(prompt)
    
    return {"generation": response.model_dump()}