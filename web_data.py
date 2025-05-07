# from llm import load_llm

# def web_search_tool(query: str) -> str:
#     """
#     Tool to answer the query related to web search simulation.

#     This function simulates a web search by generating responses using the `load_llm().invoke(query)` method.
#     If no response is generated, it returns a default message. Otherwise, it sets a global variable to indicate that a response was found.
#     """
    
#     # Generate a response to the query using the load_llm() (assumed to be defined elsewhere)
#     response = load_llm().invoke(query)
    
#     if not response:
#         return "No information found."
#     else:
#         return response
    
# web_output=web_search_tool("how to do adobe installation")
# print(web_output)


from langchain.agents import AgentExecutor, create_tool_calling_agent, tool
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory, ConversationSummaryBufferMemory
from langchain_openai import ChatOpenAI 
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
# import nltk
# nltk.download('stopwords')
from dotenv import load_dotenv
load_dotenv()

from llm import load_llm
from tool import  web_search_tool,Rag_tool

# Initialize memory for chat history
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)


 
fixed_prompt_old = ChatPromptTemplate.from_messages([
    ("system",
"""
Assistant Role and Goal:

🌐 📞 when recieving user input Call web search tool using the user query given 
    📋 📋Present  solutions clearly

"""),
    ("placeholder", "{chat_history}"),
    ("human", "{query}"),
    ("placeholder", "{agent_scratchpad}"),
])

 

 
# Define tools
tools=[web_search_tool]

# tools = [json_search_tool, Rag_tool, web_search_tool, profile_based_incident_tool_tickets, find_required_service_toolm_tool,profile_based_incident_tool_user ,get_device_list_by_email, create_incident_tool, create_incident_tool_with_ci ,identify_profile_tool, action_get_incident,Update_incident_tool, all_service_family_tool, service_based_on_service_family_tool, retrieve_tool, serviceSubCategory_based_on_Service_id_tool, create_service_request_tool, create_user_request_tool_with_ci, profile_based_incident_tool_agent]


agent = create_tool_calling_agent(load_llm(), tools, fixed_prompt_old)
agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True)
 

print("Pro-Serve Chatbot is ready. Type your query below. Type 'thanks' to exit.")

from fpdf import FPDF

chat_responses=[]

while True:
    query = input("You: ")
    if query.lower() == "thanks":
        break  # Exit loop when user types 'thanks'

    response = agent_executor.invoke({"query": query})['output']
    chat_responses.append(response)  # Store response

    # Clear the PDF and regenerate it with updated chat history
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for res in chat_responses:
        pdf.multi_cell(0, 10, res)
        pdf.ln(5)  # Add space between responses

    pdf.output("data/chat_responses.pdf")
    print("Chat saved to chat_responses.pdf")

# while True:

#     query = input("You: ")
#     email="abhishek.arya@in2ittech.com"
    
#     # Process the query through the agent
#     mssg=f"query:{query} email:{email}"
#     response = agent_executor.invoke({"query": mssg})

#     # Print the response
#     print(f"Pro-Serve Chatbot: {response['output']}")
    