# utils/llm_client.py

import os
import openai
from dotenv import load_dotenv
import tiktoken

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

# Toggle model here
default_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# Tokenizer for token tracking
def count_tokens(text, model="gpt-3.5-turbo"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def llm_chat(prompt: str, model: str = default_model):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages
        )
        reply = response.choices[0].message.content
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        total_tokens = response.usage.total_tokens
        print(f"📊 [llm_chat] Tokens — Prompt: {prompt_tokens}, Completion: {completion_tokens}, Total: {total_tokens}")
        return reply
    except Exception as e:
        print(f"❌ LLM chat error: {e}")
        raise

def llm_embed(text: str, model: str = "text-embedding-ada-002"):
    try:
        response = openai.Embedding.create(
            model=model,
            input=text
        )
        tokens_used = count_tokens(text, model=model)
        print(f"📊 [llm_embed] Tokens used: {tokens_used}")
        return response.data[0].embedding
    except Exception as e:
        print(f"❌ LLM embedding error: {e}")
        raise

def get_embedding(text, model="text-embedding-ada-002"):
    try:
        response = client.embeddings.create(
            input=[text],
            model=model
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"❌ Embedding error: {e}")
        return None

