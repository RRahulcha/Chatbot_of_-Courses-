import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv(".env")

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Explain the importance of fast language models",
        }
    ],
    model="meta-llama/llama-prompt-guard-2-86m",
)

print(chat_completion.choices[0].message.content)