import re
from guardrails import Guard
from guardrails_ai.provenance_llm import ProvenanceLLM
from app.guardrails.provenance import groq_provenance_llm

MAX_QUESTION_LENGTH = 1000


def validate_input(question: str) -> tuple[bool, str]:
    """
    Validate and sanitize user input before sending it
    to the RAG/LLM pipeline.
    """

    if not question:
        return False, "Please enter a question."

    question = question.strip()

    if not question:
        return False, "Please enter a question."

    if len(question) > MAX_QUESTION_LENGTH:
        return (
            False,
            "Your question is too long. Please ask a shorter question."
        )

    # Basic prompt-injection protection.
    suspicious_patterns = [
        r"ignore previous instructions",
        r"ignore all previous instructions",
        r"ignore the system prompt",
        r"reveal your system prompt",
        r"show me your system prompt",
        r"reveal your instructions",
        r"show your hidden instructions",
    ]

    for pattern in suspicious_patterns:
        if re.search(pattern, question, re.IGNORECASE):
            return (
                False,
                "I can help with SETTribe courses, internships, "
                "careers and related information."
            )

    return True, question

def validate_output(answer: str) -> str:
    """
    Basic output guardrail.

    Prevent obviously unsafe or unsupported claims from
    being returned directly to the user.
    """

    if not answer:
        return (
            "I couldn't find enough information to answer that "
            "from the current SETTribe knowledge base."
        )

    answer = answer.strip()

    # Prevent accidental job-guarantee claims.
    guarantee_patterns = [
        r"guaranteed job",
        r"job guarantee",
        r"100% job",
        r"guaranteed placement",
        r"100% placement",
        r"write the code"
    ]

    for pattern in guarantee_patterns:
        if re.search(pattern, answer, re.IGNORECASE):
            return (
                "I don't have verified information confirming a job "
                "or placement guarantee. Please contact SETTribe "
                "for the latest official information."
            )

    return answer


# ---------------------------------------------------------
# GUARDRAILS AI - PROVENANCE VALIDATOR
# ---------------------------------------------------------

provenance_validator = ProvenanceLLM(
    validation_method="full",
    llm_callable=groq_provenance_llm,
    top_k=3,
    on_fail="noop",
)

provenance_guard = Guard().use(provenance_validator)


def validate_provenance(answer: str, sources: list[str]) -> str:
    """
    Validate whether the generated answer is supported by
    retrieved SETTribe RAG sources.

    If provenance validation cannot be performed, return the
    original answer instead of breaking the chatbot.
    """

    if not answer or not answer.strip():
        return validate_output(answer)

    if not sources:
        return validate_output(answer)

    try:
        result = provenance_guard.validate(
            answer,
            metadata={
                "sources": sources,
                "pass_on_invalid": True,
            },
        )

        validated_answer = getattr(result, "validated_output", None)

        if validated_answer:
            return validate_output(str(validated_answer))

        return validate_output(answer)

    except Exception as exc:
        print(f"WARNING: Provenance validation failed: {exc}")

        # Do not make the entire chatbot unavailable if
        # the optional provenance validator fails.
        return validate_output(answer)