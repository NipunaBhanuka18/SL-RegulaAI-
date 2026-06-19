from langchain_groq import ChatGroq
from app.pipeline.graph.state import AgentState

def rewrite_query(state: AgentState):
    question = state["question"]
    
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    
    prompt = (
        "You are an AI assistant that optimizes queries for vector database retrieval.\n"
        "Rewrite the following query to be more specific and keyword-focused.\n"
        f"Query: {question}\n"
        "Return ONLY the rewritten query."
    )
    
    result = llm.invoke(prompt)
    
    return {"question": result.content.strip()}
