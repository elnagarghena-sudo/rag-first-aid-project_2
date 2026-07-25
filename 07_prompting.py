import os
import requests
from importlib import import_module

# Import the retrieval function from 06_retrieve_context.py
retrieve_module = import_module("06_retrieve_context")
retrieve_context = retrieve_module.retrieve_context

# Read the API key from an environment variable (never hardcoded)
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini")

def build_prompt(question, context_chunks):
    context_text = "\n\n".join(context_chunks)
    
    return f"""Answer the question based only on the context below.
If the answer is not in the context, say you don't know.
Always mention which part of the context you used.

Context:
{context_text}

Question: {question}

Answer:"""

def ask_ai(prompt):
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": OPENROUTER_MODEL,
            "messages": [{"role": "user", "content": prompt}]
        }
    )
    result = response.json()
    return result["choices"][0]["message"]["content"]

def answer_question(question):
    context_chunks = retrieve_context(question)
    prompt = build_prompt(question, context_chunks)
    return ask_ai(prompt)

# Test the full pipeline: question -> retrieval -> prompt -> answer
if __name__ == "__main__":
    test_question = "ما هي أعراض الكسر؟"
    print(answer_question(test_question))