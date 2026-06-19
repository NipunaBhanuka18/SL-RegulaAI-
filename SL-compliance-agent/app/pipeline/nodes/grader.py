from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from app.pipeline.graph.state import AgentState
from app.pipeline.prompts import GRADER_PROMPT

class Grade(BaseModel):
    is_relevant: bool = Field(description="True if document is relevant, False otherwise")

def grade_documents(state: AgentState) -> dict:
    question = state["question"]
    documents = state.get("documents", [])

    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    structured_llm = llm.with_structured_output(Grade)

    filtered_docs = []
    
    for doc in documents:
        # Fallback to catch either .content or .page_content depending on the schema
        doc_text = getattr(doc, 'content', getattr(doc, 'page_content', str(doc)))
        
        prompt = f"""You are a strict but logical grader assessing the relevance of a retrieved document to a user's compliance query.

Evaluate the document based on the following rules:
1. BASE GRADING RULE: If the retrieved document contains direct information, lists, or context that explicitly answers the user's compliance question, you MUST grade it as 'yes' (relevant). Do not look for an exact keyword match; look for conceptual relevance.
2. EXHAUSTIVE LIST RULE: If the user asks whether a specific item (like a telephone number or secondary detail) is mandatory or required, and the document provides an official comprehensive list of requirements that completely omits that item, you MUST grade the document as 'yes' (relevant). The document is relevant because an official list's silence on an item explicitly proves it is not legally required.

Return ONLY a valid JSON object with a single key 'is_relevant' and a boolean value (true for 'yes', false for 'no').

Query: {question}
Document Context: {doc_text}"""
        
        result = structured_llm.invoke(prompt)
        
        if result.is_relevant:
            filtered_docs.append(doc)

    requires_rewrite = len(filtered_docs) == 0
    return {"documents": filtered_docs, "requires_rewrite": requires_rewrite}
