import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()

# === OPENAI ===
if LLM_PROVIDER == "openai":
    from openai import OpenAI

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    client = OpenAI(api_key=OPENAI_API_KEY)

    def llm_chat(messages):
        # messages must be a list of dicts: [{"role": "user", "content": "..."}, ...]
        if not isinstance(messages, list) or not all(isinstance(m, dict) for m in messages):
            raise ValueError("`messages` must be a list of {'role', 'content'} dicts for OpenAI")
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()

# === BEDROCK ===
elif LLM_PROVIDER == "bedrock":
    import boto3
    from langchain_aws import ChatBedrock

    BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-east-1")
    BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")

    boto3_client = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)
    client = ChatBedrock(
        model_id=BEDROCK_MODEL_ID,
        client=boto3_client,
        model_kwargs={"temperature": 0.3},
    )

    def llm_chat(messages):
        # Convert list of dicts to Claude-style prompt string
        if isinstance(messages, list):
            prompt = "\n\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in messages])
        else:
            raise ValueError("`messages` must be a list of dicts for Bedrock Claude input")
        
        return client.invoke(prompt).content.strip()

else:
    raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}")
