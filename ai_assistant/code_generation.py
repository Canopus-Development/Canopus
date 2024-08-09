import requests
from config.config import CodeGenerationConfig, logger

def generate_code(prompt):
    logger.info("Generating code.")
    headers = {"Content-Type": "application/json"}
    payload = {"prompt": prompt, "model": "codellama:7b-instruct-q4_0"}
    response = requests.post(CodeGenerationConfig.GENERATE_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        logger.info("Code generation successful.")
        data = response.json()
        generated_code = data.get("response")
        generation_time = data.get("generation_time")
        source = data.get("source")
        return generated_code
    else:
        logger.error("Failed to generate code.")
        return None
