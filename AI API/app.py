import asyncio
import aiohttp
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import ujson
import uvloop
from cachetools import TTLCache
import time
from contextlib import asynccontextmanager
import logging
from concurrent.futures import ProcessPoolExecutor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use uvloop for better performance
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

OLLAMA_API = "http://localhost:11434/api/generate"
CACHE_SIZE = 1000
CACHE_TTL = 3600  # 1 hour
TIMEOUT = 300  # 5 minutes timeout

# Initialize cache
cache = TTLCache(maxsize=CACHE_SIZE, ttl=CACHE_TTL)

class GenerateRequest(BaseModel):
    prompt: str
    model: str
async def generate_ollama(prompt: str, model: str):
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
                    
                    if full_response:
                        logger.info(f"Generated response: {full_response}")
                        return full_response.strip()
                    else:
                        logger.warning("Empty response from Ollama API")
                        raise HTTPException(status_code=500, detail="Empty response from Ollama API")
                else:
                    raise HTTPException(status_code=response.status, detail="Ollama API error")
        except asyncio.TimeoutError:
            logger.error("Ollama API request timed out")
            raise HTTPException(status_code=504, detail="Request timed out")
        except Exception as e:
            logger.error(f"Error in generate_ollama: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

async def pre_warm_model():
    warm_up_prompt = "Write a hello world function in Python"
    warm_up_model = "codellama:7b-instruct-q4_0"
    try:
        await asyncio.wait_for(generate_ollama(warm_up_prompt, warm_up_model), timeout=30)
        logger.info("Model pre-warmed successfully")
    except asyncio.TimeoutError:
        logger.warning("Pre-warming timed out, but this is okay for the first run.")

async def periodic_pre_warm():
    while True:
        await pre_warm_model()
        await asyncio.sleep(300)  # Sleep for 5 minutes

def cpu_bound_task(data):
    # Simulate a CPU-bound task
    result = 0
    for i in range(1000000):
        result += i
    return result

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await pre_warm_model()
    periodic_task = asyncio.create_task(periodic_pre_warm())
    
    # Create a process pool for CPU-bound tasks
    app.state.process_pool = ProcessPoolExecutor()
    
    yield
    
    # Shutdown
    periodic_task.cancel()
    try:
        await periodic_task
    except asyncio.CancelledError:
        pass
    
    app.state.process_pool.shutdown()

app = FastAPI(lifespan=lifespan, json_loads=ujson.loads, json_dumps=ujson.dumps)

@app.post("/generate")
async def generate(request: GenerateRequest):
    cache_key = f"{request.prompt}:{request.model}"
    
    if cache_key in cache:
        return {"response": cache[cache_key], "source": "cache"}

    try:
        start_time = time.time()
        response = await generate_ollama(request.prompt, request.model)
        
        if not response:
            logger.warning("Empty response received from Ollama API")
            raise HTTPException(status_code=500, detail="Empty response from Ollama API")
        
        logger.info(f"Response from Ollama API: {response}")
        
        # Perform a CPU-bound task in a separate process
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(app.state.process_pool, cpu_bound_task, response)
        
        end_time = time.time()

        cache[cache_key] = response

        return {"response": response, "generation_time": end_time - start_time, "source": "ollama"}
    except HTTPException as he:
        logger.error(f"HTTPException in generate endpoint: {str(he)}")
        raise he
    except Exception as e:
        logger.error(f"Error in generate endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")    