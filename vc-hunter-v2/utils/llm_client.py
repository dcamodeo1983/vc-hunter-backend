import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Global token counters
token_stats = {
    "chat_prompt": 0,
    "chat_completion": 0,
    "embedding": 0
}

def llm_chat(messages, model="gpt-3.5-turbo", temperature=0.3):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        content = response.choices[0].message.content.strip()
        usage = response.usage
        print(f"📊 [llm_chat] Tokens used: prompt={usage.prompt_tokens}, completion={usage.completion_tokens}, total={usage.total_tokens}")

        token_stats["chat_prompt"] += usage.prompt_tokens
        token_stats["chat_completion"] += usage.completion_tokens

        return content
    except Exception as e:
        print(f"❌ LLM chat error: {e}")
        return None

def get_embedding(text, model="text-embedding-ada-002"):
    try:
        response = client.embeddings.create(
            input=[text],
            model=model
        )
        usage = response.usage
        print(f"📊 [get_embedding] Tokens used: {usage.total_tokens}")

        token_stats["embedding"] += usage.total_tokens

        return response.data[0].embedding
    except Exception as e:
        print(f"❌ Embedding error: {e}")
        return None

def count_tokens(text, model="gpt-3.5-turbo"):
    try:
        return int(len(text) / 4)
    except Exception as e:
        print(f"❌ Token counting error: {e}")
        return 0

def get_total_cost_summary():
    chat_prompt = token_stats["chat_prompt"]
    chat_completion = token_stats["chat_completion"]
    embedding = token_stats["embedding"]

    cost_chat = (chat_prompt / 1000) * 0.0015 + (chat_completion / 1000) * 0.002
    cost_embedding = (embedding / 1000) * 0.0001
    total_cost = cost_chat + cost_embedding

    print("\n🧾 Usage Summary")
    print(f"🧠 Chat prompt tokens:     {chat_prompt}")
    print(f"🧠 Chat completion tokens: {chat_completion}")
    print(f"🔗 Embedding tokens:       {embedding}")
    print(f"💵 Estimated total cost:   ${total_cost:.6f}")
    return total_cost
