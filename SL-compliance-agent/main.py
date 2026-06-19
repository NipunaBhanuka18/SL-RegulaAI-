from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import Optional, List
import uuid
import os
import time
from dotenv import load_dotenv
from langgraph.errors import GraphRecursionError
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

# Load API keys
load_dotenv()

# Assuming your graph builder is here
from app.pipeline.graph.builder import get_graph

# 1. Initialize the FastAPI Server
app = FastAPI(
    title="Genary.ai - Tax Compliance API",
    description="Agentic RAG Pipeline for Sri Lankan Corporate Regulations",
    version="1.0.0"
)

# CORS Configuration for Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("API_KEY", "fallback_dev_key")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

def verify_api_key(api_key_ref: str = Security(api_key_header)):
    if api_key_ref != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API Key")
    return api_key_ref

# 2. Initialize the LangGraph Engine
print("Initializing LangGraph Engine...")
app_graph = get_graph()

# --- Strict API Schemas ---
class QueryRequest(BaseModel):
    query: str
    thread_id: Optional[str] = None 

class QueryResponse(BaseModel):
    answer: str
    citations: List[str] = []
    requires_human: bool
    thread_id: str
    path: List[str] = []
    telemetry: Optional[dict] = None

# --- Main API Endpoint ---
@app.post("/api/v1/ask", response_model=QueryResponse)
def ask_agent(request: QueryRequest, api_key: str = Depends(verify_api_key)): 
    try:
        session_id = request.thread_id or str(uuid.uuid4())
        
        # Circuit Breaker
        config = {"configurable": {"thread_id": session_id}, "recursion_limit": 5}
        
        memory_snapshot = app_graph.get_state(config)
        past_state = memory_snapshot.values
        search_query = request.query
        
        # --- PRONOUN / CONTEXT REWRITER ---
        if past_state and "question" in past_state:
            last_question = past_state["question"]
            rewriter_llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
            sys_msg = SystemMessage(content="You are a query rewriter. Given a previous question and a follow-up, rewrite the follow-up into a clear, standalone question that resolves all pronouns and implied context. Output ONLY the standalone question text, nothing else.")
            human_msg = HumanMessage(content=f"Previous: '{last_question}' \nFollow-up: '{request.query}'")
            try:
                response = rewriter_llm.invoke([sys_msg, human_msg])
                search_query = response.content.strip()
                print(f"[QUERY REWRITTEN] {search_query}")
            except Exception as e:
                print(f"[REWRITER FAILED] {e} - Falling back to raw query")
                search_query = request.query
        
        state = {
            "question": search_query,
            "requires_human": False
        }
        
        print(f"\nExecuting Query: {search_query}")
        
        start_time = time.time()
        try:
            result = app_graph.invoke(state, config=config)
            execution_latency = round(time.time() - start_time, 2)
            
        except GraphRecursionError:
            print("[CIRCUIT BREAKER TRIGGERED] Infinite loop detected! Escalating to human.")
            return QueryResponse(
                answer="This is a highly specific scenario. I am escalating this conversation to a human accountant for manual review.",
                citations=[],
                requires_human=True, 
                thread_id=session_id,
                path=["Retrieve", "Grade", "Circuit Breaker", "Escalate"],
                telemetry={"latency": f"{round(time.time() - start_time, 2)}s", "tokens": 0, "model": "llama-3.1-8b-instant", "database": "Neon Postgres", "engine": "LangGraph CRAG"}
            )
        except Exception as e:
            print(f"[UPSTREAM API FAILURE] {e}")
            raise HTTPException(status_code=500, detail="Core engine failure during execution.")

        # 1. Safely extract final answer
        final_answer = "I could not generate an answer."
        if result and isinstance(result, dict):
            generation = result.get("generation")
            if generation:
                if isinstance(generation, dict):
                    final_answer = generation.get("answer") or final_answer
                elif isinstance(generation, str):
                    final_answer = generation
                else:
                    final_answer = getattr(generation, "answer", str(generation))
            
            if final_answer == "I could not generate an answer.":
                final_answer = result.get("answer") or result.get("response") or final_answer

        # 2. Token Estimate
        token_count = len(request.query + str(final_answer)) // 3
        
        # 3. Safely extract Citations
        citations_list = []
        docs = result.get("documents") if isinstance(result, dict) else None
        
        if docs and isinstance(docs, list):
            for doc in docs:
                if doc is None:
                    continue
                
                # Get the metadata object/dict
                metadata = getattr(doc, "metadata", {}) if hasattr(doc, "metadata") else (doc.get("metadata", {}) if isinstance(doc, dict) else {})
                
                # Extract values safely whether metadata is a dict OR a custom object like 'GazetteMetadata'
                gazette_val = metadata.get("gazette") if isinstance(metadata, dict) else getattr(metadata, "gazette", None)
                source_val = metadata.get("source") if isinstance(metadata, dict) else getattr(metadata, "source", None)
                title_val = metadata.get("title") if isinstance(metadata, dict) else getattr(metadata, "title", None)
                page_val = metadata.get("page") if isinstance(metadata, dict) else getattr(metadata, "page", None)
                
                gazette = gazette_val or source_val or title_val or "Sri Lanka Inland Revenue Act"
                
                citation_str = f"Source: {gazette}, Page: {page_val}" if page_val else str(gazette)
                if citation_str not in citations_list:
                    citations_list.append(citation_str)
                    
        # 4. Safely determine Execution Path
        is_rewritten = False
        if isinstance(result, dict):
            is_rewritten = result.get("is_rewritten", False) or (past_state and "question" in past_state)
            
        if result and isinstance(result, dict) and result.get("requires_human"):
            exec_path = ["Retrieve", "Grade", "Escalate"]
        elif is_rewritten:
            exec_path = ["Rewrite", "Retrieve", "Grade", "Generate"]
        else:
            exec_path = ["Retrieve", "Grade", "Generate"]
            
        try:
            latency_str = f"{execution_latency}s"
        except NameError:
            latency_str = "0.0s"

        # 5. Return the clean API response
        return QueryResponse(
            answer=str(final_answer),
            citations=citations_list,
            requires_human=result.get("requires_human", False) if isinstance(result, dict) else False,
            thread_id=session_id,
            path=exec_path,
            telemetry={
                "latency": latency_str,
                "tokens": token_count,
                "model": "llama-3.1-8b-instant",
                "database": "Neon Postgres",
                "engine": "LangGraph CRAG"
            }
        )
        
    except Exception as e:
        print(f"[FATAL ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))