import time
import gradio as gr
import json
import os
import requests
import re
from typing import Tuple, List, Optional, Dict

API_URL = "http://localhost:8000/ask"
def clean_and_parse_json(json_string):
    try:
        if json_string.startswith('"') and json_string.endswith('"'):
            json_string = json_string[1:-1]
        # Remove newline characters and escape characters if needed
        cleaned_string = json_string.replace('\n', '').replace('\\n', '\n')
        
        # Parse the cleaned string using json.loads()
        parsed_dict = json.loads(cleaned_string)
        
        return parsed_dict
    
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return {}

# def clean_and_parse_json(response_text: str) -> dict:
#     try:
#         response_text = response_text.strip('json\n')
#         if response_text.startswith('"') and response_text.endswith('"'):
#             response_text = response_text[1:-1]
#         print("CLEANED PHASE 1: ",response_text)
#         response_text = response_text.encode().decode('unicode_escape')
#         print("CLEANED PHASE 2: ",response_text)
#         if response_text.startswith('```') and response_text.endswith('```'):
#             response_text = response_text[3:-3].strip()
#         print("CLEANED PASE 2: ", response_text)
#         return json.loads(response_text.strip('json'))
#     except json.JSONDecodeError as e:
#         print(f"JSON parsing error: {e}")
#         return {"response": response_text, "link": ""}
    
# def clean_and_parse_json(response_text: str) -> dict:
#     try:
#         # Remove multiple layers of quotes
#         while response_text.startswith('"') and response_text.endswith('"'):
#             response_text = response_text[1:-1]
        
#         # Remove code block markers if present
#         if response_text.startswith('```json\n') and response_text.endswith('```'):
#             response_text = response_text[8:-3].strip()
        
#         # Remove escape characters
#         response_text = response_text.replace('\\n', '\n').replace('\\"', '"')
        
#         # Parse the JSON
#         return json.loads(response_text)
    
#     except json.JSONDecodeError as e:
#         print(f"JSON parsing error: {e}")
#         print(f"Problematic JSON string: {response_text}")
#         return {"response": response_text, "link": ""}
    
# def call_chatbot_api(message: str) -> dict:
def call_chatbot_api(message: str, history: List[Tuple[str,str]]) -> dict:
    try:
        api_response = requests.post(
            API_URL,
            # json={"text": message},
            json={
                "message":message,
                "history":history[4:]
            },
            headers={"Content-Type": "application/json"}
        )
        print("MESSAGE : ",api_response)
        # response_text = response_text.strip()
        # if response_text.startswith("```") and response_text.endswith("```"):
            # response_text = response_text[3:-3].strip()
        print("MESSAGE RESPONSE : ",api_response.json()["response"])
        print("MESSAGE LINK : ",api_response.json()["link"])
        return (api_response.json()["response"], api_response.json()["link"])
    except requests.exceptions.RequestException as e:
        print(f"API call failed: {e}")
        return {"response": f"Error: Could not connect to the chatbot API. {str(e)}"}
        # return ()
        

def process_chat(message: str, history: List[Tuple[str, str]]) -> Tuple[List[Tuple[str, str]], Optional[str]]:
    try:
        # api_response = call_chatbot_api(message)
        api_message, api_link = call_chatbot_api(message,history)
        # print("RAW RESPONSE: ",api_response)
    
        # response_text = clean_and_parse_json(api_response)
            
        history.append((message, api_message))
        image = None
        if api_link and os.path.isfile(api_link):
            try:
                image = api_link
            except Exception as e:
                print(f"Error loading image: {e}")
                image = None
        print('PROCESSED MESSAGE SUCCESSFULLY')
        return history, image
    except Exception as e:
        error_message = f"Error processing message: {str(e)}"
        history.append((message, error_message))
        print(error_message)
        return history, None

if __name__ == "__main__":
    with gr.Blocks() as demo:
        chatbot = gr.Chatbot(value=[
            ["","It's recommended to ask your question in each bubble separately.\nIt's hard for a chatbot to respond properly to multiple questions at a time.\nFor example:"],
            ["❌ Give me all the report of Petrophysical? and summary the petrophysical result of Well named ''15/9-F-1''","❌ The petrophysical report for Well 15/9-F-1 includes information on rock mechanical testing, biostratigraphy, and drilling and measurements for the end of the well. The report also includes a stratigraphic reconstruction of bulk volatile chemistry from fluid inclusion. The petrophysical report is a comprehensive document that provides detailed information on the well's geology and properties."],
            ["✅ Give me all the report of Petrophysical?","✅ Petrophysical reports found in the database include PETROPHYSICAL_REPORT_1.PDF, PETROPHYSICAL_REPORT_3.PDF, PETROPHYSICAL_REPORT_1 (3).pdf, PETROPHYSICAL_REPORT_1 (4).PDF, and PETROPHYSICAL_REPORT_4.PDF. These reports cover wells 15/9-F-1, 15/9-F-1 A, 15/9-F-1 B, 15/9-F-10, and 15/9-F-15."],
            ["✅ summary the petrophysical result of Well named ''15/9-F-1''","✅The petrophysical result of Well 15/9-F-1 indicates that the Hugin Fm. seems to be missing, probably due to faulting. The Volve stratigraphy in general is difficult to recognize. Heather Fm. has a high net/gross ratio, N/G ~ 0.5. Two intervals might contain some residual oil: 3320.6 - 3322.5 m MD RKB / 2991.5 - 2993.0 m TVD MSL, and 3332.4 - 3334.0 m MD RKB / 3001.2 - 3002.5 m TVD MSL. However, no shows on cuttings are reported. Skagerak Fm. seems quite heterogeneous with rather poor properties, but slightly better in the lower part below 3450 m MD RKB. LWD log data is of good quality."]])
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