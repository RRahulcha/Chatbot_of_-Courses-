import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app.rag.chains import answer_question

if __name__ == "__main__":
    question = "What is the fee for the Data Analytics course?"
    print(f"Question: {question}")
    answer = answer_question(question)
    print(f"Answer: {answer}")
