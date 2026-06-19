import os
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool
from app.pipeline.graph.state import AgentState
from app.pipeline.nodes.retriever import retrieve
from app.pipeline.nodes.grader import grade_documents
from app.pipeline.nodes.query_rewriter import rewrite_query
from app.pipeline.nodes.generator import generate_answer

def decide_to_generate(state: AgentState):
    if state.get("requires_rewrite") is True:
        return "rewrite"
    else:
        return "generate"

def get_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("grade_documents", grade_documents)
    workflow.add_node("rewrite_query", rewrite_query)
    workflow.add_node("generate_answer", generate_answer)
    
    workflow.set_entry_point("retrieve")
    
    workflow.add_edge("retrieve", "grade_documents")
    
    workflow.add_conditional_edges(
        "grade_documents",
        decide_to_generate,
        {
            "rewrite": "rewrite_query",
            "generate": "generate_answer"
        }
    )
    
    workflow.add_edge("rewrite_query", "retrieve")
    workflow.add_edge("generate_answer", END)
    
    DB_URI = os.getenv("DATABASE_URL")
    connection_pool = ConnectionPool(conninfo=DB_URI, max_size=10, kwargs={"autocommit": True})
    checkpointer = PostgresSaver(connection_pool)
    checkpointer.setup()
    
    app = workflow.compile(checkpointer=checkpointer)
    return app
