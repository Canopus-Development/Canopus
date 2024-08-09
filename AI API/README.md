
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
import asyncio
import aiohttp
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from functools import lru_cache
import ujson
import uvloop
import os
from concurrent.futures import ProcessPoolExecutor

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

app = FastAPI(json_loads=ujson.loads, json_dumps=ujson.dumps)

OLLAMA_API = "http://localhost:11434/api/generate"
MAX_WORKERS = os.cpu_count()
BATCH_SIZE = 10

os.environ["OMP_NUM_THREADS"] = str(MAX_WORKERS)
os.environ["MKL_NUM_THREADS"] = str(MAX_WORKERS)

class GenerateRequest(BaseModel):
    prompt: str
    model: str

executor = ProcessPoolExecutor(max_workers=MAX_WORKERS)

@lru_cache(maxsize=1000)
def cached_generate(prompt: str, model: str):
    return prompt, model

async def generate_ollama(prompt: str, model: str):
    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.post(OLLAMA_API, json={"model": model, "prompt": prompt}) as response:
            if response.status == 200:
                data = await response.json(loads=ujson.loads)
                return data['response']
            else:
                raise HTTPException(status_code=response.status, detail="Ollama API error")

async def batch_generate(requests):
    tasks = [generate_ollama(req.prompt, req.model) for req in requests]
    return await asyncio.gather(*tasks)

@app.post("/generate")
async def generate(request: GenerateRequest, background_tasks: BackgroundTasks):
    try:
        cached_result = cached_generate(request.prompt, request.model)
        if cached_result != (request.prompt, request.model):
            return {"response": cached_result}

        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(executor, generate_ollama, request.prompt, request.model)
        
        background_tasks.add_task(cached_generate, request.prompt, request.model)
        
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch_generate")
async def batch_generate_endpoint(requests: list[GenerateRequest]):
    try:
        results = []
        for i in range(0, len(requests), BATCH_SIZE):
            batch = requests[i:i+BATCH_SIZE]
            results.extend(await batch_generate(batch))
        return {"responses": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=MAX_WORKERS)
```

## Step 5: Run the Application

1. Start the FastAPI application:
   ```
   python main.py
   ```

## Step 6: Using the API

1. For single generation:
   ```
   curl -X POST "http://localhost:8000/generate" -H "Content-Type: application/json" -d '{"prompt": "Write a Python function to sort a list", "model": "codellama:7b-instruct-q4_0"}'
   ```

2. For batch generation:
   ```
   curl -X POST "http://localhost:8000/batch_generate" -H "Content-Type: application/json" -d '[{"prompt": "What is AI?", "model": "llama2:7b-q4_0"}, {"prompt": "Explain quantum computing", "model": "llama2}]'
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


