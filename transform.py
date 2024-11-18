import os
from PIL import Image
import fitz  # PyMuPDF
from pathlib import Path
import json
from tqdm.notebook import tqdm
import sys
from collections import defaultdict
from openai import OpenAI
import fitz
import requests
import base64
from io import BytesIO
from config import settings
client = OpenAI(base_url=settings.FUNCTION_CALLING_BASE_URL, api_key=settings.TOGETHER_API_KEY)


def convert_image_to_bytes(image_path):

    img = Image.open(image_path)
    
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format=img.format)
    img_byte_arr = img_byte_arr.getvalue()
    
    return img_byte_arr

def get_image_description(image_path,previous_knowledge):
    image_bytes = convert_image_to_bytes(image_path)
    image_data = base64.b64encode(image_bytes).decode('utf-8')
    response = client.chat.completions.create(
        model="meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"You have to determine the description of this image/table. You are provided the previous content before this table/picture and your job is to determine the proper description for it.It's better to write a description more details. Previous content: {previous_knowledge}."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}},
                ],
            }
        ],
        max_tokens=300,
    )

    return response.choices[0].message.content

def get_image_description(name_file_path,page_num,previous_message):
    # name_file : string, end with .pdf,
    # page_num : int (where the table/pictures locate at the name_file)
    # previous message: string (the previous message of table/string we want to get description)
    # This function get the image of the page at page_num of the file pdf name_file_path, then pass that  image of page to message sending to chatbot to get the description of the table/picture in the page.
    pdf_document = fitz.open(name_file_path)
    page = pdf_document[page_num-1]
    zoom = 2
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img_data = pix.tobytes("png")
    image = Image.open(BytesIO(img_data))
    jpeg_buffer = BytesIO()

    image.convert('RGB').save(jpeg_buffer, format='JPEG', quality=85)
    jpeg_bytes = jpeg_buffer.getvalue()
    image_data = base64.b64encode(jpeg_bytes).decode('utf-8')
    response = client.chat.completions.create(
        model="meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"You are required to detect the title of a table/figure, which can be table or figure. The image user gives to you is the page which contain that table/ficture and you can identify that table/figure via it's `previous message`.Please determine the title for that table/figure when looking at the page. In other words, tell user what does figure is talking about. Describe under 50 word. The `previous message` here: {previous_message}. "},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}},
                ],
            }
        ],
        max_tokens=300,
    )
    if 'pdf_document' in locals():
        pdf_document.close()
    return response.choices[0].message.content

def extract_element_from_pdf(pdf_path, element_info_list, element='tables'):
    """
    Extract elements (tables or pictures) from PDF metadata using provided coordinates to get images of them.
    
    Args:
        pdf_path (str): Path to the PDF file
        element_info_list (list): List of dictionaries containing element location information
            [{
                "page_no": int,
                "bbox": {
                    "l": float,  # left
                    "t": float,  # top
                    "r": float,  # right
                    "b": float,  # bottom
                    "coord_origin": str  # coordinate system origin
                }
            }]
        element (str): Type of element to extract ('table' or 'picture')
    """
    try:
        if element not in ['tables', 'pictures']:
            raise ValueError("Element parameter must be either 'table' or 'picture'")
        
        pdf_name = Path(pdf_path).stem
        output_dir = f'{element}/{pdf_name}'
        os.makedirs(output_dir, exist_ok=True)
        
        doc = fitz.open(pdf_path)
        
        for idx, info in enumerate(element_info_list, 1):
            page = doc[info['page_no'] - 1]  
            page_height = page.rect.height
            
            bbox = info['bbox']
            
            if bbox['coord_origin'].upper() == 'BOTTOMLEFT':
                original_top = bbox['t']
                original_bottom = bbox['b']
                bbox['t'] = page_height - original_top
                bbox['b'] = page_height - original_bottom
            
            rect = fitz.Rect(
                bbox['l'],
                bbox['t'],
                bbox['r'],
                bbox['b']
            )
            
            pix = page.get_pixmap(clip=rect, matrix=fitz.Matrix(2, 2))  # 2x scaling for better quality
            output_path = os.path.join(output_dir, f'{element}_page_{info["page_no"]:03d}.png')
            pix.save(output_path)
            
            # print(f"Extracted {element} {idx} from page {info['page_no']} to: {output_path}")
        
        doc.close()
        
        # print(f"\nAll {element}s extracted to: {output_dir}")
        return output_path
        
    except Exception as e:
        print(f"Error extracting {element}: {str(e)}")
        return None


def concatenate_content_by_page(mapping):
  page_content_map = defaultdict(str)
  for ref, data in mapping.items():
    page = data['page']
    content = data['content']
    page_content_map[page] += content + '\n' 

  return dict(page_content_map)

def get_text_element_code_mapping(metadata):
    mapping = {}
    for text in metadata["texts"]:
        ref = text["self_ref"]
        content = text["text"]
        page = text["prov"][0]["page_no"]
        mapping[ref] = {
            "page":page,
            "content":content
        }
    return mapping

def handle_text_data(metadata):
    """
    return value:
    {
        "name_file": name_of_the_pdf_file,
        "type":"Text",
        "content":[
            {
                "pages":list,
                "text":string,
            }
        ]
        
    }
    Prepare group by logic
    """
    content = []
    mapping = get_text_element_code_mapping(metadata)
    for group in metadata["groups"]:
        text = ''
        page_set = set()
        for child in group["children"]:
            text += mapping[child["$ref"]]["content"] + '\n'
            page_set.add(mapping[child["$ref"]]["page"])
            mapping.pop(child["$ref"])
        content.append({
            "page_num":page_set,
            "text":text
        })

    page_concatenation = concatenate_content_by_page(mapping)
    for key, val in page_concatenation.items():
        content.append({
            "page_num":{key}, 
            "text":val
        })
    result = [{
        "name_file":metadata["origin"]["filename"],
        "type":"text",
        "content":con
    } for con in content]
    # with open('text_result_test.json','w') as f:
    #     json.dump(result,f,indent=4,ensure_ascii=False)
    # print(result)
    return result
    # pass

def get_previous_message(metadata,mapping,element_ref,latest=20):
    result = ''
    elements = metadata["body"]["children"]
    for i in range(len(elements)):
        if elements[i]["$ref"] == element_ref:
            index = i
            break
    traceback = index
    count = 0 
    while traceback >= 0 and count < latest:
        ref = elements[traceback]["$ref"]
        if "texts" in ref:
            result += mapping[ref]["content"] + '\n'
            count += 1
        traceback -= 1
    return result

def handle_table_data(metadata,pdf_path):
    """ 
    return value:
    {
        "name_file": name_of_the_pdf_file,
        "type":"Table",
        "content":[
            "page_num":int,
            "link_to_table": path_to_table,
            "description": captions of the table else prepare VLM function
        ]
    }
    """
    pdf_folder = "pdf/"
    mapping = get_text_element_code_mapping(metadata)
    content = []
    total_tables = len(metadata['tables'])
    sys.stdout.flush()  
    name_file = pdf_folder+metadata["origin"]["filename"].replace(".PDF",".pdf")
    for table in tqdm(metadata['tables'], 
                       total=total_tables,
                       desc="Processing pictures",
                       ncols=80):  
        ref = table["self_ref"]
        page_num = table["prov"][0]["page_no"]
        # try:
        #     description =  mapping.get(table["captions"][0]["$ref"],'')
        # except:
        #     description = ''
        link_to_table = extract_element_from_pdf(pdf_path,table["prov"],element='tables')
        previous_message = get_previous_message(metadata,mapping,ref)
        
        data = {
            "page_num":page_num,
            "link_to_table":link_to_table,
            "description":  get_image_description(name_file,page_num,previous_message)
        }
        # print("link to tablee ", data["link_to_table"])
        content.append(data)
    return [{
        "name_file":name_file,
        "type":"table",
        "content":con
    } for con in content]
    
def handle_picture_data(metadata, pdf_path):
    pdf_folder = 'pdf/'
    mapping = get_text_element_code_mapping(metadata)
    content = []
    
    total_pictures = len(metadata['pictures'])
    # print(f"\nProcessing {total_pictures} pictures...")
    sys.stdout.flush()  
    name_file = pdf_folder + metadata["origin"]["filename"].replace(".PDF",".pdf")
    for picture in tqdm(metadata['pictures'], 
                       total=total_pictures,
                       desc="Processing pictures",
                       ncols=80):  
        ref = picture["self_ref"]
        page_num = picture["prov"][0]["page_no"]
        # try:
        #     description = mapping.get(picture["captions"][0]["$ref"],'')
        # except:
        #     description = ''
        link_to_picture = extract_element_from_pdf(pdf_path, picture["prov"], element='pictures')
        previous_message = get_previous_message(metadata, mapping, ref)
        data = {
            "page_num": page_num,
            "link_to_picture": link_to_picture,
            "description": get_image_description(name_file,page_num,previous_message)
        }
        # print(f'description : {data["description"]}')
        content.append(data)
    # tqdm.write(f'description : {data["description"]}')
    return [{
        "name_file": metadata["origin"]["filename"],
        "type": "pictures",
        "content": con
    } for con in content]

def prepare_data(metadata,pdf_path):
    result = []
    info = [handle_text_data(metadata), handle_table_data(metadata,pdf_path), handle_picture_data(metadata,pdf_path)]
    for ele in info:
        for e in ele:
            result.append(e)
    return result
    