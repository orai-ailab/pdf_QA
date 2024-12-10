import time
import gradio as gr
import json
import os
import requests
import re
from typing import Tuple, List, Optional, Dict

API_URL = "http://localhost:8000/ask"
def prune_history(history):
    """
    history = [
        ('hi', "It's nice to meet you. How can I assist you today?"),
        ...
    ]
    """
    if len(history) == 0:
        return history
    try:
        i = -1
        count_word = 0 
        while count_word < 1500 and abs(i) <= len(history):
            count_word += len(history[i][0]) + len(history[i][1])
            i -= 1
        print('WORD ADDED: ', count_word)
    except Exception as e:
        print('ERROR WHILE PRUNING HISTORY: ',e)
        return history 
    
    return history[i+1:]

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
    
def call_chatbot_api(message: str, history: List[Tuple[str,str]]) -> dict:
    try:
        # print('HISTORY GRADIO SEND: ',history[4:])
        pruned_history = prune_history(history=history[4:])
        print('PRUNED HISTORY: ',pruned_history)
        api_response = requests.post(
            API_URL,
            json={
                "message":message,
                "history":pruned_history
            },
            headers={"Content-Type": "application/json"}
        )
        print("MESSAGE : ",api_response)
        print("MESSAGE RESPONSE : ",api_response.json()["response"])
        print("MESSAGE PATH : ",api_response.json()["path"])
        return (api_response.json()["response"], api_response.json()["path"])
    except requests.exceptions.RequestException as e:
        print(f"API call failed: {e}")
        return {"response": f"Error: Could not connect to the chatbot API. {str(e)}"}

def process_chat(message: str, history: List[Tuple[str, str]]) -> Tuple[List[Tuple[str, str]], Optional[str]]:
    try:
        api_response = call_chatbot_api(message,history)
        api_message, api_path = api_response
    
        history.append((message, api_message))
        image = None
        if api_path and os.path.isfile(api_path):
            try:
                image = api_path
            except Exception as e:
                print(f"Error loading image: {e}")
                image = None
        print('PROCESSED MESSAGE SUCCESSFULLY')
        return history, image
    except Exception as e:
        error_message = f"Error processing message: {str(e)}"
        history.append((message, api_response))
        print(error_message)
        return history, None

def clear_chat_history(chatbot):
    # Reset chatbot to initial recommended message
    return [
        ["","It's recommended to ask your question in each bubble separately.\nIt's hard for a chatbot to respond properly to multiple questions at a time.\nFor example:"],
        ["❌ Give me all the report of Petrophysical? and summary the petrophysical result of Well named ''15/9-F-1''","❌ The petrophysical report for Well 15/9-F-1 includes information on rock mechanical testing, biostratigraphy, and drilling and measurements for the end of the well. The report also includes a stratigraphic reconstruction of bulk volatile chemistry from fluid inclusion. The petrophysical report is a comprehensive document that provides detailed information on the well's geology and properties."],
        ["✅ Give me all the report of Petrophysical?","✅ Petrophysical reports found in the database include PETROPHYSICAL_REPORT_1.PDF, PETROPHYSICAL_REPORT_3.PDF, PETROPHYSICAL_REPORT_1 (3).pdf, PETROPHYSICAL_REPORT_1 (4).PDF, and PETROPHYSICAL_REPORT_4.PDF. These reports cover wells 15/9-F-1, 15/9-F-1 A, 15/9-F-1 B, 15/9-F-10, and 15/9-F-15."],
        ["✅ summary the petrophysical result of Well named ''15/9-F-1''","✅The petrophysical result of Well 15/9-F-1 indicates that the Hugin Fm. seems to be missing, probably due to faulting. The Volve stratigraphy in general is difficult to recognize. Heather Fm. has a high net/gross ratio, N/G ~ 0.5. Two intervals might contain some residual oil: 3320.6 - 3322.5 m MD RKB / 2991.5 - 2993.0 m TVD MSL, and 3332.4 - 3334.0 m MD RKB / 3001.2 - 3002.5 m TVD MSL. However, no shows on cuttings are reported. Skagerak Fm. seems quite heterogeneous with rather poor properties, but slightly better in the lower part below 3450 m MD RKB. LWD log data is of good quality."]
    ]

if __name__ == "__main__":
    with gr.Blocks() as demo:
        chatbot = gr.Chatbot(value=[
            ["","It's recommended to ask your question in each bubble separately.\nIt's hard for a chatbot to respond properly to multiple questions at a time.\nFor example:"],
            ["❌ Give me all the report of Petrophysical? and summary the petrophysical result of Well named ''15/9-F-1''","❌ The petrophysical report for Well 15/9-F-1 includes information on rock mechanical testing, biostratigraphy, and drilling and measurements for the end of the well. The report also includes a stratigraphic reconstruction of bulk volatile chemistry from fluid inclusion. The petrophysical report is a comprehensive document that provides detailed information on the well's geology and properties."],
            ["✅ Give me all the report of Petrophysical?","✅ Petrophysical reports found in the database include PETROPHYSICAL_REPORT_1.PDF, PETROPHYSICAL_REPORT_3.PDF, PETROPHYSICAL_REPORT_1 (3).pdf, PETROPHYSICAL_REPORT_1 (4).PDF, and PETROPHYSICAL_REPORT_4.PDF. These reports cover wells 15/9-F-1, 15/9-F-1 A, 15/9-F-1 B, 15/9-F-10, and 15/9-F-15."],
            ["✅ summary the petrophysical result of Well named ''15/9-F-1''","✅The petrophysical result of Well 15/9-F-1 indicates that the Hugin Fm. seems to be missing, probably due to faulting. The Volve stratigraphy in general is difficult to recognize. Heather Fm. has a high net/gross ratio, N/G ~ 0.5. Two intervals might contain some residual oil: 3320.6 - 3322.5 m MD RKB / 2991.5 - 2993.0 m TVD MSL, and 3332.4 - 3334.0 m MD RKB / 3001.2 - 3002.5 m TVD MSL. However, no shows on cuttings are reported. Skagerak Fm. seems quite heterogeneous with rather poor properties, but slightly better in the lower part below 3450 m MD RKB. LWD log data is of good quality."]
        ])
        msg = gr.Textbox(label="Message")
        image_output = gr.Image(label="Response Image")
        clear_btn = gr.Button("Clear Context")
        
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
        
        # Add clear context button functionality
        clear_btn.click(
            clear_chat_history,
            inputs=[chatbot],
            outputs=[chatbot]
        )
        
        demo.launch(share=True)