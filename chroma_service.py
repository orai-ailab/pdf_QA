import ctranslate2
from transformers import AutoTokenizer

import torch
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import argparse 
import time

model_name = "BAAI/bge-base-en-v1.5"
model_save_path = "bge_model_ctranslate2"
# model_path = "bge_model_ctranslate2_base"


device = "cpu"
tokenizer = AutoTokenizer.from_pretrained(model_name)
if device == "cuda":
    translator = ctranslate2.Encoder(
        model_save_path, device=device, compute_type="float16"
    )  # or "cuda" for GPU
else:
    translator = ctranslate2.Encoder(model_save_path, device=device)


def generate_embeddings(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    input_ids = inputs["input_ids"].tolist()[0]
    output = translator.forward_batch([input_ids])
    pooler_output = output.pooler_output
    if device == "cuda":
        embeddings = (
            torch.as_tensor(pooler_output, device=device).detach().cpu().tolist()[0]
        )
    else:
        pooler_output = np.array(pooler_output)
        embeddings = torch.as_tensor(pooler_output, device=device).detach().tolist()[0]
    return embeddings


app = FastAPI()


class EmbeddingRequest(BaseModel):
    input: str
    model: str


class EmbeddingResponse(BaseModel):
    object: str = "list"
    data: list
    model: str
    usage: dict


@app.post("/v1/embeddings", response_model=EmbeddingResponse)
async def embeddings(request: EmbeddingRequest):
    input_text = request.input
    if not input_text:
        raise HTTPException(status_code=400, detail="No input text provided")

    # Generate embeddings
    embeddings = generate_embeddings(input_text)

    # Construct the response in OpenAI format
    response = {
        "object": "list",
        "data": [{"object": "embedding", "embedding": embeddings, "index": 0}],
        "model": request.model,
        "usage": {
            "prompt_tokens": len(input_text.split()),
            "total_tokens": len(input_text.split()),
        },
    }

    return response

@app.get("/ping")
async def ping():
    return {"status": "pong"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5001)
    args = parser.parse_args()
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=args.port)