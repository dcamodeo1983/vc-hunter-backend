import os
from dotenv import load_dotenv
from langchain_aws import ChatBedrock
import boto3

load_dotenv()
use_bedrock = os.getenv("USE_BEDROCK", "false").lower() == "true"
model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")

if use_bedrock:
    client = ChatBedrock(
        model_id=model_id,
        region_name="us-east-1",  # or your actual AWS region
        credentials_profile_name=None  # optional: your AWS CLI profile
    )
else:
    from openai import OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=openai_key)

def llm_chat(prompt: str):
    if use_bedrock:
        return client.invoke(prompt)
    else:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
