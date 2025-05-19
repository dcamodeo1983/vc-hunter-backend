import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def llm_chat(messages, model="gpt-3.5-turbo", temperature=0.3):
    """
    Sends messages to OpenAI chat model and returns response content.
    Also prints token usage for diagnostics.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        content = response.choices[0].message.content.strip()

        usage = response.usage
        print(f"📊 [llm_chat] Tokens used: prompt={usage.prompt_tokens}, completion={usage.completion_tokens}, total={usage.total_tokens}")

        return content
    except Exception as e:
        print(f"❌ LLM chat error: {e}")
        return None

def get_embedding(text, model="text-embedding-ada-002"):
    """
    Returns embedding vector and prints token count.
    """
    try:
        response = client.embeddings.create(
            input=[text],
            model=model
        )
        print(f"📊 [get_embedding] Tokens used: {response.usage.total_tokens}")
        return response.data[0].embedding
    except Exception as e:
        print(f"❌ Embedding error: {e}")
        return None

def count_tokens(text, model="gpt-3.5-turbo"):
    """
    Quick heuristic token estimator. For actual tracking, see .usage in responses.
    """
    try:
        return int(len(text) / 4)
    except Exception as e:
        print(f"❌ Token counting error: {e}")
        return 0
