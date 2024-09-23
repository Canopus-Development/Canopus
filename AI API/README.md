
# High-Performance AI Model API Setup Guide

This guide will walk you through setting up a high-performance API for AI model inference using Ollama and FastAPI on an Oracle free tier VM with an ARM processor.

## System Requirements

- Oracle free tier VM with ARM processor
- 24GB RAM
- Ubuntu 20.04 or later

## Step 1: Initial Setup

1. Update your system:
   ```
   sudo apt update && sudo apt upgrade -y
   ```

2. Install required system packages:
   ```
   sudo apt install -y python3-pip python3-venv git curl
   ```

## Step 2: Install and Configure Ollama

1. Install Ollama:
   ```
   curl https://ollama.ai/install.sh | sh
   ```

2. Start Ollama service:
   ```
   ollama serve
   ```

3. Pull optimized models:
   ```
   ollama pull codellama:7b-instruct-q4_0
   ollama pull llama2
   ollama pull vicuna:7b-q4_0
   ```

## Step 3: Set Up Python Environment

1. Create a virtual environment:
   ```
   python3 -m venv aienv
   source aienv/bin/activate
   ```

2. Install required Python packages:
   ```
   pip install fastapi uvicorn aiohttp ujson uvloop
   ```
## Step 4: Create the FastAPI Application

1. Create a new file named `main.py` and paste the following code:
```
# main.py

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
    uvicorn.run(app, host="0.0.0.0", port=8000)

```

2. Create a `.env` file in the same directory as `main.py` and add the following environment variables:

```
GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY
GOOGLE_CSE_ID=YOUR_GOOGLE_CSE_ID
```

## Step 5: Run the Application

1. Start the FastAPI application:
   ```
   python main.py
   ```

## Step 6: Using the API

1. For single generation:
   ```
   curl -X POST "http://localhost:7297/generate" -H "Content-Type: application/json" -d '{"prompt": "Write a Python function to sort a list", "model": "codellama:7b-instruct-q4_0"}'
   ```

2. For batch generation:
   ```
   curl -X POST "http://localhost:7297/batch_generate" -H "Content-Type: application/json" -d '[{"prompt": "What is AI?", "model": "llama2:7b-q4_0"}, {"prompt": "Explain quantum computing", "model": "llama2}]'
   ```

## Performance Optimization Tips

1. **Model Quantization**: Use Ollama's quantized models (e.g., `llama2`) for faster inference.

2. **Caching**: The LRU cache will store results for repeated queries. Adjust the `maxsize` in `@lru_cache(maxsize=1000)` based on your RAM availability.

3. **Batching**: Use the `/batch_generate` endpoint for multiple queries. Adjust `BATCH_SIZE` based on your system's capabilities.

4. **CPU Optimization**: The code uses all available CPU cores. Ensure your system is using performance CPU governors.

5. **Network Optimization**: If possible, optimize your network stack for low latency.

6. **Memory Usage**: Monitor memory usage and adjust the LRU cache size if needed.

7. **Regular Updates**: Keep Ollama and all dependencies updated for the latest performance improvements.

## Monitoring and Maintenance

1. Monitor system resources using tools like `htop` or `glances`.

2. Regularly update Ollama and the pulled models:
   ```
   ollama pull codellama:7b-instruct-q4_0
   ollama pull llama2
    ollama pull vicuna:7b-q4_0
   ```
3. Keep Python packages updated:
   ```
   pip install --upgrade fastapi uvicorn aiohttp ujson uvloop
   ```

## Troubleshooting

1. If Ollama is not responding, ensure the service is running:
   ```
   ollama serve
   ```

2. Check Ollama logs for any errors:
   ```
   journalctl -u ollama
   ```
   
3. If you encounter memory issues, try reducing the LRU cache size or the number of worker processes.


