import os
import json
from transform import prepare_data
from utils import add_pdfs

parsed_dir = 'parsed'
pdf_dir = 'pdf'

if not os.path.exists(parsed_dir):
    raise FileNotFoundError(f"Directory '{parsed_dir}' not found")
if not os.path.exists(pdf_dir):
    os.makedirs(pdf_dir)

for filename in os.listdir(parsed_dir):
    if filename.endswith('.json'):
        try:
            json_path = os.path.join(parsed_dir, filename)
            pdf_filename = filename.replace('.json', '.pdf')
            relative_pdf_path = os.path.join(pdf_dir, pdf_filename)
            
            with open(json_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            prepared_data = prepare_data(metadata, relative_pdf_path)
            # print(prepared_data)
            # break
            add_status = add_pdfs(prepared_data)
            
            if add_status:
                print(f"Successfully processed {filename}")
            else:
                print(f"Failed to process {filename}")
            # break
                
        except Exception as e:
            print(f"Error processing file {filename}: {str(e)}")
            continue