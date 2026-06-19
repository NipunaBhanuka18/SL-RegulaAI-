from loguru import logger
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.pipeline.graph.state import AgentState
from app.pipeline.prompts import HALLUCINATION_CHECKER_SYSTEM
from app.core.config import get_settings

HALLUCINATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", HALLUCINATION_CHECKER_SYSTEM),
    ("human", "Source Documents:\n{context}\n\nGenerated Answer:\n{answer}\n\nIs the answer grounded in the sources?"),
])


def hallucination_checker_node(state: AgentState) -> AgentState:
    """
    Node 5: Groundedness checker — verify the draft answer is fully
    supported by retrieved sources. Flags for regeneration if not.
    """
    settings = get_settings()
    llm = ChatGroq(model=settings.groq_model, temperature=0, api_key=settings.groq_api_key)
    chain = HALLUCINATION_PROMPT | llm

    docs = state.get("retrieved_docs", [])
    context = "\n\n".join([content[:600] for content, _, _ in docs])
    draft = state.get("draft_answer", "")

    result = chain.invoke({"context": context, "answer": draft})
    is_hallucination = "hallucination" in result.content.lower()

    logger.info("[GroundednessChecker] Result: {} | detected={}", result.content.strip(), is_hallucination)

    distances = [d for _, _, d in docs] if docs else [1.0]
    avg_distance = sum(distances) / len(distances)
    confidence = "high" if avg_distance < 0.3 else "medium" if avg_distance < 0.6 else "low"

    return {
        **state,
        "hallucination_detected": is_hallucination,
        "final_answer": None if is_hallucination else draft,
        "confidence": None if is_hallucination else confidence,
    }
