import time
import gradio as gr
import json
import os
from openai import OpenAI
from gradio_multimodalchatbot import MultimodalChatbot
from gradio.data_classes import FileData
from config import settings
from utils import query_pdfs

def infer_chat(message):
    model = settings.LLM_INFERENCE_MODEL
    TOGETHER_API_KEY = settings.TOGETHER_API_KEY
    client = OpenAI(
        api_key=TOGETHER_API_KEY,
        base_url='https://api.together.xyz/v1',
    )
    chat_response = client.chat.completions.create(
        model=model,
        messages=message,
        top_p=0.2,
        stream=False,
    )   
    return chat_response.choices[0].message.content
def paraphrase(message):
    infer_message = [{
        "role": "user",
        "content": f"""
            Simple paraphrase this message : `{message}`
            Just return the paraphrased sentence, do not say anything else.
        """
    }]
    response = infer_chat(infer_message)
    return response
def chat_response(message):
    query_result = query_pdfs(message)
    
    infer_message = [{
        "role": "user",
        "content": f"""
            User will ask you the information relating to some pdf files.
            This is their question: {message}
            You are required to answer their question based on this relevant information which is queried from vector database according to the user's message. Extract the relevant info and answer to user. If the query result is table or picture,select the most appropriate table/picture provide path to the table. If the query give you different path, choose the first one.
            This is the query result (information you rely on):
            ```
            {query_result}
            ```
            Your answer must be in this json format, dont reply anything else, like this:
            {{
                "text":"your response after concatenate all relative information to get the answer",
                "files":"path_to_table or path_to_picture if you think a table or picture relate to user's question else you can leave this ''."
            }}
        """
    }]
    response = infer_chat(infer_message)
    try:
        json_loaded_response = json.loads(response)
        print(json_loaded_response)
    except:
        print('JSON not properly generated')
        print(response)
    
    return json_loaded_response
# # user_msg3 = {"text": "Give me a video clip please.",
# #              "files": []}
# # bot_msg3 = {"text": "Here is a video clip of the world",
# #             "files": [{"file": FileData(path="table_Well Test Report_nr-20/table_page_004.png")},
# #                     ]}

# # conversation = [[user_msg3, bot_msg3]]

# # with gr.Blocks() as demo:
# #     MultimodalChatbot(value=conversation, height=800)


# # demo.launch()



def process_chat(message, history):
    # Call your chat function
    response = chat_response(message)
    
    # Append the new message to history
    history.append((message, response["text"]))
    
    # Handle image display
    image = None
    if response["files"] and os.path.isfile(response["files"]):
        try:
            image = response["files"]
        except Exception as e:
            print(f"Error loading image: {e}")
            image = None
    
    return history, image

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