import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize the OpenAI client using environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def llm_chat(messages, model="gpt-3.5-turbo", temperature=0.3):
    """
    Sends a list of messages to the OpenAI chat API and returns the response content.
    Format of `messages`: [{"role": "user", "content": "your prompt"}]
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ LLM chat error: {e}")
        return None

def get_embedding(text, model="text-embedding-ada-002"):
    """
    Returns the embedding vector for a given input text.
    """
    try:
        response = client.embeddings.create(
            input=[text],
            model=model
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"❌ Embedding error: {e}")
        return None

def count_tokens(text, model="gpt-3.5-turbo"):
    """
    Estimates the number of tokens in the text based on simple heuristics.
    For more accuracy, integrate with tiktoken library.
    """
    try:
        # Basic heuristic: 1 token ≈ 4 characters in English
        return int(len(text) / 4)
    except Exception as e:
        print(f"❌ Token counting error: {e}")
        return 0
