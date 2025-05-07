from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_core.tools import tool
import pandas as pd
from llm import load_llm

# Load Dataset
def df_pandas():
    return pd.read_csv("output_file.csv")

# Define Gemini DataFrame Tool
# @tool
# def df_agent_gemini(user_question: str) -> str:
#     """Tool to answer queries about tabular data using Google Gemini."""
#     agent = create_pandas_dataframe_agent(
#         llm=llm,
#         df=df_pandas(),
#         agent_type="zero-shot-react-description",
#         verbose=True,
#         allow_dangerous_code=True
#     )
#     result = agent.run(user_question)
#     return result

# Define OpenAI DataFrame Tool
@tool
def df_agent_openai(user_question: str) -> str:
    """Tool to answer queries about tabular data using OpenAI."""
    agent = create_pandas_dataframe_agent(
        llm=load_llm(),
        df=df_pandas(),
        agent_type="openai-tools",
        verbose=True,
        allow_dangerous_code=True
    )
    result = agent.run(user_question)
    return result












# from langchain_experimental.agents import create_pandas_dataframe_agent
# from langchain_core.tools import tool
# import pandas as pd
# from dotenv import load_dotenv
# import os
# from llm import llm,llm_openai
# load_dotenv()




# #### LOADING DATASET USING PANDAS 
# def df_pandas():
#     df=pd.read_excel("tabular_form.xlsx")
#     return df



# ######### AGENT USING GOOGLE GEMINI
# def df_agent_gemini(user_question):
#     agent = create_pandas_dataframe_agent(
#         llm=llm,
#         df=df_pandas(),
#         agent_type="zero-shot-react-description",
#         verbose=True,
#         allow_dangerous_code=True
#     )
#     result=agent.run(user_question)

#     return result



# ######### AGENT USING OPENAI
# def df_agent_openai(user_question):
#     agent = create_pandas_dataframe_agent(
#         llm=llm_openai,
#         df=df_pandas(),
#         agent_type="openai-tools",
#         verbose=True,
#         allow_dangerous_code=True
#     )
#     result=agent.run(user_question)

#     return result

# @tool
# def df_ans(user_query:str) ->str :
#     """this is create pandas dataframe agent tool that help to generate given query answer from available data saved in similar_data variable
#     similar_data = user_input(user_query)
#     user_query = user_query
#     query_answer is :           
#     return query_answer"""
#     similar_data = df_agent_openai(user_query)
#     return similar_data


