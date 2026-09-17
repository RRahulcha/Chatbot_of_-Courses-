from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory
from app.rag.retriever import get_retriever
from app.rag.prompts import get_rag_prompt
from app.core.llm import get_llm
from app.config import settings
from app.chatbot.memory import get_session_history


def format_docs(docs):
    return "\n\n".join(
        f"Source: {doc.metadata.get('source', 'Unknown')}\n"
        f"{doc.page_content}" 
        for doc in docs
    )

def get_rag_chain():
    retriever = get_retriever()
    prompt = get_rag_prompt()
    llm = get_llm()
    
    # Core RAG Chain
    rag_chain = (
        RunnablePassthrough.assign(
            context=lambda x: format_docs(
                retriever.invoke(x["question"])
            )
        )
        | prompt
        | llm
        | StrOutputParser()
    )
    
    # Wrap with Message History
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
    """
    Convenience function to test the pipeline synchronously with memory.
    """
    if not settings.llm_api_key or settings.llm_api_key == "your_llm_api_key_here":
        documents = get_retriever().invoke(question)
        if not documents:
            return ("I couldn't find that information in the current."
                    "SETTribe knowledge base."
                )
        return ("Based on the approved SETTribe knowledge base:\n\n" 
                + format_docs(documents)
        )

    chain = get_rag_chain()
    return chain.invoke(
        {"question": question, 
         "intent": intent
        },
        config={"configurable": {
            "session_id": session_id}
        }
    )
