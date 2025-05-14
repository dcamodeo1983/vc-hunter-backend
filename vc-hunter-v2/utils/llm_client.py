import os, json
from dotenv import load_dotenv

load_dotenv()
provider_config = json.load(open("config/model_provider.json"))
provider = provider_config["provider"]
model = provider_config["model"]

if provider == "openai":
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
elif provider == "bedrock":
    import boto3
    from langchain_community.chat_models import BedrockChat
    session = boto3.Session(region_name=os.getenv("AWS_REGION"))
    bedrock = session.client(service_name="bedrock-runtime")
    client = BedrockChat(
        client=bedrock,
        model_id=model,
        model_kwargs={"temperature": 0.2}
    )
else:
    raise ValueError("❌ Unknown provider in config/model_provider.json")

def llm_chat(prompt):
    if provider == "openai":
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    elif provider == "bedrock":
        return client.invoke(prompt).content.strip()

