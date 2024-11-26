import chromadb
# from .encoder import get_embedding
import uuid
from tqdm import tqdm
from config import settings
import os
import json
from logs.logger_config import logger
import requests

def get_embedding(content=""):
    response = requests.post(
        f"{settings.ENCODER_INFERENCE_ENDPOINT}/v1/embeddings",
        json={"input": content, "model": settings.ENCODER_INFERENCE_MODEL},
    )

    # Check if the response is successful
    if response.status_code == 200:
        logger.bind(logger_name="encoder_inference").info("Encode done!")
    else:
        logger.bind(logger_name="encoder_inference").error(
            "Error:  {response.status_code} , {response.text} "
        )
    return response.json()["data"][0]["embedding"]


def generate_id():
    return str(uuid.uuid4())


def init_pdfs(
    COLLECTION_NAME=settings.PDF_COLLECTION_NAME,
    CHROMA_PERSISTENT_DISK=settings.CHROMA_PERSISTENT_DISK,
    CHROMA_ENDPOINT=settings.CHROMA_ENDPOINT,
):
    if CHROMA_PERSISTENT_DISK != None:
        chroma_client = chromadb.PersistentClient(path=CHROMA_PERSISTENT_DISK)
    else:
        chroma_client = chromadb.HttpClient(host=CHROMA_ENDPOINT)
    logger.bind(logger_name="system").info(chroma_client.heartbeat())
    chroma_client.get_or_create_collection(
        COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )
    logger.bind(logger_name="system").info(
        f"Collection {COLLECTION_NAME} initial successfully"
    )


def add_pdfs(
    pdfs=[],
    chroma_client=None,
    COLLECTION_NAME=settings.PDF_COLLECTION_NAME,
    CHROMA_PERSISTENT_DISK=settings.CHROMA_PERSISTENT_DISK,
    CHROMA_ENDPOINT=settings.CHROMA_ENDPOINT,
):
    try:
        if chroma_client == None:
            if CHROMA_PERSISTENT_DISK != None:
                chroma_client = chromadb.PersistentClient(path=CHROMA_PERSISTENT_DISK)
            else:
                chroma_client = chromadb.HttpClient(host=CHROMA_ENDPOINT)
        logger.bind(logger_name="system").info(chroma_client.heartbeat())
        collection = chroma_client.get_collection(COLLECTION_NAME)
    except Exception as e:
        logger.bind(logger_name="system").info("ERROR: ", e)
        return "Fail"
    for pdf in tqdm(pdfs):
        try:
            # chunk = f"""Filename: {pdf["name_file"]}\n\nType: {pdf["type"]}\n\nPage_num: {pdf["content"].get("page_num",None)}\n\nText: {pdf["content"].get("text", None)}\n\nLink_to_table: {pdf["content"].get("link_to_table",None)}\n\nLink_to_picture: {pdf["content"].get("link_to_pictures",None)}\n\nDescription: {pdf["content"].get("description",None)}"""
            # chunk = f"""
            #     Filename: {pdf["name_file"]}\n\n
            #     Type: {pdf["type"]}\n\n
            #     Report type: {pdf["report_type"]}\n\n
            #     Well name: {pdf["well_name"]}\n\n
            #     Extra information: {pdf["extra"]}\n\n
            #     Page_num: {pdf["content"].get("page_num",None)}\n\n
            #     Text: {pdf["content"].get("text", None)}\n\n
            #     Link_to_table: {pdf["content"].get("link_to_table",None)}\n\n
            #     Link_to_picture: {pdf["content"].get("link_to_picture",None)}\n\n
            #     Description: {pdf["content"].get("description",None)}
            #     """
            text = pdf["content"].get("text", '')
            description = pdf["content"].get("description",'')
            if not text or text == 'None':
                text = ''
            if not description or description == 'None':
                description = ''
            chunk = f"""
                {text}.\n
                {description}.\n
                Report type of {pdf["report_type"]}.\n
                Talking about well {pdf["well_name"]}.\n
                
                """
            chunk_id = f"PDF-{generate_id()}"
            embedding = get_embedding(chunk)
            # metadata = {"Filename": str(pdf["name_file"]),
            #             "Type": str(pdf["type"]),
            #             "Page_num": str(pdf["content"].get("page_num",None)),
            #             "Text":str(pdf["content"].get("text",None)),
            #             "Link_to_table":str(pdf["content"].get("link_to_table",None)),
            #             "Link_to_picture":str(pdf["content"].get("link_to_picture",None)),
            #             "Description":str(pdf["content"].get("description",None))
            #             }
            metadata = {"Filename": str(pdf["name_file"]),
                        "Report_type": str(pdf["report_type"]),
                        "Well_name": str(pdf["well_name"]),
                        "Extra_infomation": str(pdf["extra"]),
                        "Type": str(pdf["type"]),
                        "Page_num": str(pdf["content"].get("page_num",None)),
                        "Text":str(pdf["content"].get("text",None)),
                        "Link_to_table":str(pdf["content"].get("link_to_table",None)),
                        "Link_to_picture":str(pdf["content"].get("link_to_picture",None)),
                        "Description":str(pdf["content"].get("description",None))
                        }
            # print('chunking here: ',chunk)
            # print('metadata here: ',metadata)
            # print([pdf])
            collection.add(
                embeddings=[embedding],
                metadatas=[metadata],
                # documents = documents,
                ids=[chunk_id],
            )
        except Exception as e:
            logger.bind(logger_name="system").info(f"ERROR: {e}")
            logger.bind(logger_name="system").info(f"DROP: {pdf}")
    return "Suck seed"


def format_pdfs(metadatas):
    logger.bind(logger_name="system").info(metadatas)
    # print(metadatas[0].keys())
    outputs = ''
    for pdf in metadatas:
        try:
            # outputs += "\n\n" + f"""Filename: {pdf.get("Filename","None")}\nType: {pdf.get("Type","None")}\nPage_num: {pdf.get("Page_num","None")}\nText: {pdf.get("Text",None)}\nLink_to_table: {pdf.get("Link_to_table",None)}\nLink_to_picture: {pdf.get("Link_to_picture",None)}\nDescription: {pdf.get("Description",None)}""" 
            # outputs += "\n\n" + f"""
            #         Filename: {pdf["Filename"]}\n\n
            #         Type: {pdf["Type"]}\n\n
            #         Report type: {pdf["Report_type"]}\n\n
            #         Well name: {pdf["Well_name"]}\n\n
            #         Extra information: {pdf["Extra_infomation"]}\n\n

            #         Page_num: {pdf.get("Page_num",None)}\n\n
            #         Text: {pdf.get("Text", None)}\n\n
            #         Link_to_table: {pdf.get("Link_to_table",None)}\n\n
            #         Link_to_picture: {pdf.get("Link_to_picture",None)}\n\n
            #         Description: {pdf.get("Description",None)}
            #         """  + '------------------------------------'
            if not pdf.get("Text") or pdf.get("Text") == 'None':
                if not pdf.get("Link_to_table") or pdf.get("Link_to_table") == "None":
                    outputs += "\n\n" + f"""
                            Filename: {pdf["Filename"]}\n\n
                            Report type: {pdf["Report_type"]}\n\n
                            Well name: {pdf["Well_name"]}\n\n
                            Page_num: {pdf.get("Page_num",None)}\n\n
                            Link_to_picture: {pdf.get("Link_to_picture",None)}\n\n
                            Description: {pdf.get("Description",None)}
                            """  + '------------------------------------'
                else:
                    outputs += "\n\n" + f"""
                            Filename: {pdf["Filename"]}\n\n
                            Report type: {pdf["Report_type"]}\n\n
                            Well name: {pdf["Well_name"]}\n\n
                            Page_num: {pdf.get("Page_num",None)}\n\n
                            Link_to_table: {pdf.get("Link_to_table",None)}\n\n
                            Description: {pdf.get("Description",None)}
                            """  + '------------------------------------'

            else:
                outputs += "\n\n" + f"""
                        Filename: {pdf["Filename"]}\n\n
                        Report type: {pdf["Report_type"]}\n\n
                        Well name: {pdf["Well_name"]}\n\n
                        Page_num: {pdf.get("Page_num",None)}\n\n
                        Text: {pdf.get("Text", None)}\n\n
                        """  + '------------------------------------'
        except Exception as e:
            print(f'Exception raised: {e} for keys',pdf.keys())
    logger.bind(logger_name="system").info(outputs)
    return outputs


def query_pdfs(
    query="",
    where={},
    n_results=10,
    n_top=5,
    group_by='',
    chroma_client=None,
    COLLECTION_NAME=settings.PDF_COLLECTION_NAME,
    CHROMA_PERSISTENT_DISK=settings.CHROMA_PERSISTENT_DISK,
    CHROMA_ENDPOINT=settings.CHROMA_ENDPOINT,
):
    try:
        if chroma_client == None:
            if CHROMA_PERSISTENT_DISK != None:
                chroma_client = chromadb.PersistentClient(path=CHROMA_PERSISTENT_DISK)
            else:
                chroma_client = chromadb.HttpClient(host=CHROMA_ENDPOINT)
            logger.bind(logger_name="system").info(chroma_client.heartbeat())
        collection = chroma_client.get_collection(name=COLLECTION_NAME)
    except:
        return f"Collection {COLLECTION_NAME} not found"
    query = "Represent this sentence for searching relevant passages: \n" + query
    if where:
        query_results = collection.query(query_embeddings=get_embedding(query),where=where, n_results=n_results)
    else:
        query_results = collection.query(query_embeddings=get_embedding(query),n_results=n_results)
    logger.bind(logger_name="system").info(query_results)
    if group_by:
        return [pdf[group_by] for pdf in query_results["metadatas"][0]]
    return format_pdfs(query_results["metadatas"][0][:n_top])

def list_collections(
    chroma_client=None,
    CHROMA_PERSISTENT_DISK=settings.CHROMA_PERSISTENT_DISK,
    CHROMA_ENDPOINT=settings.CHROMA_ENDPOINT,
):
    try:
        if chroma_client == None:
            if CHROMA_PERSISTENT_DISK != None:
                chroma_client = chromadb.PersistentClient(path=CHROMA_PERSISTENT_DISK)
            else:
                chroma_client = chromadb.HttpClient(host=CHROMA_ENDPOINT)
        
        collections = chroma_client.list_collections()
        logger.bind(logger_name="system").info("Available collections:")
        for collection in collections:
            logger.bind(logger_name="system").info(f"- Name: {collection.name}, Count: {collection.count()}")
        
        return collections
        
    except Exception as e:
        logger.bind(logger_name="system").error(f"Error listing collections: {e}")
        return []
    
def delete_collection(
    collection_name,
    chroma_client=None,
    CHROMA_PERSISTENT_DISK=settings.CHROMA_PERSISTENT_DISK,
    CHROMA_ENDPOINT=settings.CHROMA_ENDPOINT,
):
    try:
        if chroma_client == None:
            if CHROMA_PERSISTENT_DISK != None:
                chroma_client = chromadb.PersistentClient(path=CHROMA_PERSISTENT_DISK)
            else:
                chroma_client = chromadb.HttpClient(host=CHROMA_ENDPOINT)
                
        chroma_client.delete_collection(name=collection_name)
        logger.bind(logger_name="system").info(f"Collection '{collection_name}' deleted successfully")
        return True
        
    except Exception as e:
        logger.bind(logger_name="system").error(f"Error deleting collection '{collection_name}': {e}")
        return False

def list_chunks(
    collection_name=settings.PDF_COLLECTION_NAME,
    chroma_client=None,
    CHROMA_PERSISTENT_DISK=settings.CHROMA_PERSISTENT_DISK,
    CHROMA_ENDPOINT=settings.CHROMA_ENDPOINT,
):
    try:
        # Initialize ChromaDB client if not provided
        if chroma_client is None:
            if CHROMA_PERSISTENT_DISK is not None:
                chroma_client = chromadb.PersistentClient(path=CHROMA_PERSISTENT_DISK)
            else:
                chroma_client = chromadb.HttpClient(host=CHROMA_ENDPOINT)
        
        # Log connection status
        logger.bind(logger_name="system").info(chroma_client.heartbeat())

        # Get the collection
        collection = chroma_client.get_collection(name=collection_name)

        # Retrieve all chunks (documents)
        chunks = collection.get()

        # Log and return chunks
        documents = chunks.get("metadatas", [])
        logger.bind(logger_name="system").info(f"Retrieved {len(documents)} chunks from the collection '{collection_name}'")
        return documents

    except Exception as e:
        logger.bind(logger_name="system").error(f"Error listing chunks in collection '{collection_name}': {e}")
        return []

def get_distinct_field(
    field='Report_type',
    collection_name=settings.PDF_COLLECTION_NAME,
    chroma_client=None,
    CHROMA_PERSISTENT_DISK=settings.CHROMA_PERSISTENT_DISK,
    CHROMA_ENDPOINT=settings.CHROMA_ENDPOINT,
):
    try:
        if chroma_client is None:
            if CHROMA_PERSISTENT_DISK is not None:
                chroma_client = chromadb.PersistentClient(path=CHROMA_PERSISTENT_DISK)
            else:
                chroma_client = chromadb.HttpClient(host=CHROMA_ENDPOINT)

        logger.bind(logger_name="system").info(chroma_client.heartbeat())

        collection = chroma_client.get_collection(name=collection_name)
        chunks = collection.get()
        metadatas = chunks.get("metadatas", [])

        results = set()
        for metadata in metadatas:
            # print(metadata)
            # print('HI')
            records = metadata.get(field)
            if field:
                results.add(records)
            # break
        logger.bind(logger_name="system").info(f"Found distinct report types: {results}")
        return list(results)

    except Exception as e:
        logger.bind(logger_name="system").error(f"Error retrieving distinct report types: {e}")
        return []

# logger.bind(logger_name="system").info(query_faqs("tell me about distilled ai?"))


# init_faqs()


# add_status = add_faqs(faqs)
# logger.bind(logger_name="system").info("add_status: ", add_status)


if __name__ == "__main__":
    # init_pdfs()
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
                add_status = add_pdfs(prepared_data)
                
                if add_status:
                    print(f"Successfully processed {filename}")
                else:
                    print(f"Failed to process {filename}")
                    
            except Exception as e:
                print(f"Error processing file {filename}: {str(e)}")
                continue