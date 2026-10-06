from guardrails import Guard
from guardrails_ai.provenance_llm import ProvenanceLLM

from app.guardrails.provenance import groq_provenance_llm


def create_rag_guard():
    """
    Guardrails validator for SETTribe RAG responses.

    The response should be supported by the retrieved
    SETTribe knowledge-base context.
    """

    provenance_validator = ProvenanceLLM(
        validation_method="full",
        llm_callable=groq_provenance_llm,
        top_k=3,
        on_fail="exception",
    )

    return Guard().use(provenance_validator)