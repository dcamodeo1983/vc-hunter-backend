import os
from dotenv import load_dotenv

load_dotenv()

USE_BEDROCK = os.getenv("USE_BEDROCK", "false").lower() == "true"
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

if USE_BEDROCK:
    from langchain_aws import ChatBedrock
    from langchain_core.messages import HumanMessage
    import boto3

    bedrock_runtime = boto3.client("bedrock-runtime")

    client = ChatBedrock(
        model_id=BEDROCK_MODEL_ID,
        client=bedrock_runtime,
        model_kwargs={"temperature": 0.3},
    )

    def llm_chat(prompt: str) -> str:
        response = client.invoke([HumanMessage(content=prompt)])
        return response.content

else:
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)

    def llm_chat(prompt: str) -> str:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
