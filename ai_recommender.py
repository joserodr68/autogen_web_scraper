
import os
import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv

def dame_quotes(user_input, n, df):
    # Load environment variables from a .env file
    load_dotenv()

    # Get the Groq API key from environment variables
    api_key = os.getenv("GROQ_API_KEY1")

    # Set up the LLM with ChatGroq
    llm = ChatGroq(
        temperature=0,
        api_key=api_key,
        model="llama3-70b-8192"
    )

   

    # Define system and human messages for the prompt
    system = """
    You are an expert linguist and also a marketing expert. You will be provided with a list of quotes in the form of a pandas DataFrame, named df
    Your task is to select and recommend engaging quotes from this list based on the user input which specifies the sentiment and other tags.
    The user will also specify the number of desired quotes.
    The use query may be in Spanish, translate precisely to english first in order to make a better selection.
    select only the relevant quotes, include the author in each quote, and do not explain further, just enumerate the quotes in your response, without any heading.
    Never show the tags in the quote, do not start with "here are some quotes" or "here is a quote "

    """
    human = """
    Here is the DataFrame with quotes:
    {df}

    User input: {user_input}
    Number of quotes desired: {n}
    """

    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

    # Create a query engine
    llm_chain = prompt | llm

    # Prepare the input for the LLM as a dictionary
    user_prompt = {
        "df": df.to_string(index=False),
        "user_input": user_input,
        "n": n
    }

    # Get the response from the LLM
    response = llm_chain.invoke(user_prompt)


    return response.content
