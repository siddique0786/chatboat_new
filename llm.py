import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_openai import ChatOpenAI 

load_dotenv()
def load_llm():
    gemini_llm= ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash-exp",
                    temperature=0,
                )

    # openai_llm=ChatOpenAI(model="gpt-4o",temperature=0.0)

    return gemini_llm
