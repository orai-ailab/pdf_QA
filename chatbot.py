from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Tuple
from openai import OpenAI
from utils import query_pdfs, get_distinct_field
import json
from bot_utils.functions import *
from bot_utils.prompts import *
from config import settings
from bot_utils.utils import *
import uuid

app = FastAPI(title="Chat Inference API", version="1.0.0")

# class Question(BaseModel):
#     text: str

# class ChatMessage(BaseModel):
#     role: str
#     content: str
#     tool_call_id: Optional[str] = None
#     name: Optional[str] = None

# class ChatResponse(BaseModel):
#     response: str
    
class ChatRequest(BaseModel):
    message: str
    history: List[Tuple[str,str]]

class FormatResponse(BaseModel):
    response: str
    link: str


def infer_chat(messages: List[dict], tools: List[dict]) -> str:
    model = settings.LLM_INFERENCE_MODEL
    client = OpenAI(
        api_key=settings.TOGETHER_API_KEY,
        base_url='https://api.together.xyz/v1',
    )
    print('MESSAGES SENT: ',messages)
    try:
        chat_response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        tool_calls = chat_response.choices[0].message.tool_calls
        tool_response = chat_response.choices[0].message.content
        print('TOOL_CALLS: ',tool_calls)
        print('TOOL_RESPONSE: ', tool_response)
        if tool_calls or "<function" in tool_response:
            # print('TOOL_CALLS: ', tool_calls)
            if tool_calls:
                try:
                    for tool_call in tool_calls:
                        function_name = tool_call.function.name
                        print('FUNCTION NAME: ',function_name)
                        function_args = json.loads(tool_call.function.arguments)
                        print('FUNCTION ARGS: ',function_args)
                        function_response = get_function_response(function_name, function_args)
                        print('FUNCTION_RESPONSE: ',function_response) 
                        messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": function_response
                        })
                        
                    function_enriched_response = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        # response_format=FormatResponse,
                    )
                except Exception as e:
                    print(f"ERROR WHILE DOING TOOL CALL: {e}")
                response =  (function_enriched_response.choices[0].message.content)
                return clean_and_parse_json(response)
                # print(function_enriched_response.choices[0].message.parsed)
                # return function_enriched_response.choices[0].message.parsed
            else:
                try:
                    tool_parse = parse_function_call(tool_response)
                    function_name = tool_parse["function_name"]
                    function_args = tool_parse["function_args"]
                    function_response = get_function_response(function_name, function_args)
                    print('\nFUNCTION NAME: ',function_name)
                    print('\nFUNCTION ARGS: ',function_args)
                    print('\nFUNCTION_RESPONSE: ',function_response) 
                    messages.append({
                        "tool_call_id": str(uuid.uuid4())[:8],
                        "role": "tool",
                        "name": function_name,
                        "content": function_response
                    })

                    function_enriched_response = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        # response_format=FormatResponse,
                    )
                    
                    response = function_enriched_response.choices[0].message.content
                    return clean_and_parse_json(response)
                except Exception as e:
                    print('ERROR WHILE PARSING FUNCTION CALL: ', e)
        else:
            print('******************NO TOOL CALLED******************')
            # print('\nNO TOOL CALLED')   
            print('\nMESSAGE: \n',messages)  
            print('****************************************')
            response = chat_response.choices[0].message.content
            print('RETURN RESPONSE: ',response)
            
            return clean_and_parse_json(response)
        
    except Exception as e:
        print("ERROR : ",e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask_question(chat_request: ChatRequest):
    # print("RECEIVED REQUEST: ", chat_request)
    new_message = chat_request.message
    
    chat_history = chat_request.history
    
    print('\nRECEIVED NEW MESSAGE: ', new_message)
    print('\nRECEIVED HISTORY: ',chat_history)
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]
    
    for (mess,resp) in chat_history[-5:]:
        messages.extend(
            [
                {
                    "role":"user",
                    "content":mess
                },
                {
                    "role":"assistant",
                    "content":resp
                }
            ]
        )
    messages.append((
        {
            "role":"user",
            "content": new_message
        }
    ))
    # print('MESSAGES: ',messages)
    # print(messages)

    try:
        response = infer_chat(messages, TOOLS)
        print("\nRESPONSE: ",response)
        # history = [
        #     {
        #         "role":"assistant",
        #         "content":response
        #     }
        # ]
        # messages.append(history)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)