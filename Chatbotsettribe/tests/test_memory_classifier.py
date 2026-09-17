import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app.rag.chains import answer_question
from app.chatbot.classifier import classify_query

if __name__ == "__main__":
    print("--- Testing Classifier ---")
    queries = [
        "What is the fee for Data Analytics?",
        "I need a course recommendation for a b.tech graduate.",
        "Where is SETTribe located?"
    ]
    for q in queries:
        intent = classify_query(q)
        print(f"Query: '{q}' -> Intent: {intent}")
        
    print("\n--- Testing Conversation Memory ---")
    session = "test_user_123"
    
    q1 = "Hi, I am interested in Data Analytics."
    print(f"User: {q1}")
    a1 = answer_question(q1, session)
    print(f"Bot: {a1}\n")
    
    q2 = "What is the fee for it?"
    print(f"User: {q2} (relies on memory)")
    a2 = answer_question(q2, session)
    print(f"Bot: {a2}\n")
