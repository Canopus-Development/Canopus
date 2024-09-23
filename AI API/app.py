
import asyncio
import logging
import os
from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
import aiohttp
import ujson
from cachetools import TTLCache
import cv2
import numpy as np
from onnxruntime import InferenceSession
from dotenv import load_dotenv
import redis

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis setup
redis_client = redis.Redis(host='0.0.0.0', port=6379, db=0)

# FastAPI setup
app = FastAPI()

# Constants
OLLAMA_API = "http://localhost:11434/api/generate"
CACHE_SIZE = 1000
CACHE_TTL = 3600  # 1 hour
TIMEOUT = 600  # 10 minutes timeout

# Google Search API constants
GOOGLE_SEARCH_API_ENDPOINT = "https://www.googleapis.com/customsearch/v1"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

# Initialize cache
cache = TTLCache(maxsize=CACHE_SIZE, ttl=CACHE_TTL)

# Pydantic models
class GenerateRequest(BaseModel):
    prompt: str
    model: str = "codellama:7b-instruct-q4_0"

class ChatRequest(BaseModel):
    message: str
    model: str = "vicuna:7b-q4_0"

class SearchRequest(BaseModel):
    query: str
    model: str = "llama2"

# Helper functions
async def generate_ollama(prompt: str, model: str):
    cache_key = f"{prompt}:{model}"
    if cache_key in cache:
        return cache[cache_key]
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(OLLAMA_API, json={"model": model, "prompt": prompt}, timeout=TIMEOUT) as response:
                if response.status == 200:
                    full_response = ""
                    async for line in response.content:
                        try:
                            data = ujson.loads(line)
                            if 'response' in data:
                                full_response += data['response']
                            if data.get('done', False):
                                break
                        except ujson.JSONDecodeError:
                            logger.warning(f"Failed to parse line: {line}")
                    if not full_response:
                        raise HTTPException(status_code=500, detail="Empty response from Ollama API")
                    cache[cache_key] = full_response
                    return full_response
                else:
                    raise HTTPException(status_code=response.status, detail="Ollama API error")
        except Exception as e:
            logger.error(f"Error in generate_ollama: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

async def search_google(query: str, model: str):
    params = {"key": GOOGLE_API_KEY, "cx": GOOGLE_CSE_ID, "q": query, "num": 5}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(GOOGLE_SEARCH_API_ENDPOINT, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    search_results = data.get("items", [])
                    search_context = "\n".join([f"Title: {result['title']}\nSnippet: {result['snippet']}" for result in search_results[:3]])
                    prompt = f"Based on the following search results for the query '{query}', provide a comprehensive and accurate summary:\n\n{search_context}\n\nSummary:"
                    summary = await generate_ollama(prompt, model)
                    return {"query": query, "summary": summary, "search_results": search_results}
                else:
                    raise HTTPException(status_code=response.status, detail="Search API error")
        except Exception as e:
            logger.error(f"Error in search_google: {str(e)}")
            raise HTTPException(status_code=500, detail="Search engine error")

# FastAPI endpoints
@app.post("/generate")
async def generate(request: GenerateRequest):
    return {"response": await generate_ollama(request.prompt, request.model)}

@app.post("/detect_objects")
async def detect_objects(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    img = cv2.resize(img, (640, 640))
    img = img.transpose((2, 0, 1)).astype(np.float32) / 255.0
    img = np.expand_dims(img, axis=0)

    onnx_session = InferenceSession("yolov5s.onnx")
    ort_inputs = {onnx_session.get_inputs()[0].name: img}
    ort_outs = onnx_session.run(None, ort_inputs)

    detections = ort_outs[0]
    results = []
    for detection in detections[0]:
        score = float(detection[4])
        if score > 0.5:  # Confidence threshold
            class_id = int(detection[5])
            bbox = detection[:4].tolist()
            results.append({"class_id": class_id, "score": score, "bbox": bbox})

    return {"results": results}

@app.post("/chat")
async def chat(request: ChatRequest):
    return {"response": await generate_ollama(request.message, request.model)}

@app.post("/search")
async def search(request: SearchRequest):
    return await search_google(request.query, request.model)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7297)
