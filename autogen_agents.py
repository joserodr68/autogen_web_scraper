
import os
import autogen
from autogen.agentchat.contrib.web_surfer import WebSurferAgent
from groq import Groq
import pandas as pd
from dotenv import load_dotenv





def get_quotes(topic, n_results=10):

    load_dotenv()
    groq_api_key = os.environ.get("GROQ_API_KEY")
    bing_api_key = os.environ.get("BING_API_KEY")

    groq_config_list = [
        {
            "model": "llama3-70b-8192",
            "api_key": groq_api_key,
            "api_type": "groq",
            "frequency_penalty": 0.5,
            "max_tokens": 2048,
            "presence_penalty": 0.2,
            "seed": 42,
            "temperature": 0.5,
            "top_p": 0.2
        }
    ]

    # Configure LLM
    llm_config = {
        "config_list": groq_config_list,
        "cache_seed": 42,  # Seed for caching and reproducibility
    }

   
    summarizer_llm_config = llm_config.copy()


    # Declara los agentes
    web_surfer = WebSurferAgent(
        name="web_surfer",
        llm_config=llm_config,
        browser_config={"viewport_size": 4096, "bing_api_key": bing_api_key},
    )

    quote_manager = autogen.AssistantAgent(
        name="quote_manager",
        llm_config=llm_config,
        system_message="""You are a quote manager responsible for processing and validating quotes from web search results.
        Your tasks include:
        1. Carefully reading through the search results provided by the WebSurferAgent.
        2. Extracting relevant quotes along with their authors.
        3. Validating each quote by ensuring it appears in the provided search results.

        
        
        Provide at least 10 validated quotes if possible. 
        After processing all quotes, respond with TERMINATE."""
    )

    user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=1,
    code_execution_config={"use_docker":False},
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    )

    # Inicia la búsqueda
    user_proxy.initiate_chat(
        web_surfer,
        message=f"Search the web for quotes about '{topic}'. For each quote, provide the full text, the author, and the source URL or brief description of where it was found. Terminate after you find the first set of quotes",
    )
    
    # Extrae los resultados
    web_search_result = user_proxy.last_message().get("content", "").strip()
    

    if not web_search_result:
        print("Error: No results from web search.")
        return []

    print("Web search completed. Results:", web_search_result[:100] + "..." if len(web_search_result) > 100 else web_search_result)
    
    # Generate el mensaje para el procesado de quotes
    process_message = f"""Based on the following web search results, extract and process {n_results} quotes about '{topic}':

    {web_search_result}

    Format each validated quote as follows:
       - Quote: "quote text"
         Author: author name
         Tag: word that is most related to the '{topic}'
         Source: brief description or URL of the source



    After processing all quotes, respond with TERMINATE."""

    print("Starting quote processing...")
    # Use the quote_manager to process the quotes
    user_proxy.initiate_chat(
        quote_manager,
        message=process_message
    )

    # Extract the processed quotes from the chat history
    chat_history = user_proxy.chat_messages[quote_manager]
    if not chat_history:
        print("Error: No response from quote_manager.")
        return []

    processed_quotes = chat_history[-1]['content'].split('\n\n')
    print(f"Quote processing completed. Number of processed quotes: {len(processed_quotes)}")

    return processed_quotes




def parse_quotes(quote_list):
    parsed_quotes = []
    current_quote = {}
    
    for item in quote_list[1:]:  # Skip the first item which is just a description
        if item == 'TERMINATE':
            break
    
        lines = item.split('\n')
        quote_number = lines[0].split('.')[0]
        
        current_quote = {
            'number': int(quote_number),
            'text': lines[0].split('"')[1].strip(),
            'author': lines[1].split('Author:')[1].strip(),
            'tag': lines[2].split('Tag:')[1].strip(),
            'source': lines[3].split('Source:')[1].strip()
        }
        
        parsed_quotes.append(current_quote)
    
    return parsed_quotes

def print_quotes(parsed_quotes):
    for quote in parsed_quotes:
        print(f"Quote: {quote['text']}")
        print(f"Author: {quote['author']}")
        print(f"Tag: {quote['tag']}")
        print(f"Source: {quote['source']}")
        print()  # Empty line for better readability


def create_quotes_dataframe(parsed_quotes):
    # Create DataFrame directly from the list of dictionaries
    df = pd.DataFrame(parsed_quotes)
    
    # Reorder columns if needed
    df = df[['number', 'text', 'author', 'tag', 'source']]
    
    return df

#----- MAIN



