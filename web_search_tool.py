from langchain_openai import ChatOpenAI 
from langchain.tools import Tool
from dotenv import load_dotenv
load_dotenv()

# Define the function to simulate web search using OpenAI
def openai_search(query: str) -> str:
    """
    Tool to answe the query that is related to the web search 
    """
    llm = ChatOpenAI(temperature=0, model_name="gpt-4o")  
    
    # Generate a response to the query
    response = llm.invoke(query)
    
    if not response:
        return "No information found."
    
    return response

# Create the tool for the agent
web_search_tool = Tool(
    name="OpenAISearch",
    description="Simulate a web search by generating responses using OpenAI's model.",
    func=openai_search
)
