

import langchain
import os
from dotenv import load_dotenv
load_dotenv()
from langchain_openai import ChatOpenAI


print({langchain.__version__})

from langchain.agents import create_agent
#from deepagents import create_deep_agent

def get_weather(city:str)-> str:
    """Get the weather for a city."""
    return f"The weather in {city} is sunny."

llm = ChatOpenAI(
    model="Qwen/Qwen2.5-14B-Instruct-AWQ", 
    base_url=os.environ.get("LANGCHAIN_API_BASE_URL"),
    api_key="your-api-key"
)

agent=create_agent(
    model=llm,
    tools=[get_weather],
    system_prompt="You are a helpful assistant."
)

response=agent.invoke({"messages":[{"role":"user","content":"What is the weather like in New York?"}]})

print(response)