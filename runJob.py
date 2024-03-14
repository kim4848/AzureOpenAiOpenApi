
import requests
import json
from openai import AzureOpenAI
import urllib.parse
from Utils.swaggerHelper import GetFunctions
from interfaces import Tool
import os

client=AzureOpenAI(
    api_key= os.getenv('AZURE_OPEN_API_KEY'),        
    azure_endpoint="https://kjopenaitestse.openai.azure.com/", 
    api_version="2023-07-01-preview"
)

SWAGGER_URL = 'http://localhost:5116/swagger/v1/swagger.json'
DATA_BASEURL='http://localhost:5116'
SYSTEM_MESSAGE = """
You are a helpful assistant.
"""

def get_openai_response(functions:list[Tool], messages):    
    
    return client.chat.completions.create(
        model="test",        
        tools= functions,
        tool_choice="auto",  # "auto" means the model can pick between generating a message or calling a function.
        temperature=0,
        messages=messages,
    )

def fetch_data_from_api(endpoint):
    url = DATA_BASEURL+endpoint    
    response = requests.get(url)
    if response.status_code == 200:
        d= response.json()        
        return json.dumps(d)
    else:
        print(f"Failed to fetch content from URL. Status code: {response.status_code}")

def process_user_instruction(functions, instruction):
    messages = [
        {"content": SYSTEM_MESSAGE, "role": "system"},
        {"content": instruction, "role": "user"},
    ]

    response = get_openai_response(functions, messages)
    message = response.choices[0].message
    
    try:
        messages.append(message)
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls            
        if tool_calls:
            for tool_call in tool_calls:    
                print(f"Tool call: {tool_call.function.arguments}")                
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                #Get item from functions list
                filteredFunctions = [f for f in functions if f["function"]["name"]==function_name]
                if filteredFunctions:
                    functionDefinition=filteredFunctions[0]
                    print(f"Function: {functionDefinition}")
                    #get args from function_args
                    function_args = json.loads(tool_call.function.arguments)
                    query_string = urllib.parse.urlencode(function_args)
                    data=fetch_data_from_api(functionDefinition["function"]["endpoint"] +"?"+query_string)                    
                    messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": data,
                        }
                    )  
            response = get_openai_response(functions, messages)
        message = response.choices[0].message
        print(f"Message: {message.content}")                
    except Exception as e:
        print(f"Failed to process message: {e}")
        print("\n>> Message:\n")
        print(message.content)


if __name__ == "__main__":    
    print("-----------------")   
    functions=GetFunctions(SWAGGER_URL)

    if functions:        
        USER_INSTRUCTION = """
        Instruction:         
        Get the weather forecast for the date 2024-03-15        
        """

        process_user_instruction(functions, USER_INSTRUCTION)
    else:
        print("Failed to read Swagger file.")
    
   