from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory

from app.rag.retriever import get_retriever
from app.rag.prompts import get_rag_prompt
from app.core.llm import get_llm
from app.config import settings
from app.chatbot.memory import get_session_history


# ---------------------------------------------------------
# TOKEN / CONTEXT SAFETY LIMITS
# ---------------------------------------------------------

# Keep the prompt comfortably below Groq's 8,000 TPM limit.
MAX_CONTEXT_CHARS = 9000
MAX_HISTORY_MESSAGES = 4
MAX_HISTORY_CHARS = 5000
MAX_SEARCH_HISTORY_CHARS = 3000


def format_docs(docs):
    """
    Format retrieved documents while limiting the amount of
    knowledge-base text sent to the LLM.
    """

    parts = []
    total_chars = 0

    for doc in docs:
        content = getattr(doc, "page_content", None)

        if not content:
            continue

        remaining = MAX_CONTEXT_CHARS - total_chars

        if remaining <= 0:
            break

        content = content[:remaining]
        parts.append(content)
        total_chars += len(content)

    return "\n\n".join(parts)


def get_context_for_query(inputs):
    """
    Retrieve relevant website knowledge for the current question.

    Short follow-up questions can use a small amount of recent
    conversation history to improve retrieval.

    Retrieved context is explicitly limited to prevent oversized
    Groq requests.
    """

    question = inputs.get("question", "")
    chat_history = inputs.get("chat_history", [])

    search_query = question

    # Only use a small amount of history for short follow-up questions.
    if chat_history and len(question.split()) <= 6:
        recent_text = []

        for msg in chat_history[-2:]:
            content = getattr(msg, "content", str(msg))

            if content:
                recent_text.append(content)

        history_text = " ".join(recent_text)
        history_text = history_text[:MAX_SEARCH_HISTORY_CHARS]

        if history_text:
            search_query = f"{history_text} {question}"

    try:
        retriever = get_retriever(k=4)
        docs = retriever.invoke(search_query)

    except Exception as exc:
        print(f"WARNING: Retrieval failed: {exc}")
        docs = []

    return format_docs(docs)


def trim_chat_history(inputs):
    """
    Keep only the most recent conversation messages and limit
    their total size before sending them to the LLM.
    """

    history = inputs.get("chat_history", [])

    if not history:
        return inputs

    recent_messages = history[-MAX_HISTORY_MESSAGES:]

    trimmed_messages = []
    total_chars = 0

    # Preserve the most recent messages first.
    for message in reversed(recent_messages):
        content = getattr(message, "content", str(message))

        if not content:
            continue

        remaining = MAX_HISTORY_CHARS - total_chars

        if remaining <= 0:
            break

        content_length = len(content)

        # Normally keep the complete message.
        if content_length <= remaining:
            trimmed_messages.append(message)
            total_chars += content_length

        else:
            # Do not modify the original message object.
            # Stop here if this message is already too large.
            break

    trimmed_messages.reverse()

    return {
        **inputs,
        "chat_history": trimmed_messages,
    }


def get_rag_chain():
    """
    Create the conversational RAG chain with limits on
    conversation history and retrieved context.
    """

    prompt = get_rag_prompt()
    llm = get_llm()

    rag_chain = (
        RunnableLambda(trim_chat_history)
        | RunnablePassthrough.assign(
            context=get_context_for_query
        )
        | prompt
        | llm
        | StrOutputParser()
    )

    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="question",
        history_messages_key="chat_history"
    )

    return conversational_rag_chain


def answer_question(
    question: str,
    session_id: str = "default_session",
    intent: str = "UNKNOWN"
):

    # ---------------------------------------------------------
    # OFFLINE / NO API KEY FALLBACK
    # ---------------------------------------------------------

    if (
        not settings.groq_api_key
        or settings.groq_api_key == "your_groq_api_key_here"
    ):
        history = get_session_history(session_id)

        search_query = question

        if history.messages and len(question.split()) <= 6:
            recent_text = []

            for msg in history.messages[-2:]:
                content = getattr(msg, "content", str(msg))

                if content:
                    recent_text.append(content)

            history_text = " ".join(recent_text)
            history_text = history_text[:MAX_SEARCH_HISTORY_CHARS]

            if history_text:
                search_query = f"{history_text} {question}"

        try:
            retriever = get_retriever(k=4)
            documents = retriever.invoke(search_query)

        except Exception as exc:
            print(
                f"WARNING: Retrieval failed in fallback mode: {exc}"
            )
            documents = []

        if not documents:
            return (
                "I couldn't find that information in the current "
                "SETTribe knowledge base."
            )

        history.add_user_message(question)

        answer = format_docs(documents)

        history.add_ai_message(answer)

        return answer

    # ---------------------------------------------------------
    # GROQ RAG MODE
    # ---------------------------------------------------------

    chain = get_rag_chain()

    return chain.invoke(
        {
            "question": question,
            "intent": intent,
        },
        config={
            "configurable": {
                "session_id": session_id
            }
        },
    )


def should_use_history(question: str) -> bool:
    """
    Decide whether a short question is actually a follow-up
    to the previous conversation.

    Independent questions such as contact, location, fees,
    courses, internships, etc. should retrieve independently.
    """

    q = question.lower().strip()

    independent_keywords = [
        "contact",
        "phone",
        "mobile",
        "number",
        "email",
        "address",
        "location",
        "where",
        "fees",
        "fee",
        "cost",
        "price",
        "courses",
        "course",
        "internship",
        "internships",
        "company",
        "settribe",
        "step",
    ]

    if any(keyword in q for keyword in independent_keywords):
        return False

    follow_up_patterns = [
        "what tools",
        "which tools",
        "what skills",
        "which skills",
        "how long",
        "what projects",
        "which projects",
        "what will i learn",
        "what do i learn",
        "who can join",
        "who can enroll",
        "what about",
        "how does it",
        "is it available",
        "is it online",
        "is it offline",
    ]

    return any(pattern in q for pattern in follow_up_patterns)