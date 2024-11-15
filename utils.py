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
    CHROMA_PERSISTENT_DISK=settings.CHROMA_PERSISTENT_DISK,
    CHROMA_ENDPOINT=settings.CHROMA_ENDPOINT,
):
    if CHROMA_PERSISTENT_DISK != None:
        chroma_client = chromadb.PersistentClient(path=CHROMA_PERSISTENT_DISK)
    else:
        chroma_client = chromadb.HttpClient(host=CHROMA_ENDPOINT)
    logger.bind(logger_name="system").info(chroma_client.heartbeat())
    chroma_client.get_or_create_collection(
        settings.PDF_COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )
    logger.bind(logger_name="system").info(
        f"Collection {settings.PDF_COLLECTION_NAME} initial successfully"
    )


def add_pdfs(
    pdfs=[],
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
        logger.bind(logger_name="system").info(chroma_client.heartbeat())
        collection = chroma_client.get_collection(settings.PDF_COLLECTION_NAME)
    except Exception as e:
        logger.bind(logger_name="system").info("ERROR: ", e)
        return "Fail"
    for pdf in tqdm(pdfs):
        try:
            chunk = f"""Filename: {pdf["name_file"]}\n\nType: {pdf["type"]}\n\nContent: {pdf["content"]}"""
            chunk_id = f"PDF-{generate_id()}"
            embedding = get_embedding(chunk)
            metadata = {"Filename": str(pdf["name_file"]),
                        "Type": str(pdf["type"]),
                        "Content": str(pdf["content"])
                        }
            # print('metadata here: ')
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
            outputs += "\n\n" + f"""Filename: {pdf.get("Filename","None")}\nType: {pdf.get("Content","None")}\nContent: {pdf.get("Content","None")}""" 
        except:
            print('Exception raised: ',pdf.keys())
    logger.bind(logger_name="system").info(outputs)
    return outputs


def query_pdfs(
    query="",
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
            logger.bind(logger_name="system").info(chroma_client.heartbeat())
        collection = chroma_client.get_collection(name=settings.PDF_COLLECTION_NAME)
    except:
        return f"Collection {settings.PDF_COLLECTION_NAME} not found"
    query = "Represent this sentence for searching relevant passages: \n" + query
    query_results = collection.query(query_embeddings=get_embedding(query), n_results=30)
    logger.bind(logger_name="system").info(query_results)
    return format_pdfs(query_results["metadatas"][0])

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