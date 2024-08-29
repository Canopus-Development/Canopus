import requests
from config.config import InformationGeneratorConfig, logger, APIConfig


def info(prompt):
    logger.info("Infomer Is on")
    headers = {"Content-Type": "application/json", "X-API-Key": APIConfig.API_KEY}
    payload = {"message": prompt, "model": "llama2"}
    response = requests.post(InformationGeneratorConfig.INFO_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        logger.info("Information retrived Succesfully")
        data = response.json()
        generated_code = data.get("response")
        generation_time = data.get("generation_time")
        source = data.get("source")
        return generated_code
    else:
        logger.error("Failed to Retrive information.")
        return None
