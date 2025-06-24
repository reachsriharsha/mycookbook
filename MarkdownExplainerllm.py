import os
from markitdown import MarkItDown
#from langchain_community.llms import Ollama
from langchain_ollama import OllamaLLM
from langchain.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import TextLoader # Using TextLoader for the Markdown string
from langchain_core.documents import Document

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
import time # To measure local time
from datetime import datetime
# --- New: Custom Callback Handler for detailed output ---
class DetailedOutputCallbackHandler(BaseCallbackHandler):
    """
    A custom callback handler to capture and print detailed LLM output,
    including token usage and generation info.
    """
    def __init__(self):
        self.llm_output = None
        self.generation_info = None

    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        """Run when LLM ends running."""
        # Store the raw LLMResult
        self.llm_output = response

        # Extract generation info (which contains token usage for many models)
        # For Ollama, token usage details are often nested in generation_info of the first generation
        if response.generations and response.generations[0]:
            self.generation_info = response.generations[0][0].generation_info
        print("\n--- LLM Call Finished ---")
        # print("Full LLMResult Object:")
        # print(response) # Uncomment this if you want to see the full raw object

        if self.generation_info:
            print("\nGeneration Info (from LLMResult):")
            #for key, value in self.generation_info.items():
            #    print(f"  {key}: {value}")
            print("\n") # Add a newline for readability

# --- Part 1: Convert XLS to Markdown using MarkItDown ---

def convert_xls_to_markdown(xls_file_path: str) -> str:
    """
    Converts an XLS file to Markdown using Microsoft's MarkItDown library.
    """
    if not os.path.exists(xls_file_path):
        raise FileNotFoundError(f"XLS file not found: {xls_file_path}")

    md = MarkItDown()
    print(f"Converting '{xls_file_path}' to Markdown...")
    try:
        result = md.convert(xls_file_path)
        #print(f"Conversion successful. Markdown content:\n{result}\n\n")
        markdown_content = result.text_content.replace('NaN', '')

        with open(f"{xls_file_path}.md", "w") as f:
            f.write(markdown_content)

        print("Conversion successful.")
        return markdown_content
    except Exception as e:
        print(f"Error during MarkItDown conversion: {e}")
        return ""

# --- Part 2: Explain Markdown using LangChain and Ollama (Gemma 3:4b) ---

def explain_markdown_with_ollama(markdown_content: str, explain_file: str):
    """
    Feeds Markdown content to Ollama (Gemma 3:4b) via LangChain to get an explanation.
    """
    if not markdown_content:
        print("No Markdown content to explain.")
        return

    print("\n--- Explaining Markdown with Ollama (Gemma 3:4b) ---")

    # 1. Initialize Ollama LLM
    # Ensure Ollama is running and gemma3:4b is pulled
    try:
        # Initialize the custom callback handler
        callback_handler = DetailedOutputCallbackHandler()
#        llm = OllamaLLM(model="gemma3:4b",base_url="http://localhost:11434",callbacks=[callback_handler])
        llm = OllamaLLM(model="phi4:latest",base_url="http://localhost:11434",callbacks=[callback_handler])
        #llm = OllamaLLM(model="phi4:latest",base_url="http://172.29.136.30:11435",callbacks=[callback_handler])
    except Exception as e:
        print(f"Error initializing Ollama. Make sure Ollama is running and 'gemma3:4b' is pulled. Error: {e}")
        return

    # 2. Create a Document object from the Markdown content
    # TextLoader expects a file, so we wrap the string in a Document object directly.
    # For very large markdown, you might use TextLoader with a temp file or chunks.
    if len(markdown_content) > 75000:
        markdown_content = markdown_content[:75000]
        print("Markdown content was truncated to 20000 characters.")
    doc = Document(page_content=markdown_content, metadata={"source": "excel_to_markdown_conversion"})

    # 3. Define the Prompt Template
    '''
    prompt = ChatPromptTemplate.from_template(
        """You are an intelligent assistant. Your task is to analyze the provided Markdown content,
        which was generated from an Excel file.
        Please describe the structure, main purpose, and key information presented in this Markdown.
        Highlight important contents.
        Focus on providing a clear and concise explanation as if you're helping someone understand the data.

        Make sure explanation should not exceed 300 words.
        Markdown Content:
        {context}

        Explanation:
        """
    )

    '''
    prompt = ChatPromptTemplate.from_template(
        """You are an intelligent assistant. Your task is to analyze and  provide summary of the provided Markdown content,
        which was generated from an Excel file.
        Please describe the structure, main purpose, and key information presented in this Markdown.
        Focus on providing a clear and concise explanation as if you're helping someone understand the data.

        Make sure explanation should not exceed 300 words.
        Markdown Content:
        {context}

        Summary:
        """
    )

    prompt_value = prompt.invoke({"context": [doc]})
    full_prompt_string = prompt_value.to_string() 
    prompt_token_count = llm.get_num_tokens(full_prompt_string)
    print("=" * 80)
    print(f"Total MD length: {len(markdown_content)}")
    print(f"Prompt Token Count: {prompt_token_count}")
    print("=" * 80)


    # 4. Create a Stuff Documents Chain
    # This chain will "stuff" the entire document content into the LLM's context.
    document_chain = create_stuff_documents_chain(llm, prompt)

    # 5. Invoke the chain to get the explanation
    try:
        response = document_chain.invoke({"context": [doc]}) # Pass a list containing the Document object
        #print("\nOllama's Explanation:")
        #print(response)
        with open(explain_file, "w") as f:
            f.write(response)


        answer_token = llm.get_num_tokens(response)
        print("=" * 80              )   
        print(f"Answer Token Count: {answer_token}")
        print("=" * 80)


    except Exception as e:
        print(f"Error invoking Ollama chain: {e}")
        print("Common issues: Ollama server not running, model not downloaded, or context window exceeded.")


# --- Main Execution ---

if __name__ == "__main__":
    # Create a dummy XLS file for demonstration
    # In a real scenario, you would have your own .xls file

    startime = datetime.now()
    try:
        # Save to .xls (requires xlwt, but MarkItDown prefers openpyxl for xlsx)
        # For .xls, pandas might try to use older engines which can be tricky.
        # It's highly recommended to use .xlsx for better compatibility.
        # Let's create an .xlsx file instead, as it's more modern and widely supported by MarkItDown.
        xlsx_file_name = "./data/AI_RFX_Answered_harsha_Technical_SoCs.xlsx"
       

        # Convert the Excel file to Markdown
        markdown_output = convert_xls_to_markdown(xlsx_file_name)

        if markdown_output:
            print("\n--- Generated Markdown Content ---")
            #print(markdown_output)
            #print("----------------------------------")

            # Feed the Markdown content to Ollama for explanation
            explain_markdown_with_ollama(markdown_output,f'{xlsx_file_name}_explain.md')
        else:
            print("Failed to generate Markdown from Excel.")

    except Exception as e:
        print(f"Error: {e}")

        # Example if you have an existing XLS/XLSX:
        # markdown_output = convert_xls_to_markdown("path/to/your/existing_file.xlsx")
        # if markdown_output:
        #     explain_markdown_with_ollama(markdown_output)
    finally:
        # Clean up the dummy files
        endtime = datetime.now()
        print(f"Total time: {endtime - startime}")
        print(f"\nCompleted")