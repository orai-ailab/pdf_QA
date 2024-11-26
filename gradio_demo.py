import time
import gradio as gr
import json
import os
import requests
from typing import Tuple, List, Optional

API_URL = "http://localhost:8000/ask"

def clean_and_parse_json(response_text: str) -> dict:
    try:
        if response_text.startswith('"') and response_text.endswith('"'):
            response_text = response_text[1:-1]
            
        response_text = response_text.encode().decode('unicode_escape')
        
        if response_text.startswith('```') and response_text.endswith('```'):
            response_text = response_text[3:-3].strip()
            
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return {"response": "Sorry, I encountered an error processing the response.", "link": ""}

    
def call_chatbot_api(message: str) -> dict:
    try:
        response = requests.post(
            API_URL,
            json={"text": message},
            headers={"Content-Type": "application/json"}
        )
        
        # response_text = response_text.strip()
        # if response_text.startswith("```") and response_text.endswith("```"):
            # response_text = response_text[3:-3].strip()
            
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"API call failed: {e}")
        return {"response": f"Error: Could not connect to the chatbot API. {str(e)}"}

def process_chat(message: str, history: List[Tuple[str, str]]) -> Tuple[List[Tuple[str, str]], Optional[str]]:
    try:
        api_response = call_chatbot_api(message)
        response_text = clean_and_parse_json(api_response)
        history.append((message, response_text["response"]))
        image = None
        if "link" in response_text and os.path.isfile(response_text["link"]):
            try:
                image = response_text["link"]
            except Exception as e:
                print(f"Error loading image: {e}")
                image = None
        print('TRY RUNNED')
        return history, image
    except Exception as e:
        error_message = f"Error processing message: {str(e)}"
        history.append((message, error_message))
        print('EXCEPT RUNNED')
        return history, None

if __name__ == "__main__":
    with gr.Blocks() as demo:
        chatbot = gr.Chatbot()
        msg = gr.Textbox(label="Message")
        image_output = gr.Image(label="Response Image")
        
        msg.submit(
            process_chat,
            inputs=[msg, chatbot],
            outputs=[chatbot, image_output],
            queue=False
        ).then(
            lambda: "", 
            None,
            msg
        )
        
        demo.launch(share=True)