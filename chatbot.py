from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Tuple
from openai import OpenAI
from utils import query_pdfs, get_distinct_field
import json
from bot_utils.functions import *
from bot_utils.prompts import *
from config import settings

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
    
    try:
        chat_response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        tool_calls = chat_response.choices[0].message.tool_calls
        
        if tool_calls:
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                function_response = get_function_response(function_name, function_args)
                print('FUNCTION NAME: ',function_name)
                print('FUNCTION ARGS: ',function_args)
                # print('FUNCTION_RESPONSE: ',function_response) 
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
                return function_enriched_response.choices[0].message.content
                # print(function_enriched_response.choices[0].message.parsed)
                # return function_enriched_response.choices[0].message.parsed
                
        return chat_response.choices[0].message.content
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask_question(chat_request: ChatRequest):
    print("RECEIVED REQUEST: ", chat_request)
    new_message = chat_request.message
    
    chat_history = chat_request.history
    
    print('RECEIVED NEW MESSAGE: ', new_message)
    print('RECEIVED HISTORY: ',chat_history)
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]
    
    for (mess,resp) in chat_history[:-10]:
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
    print('MESSAGES: ',messages)
    # print(messages)

    try:
        response = infer_chat(messages, TOOLS)
        # print("RESPONSE: ",response)
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