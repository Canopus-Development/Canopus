import requests
from config.config import ChatGenerationConfig, logger, APIConfig


def Chater(prompt):
    logger.info("Chatter is on")
    headers = {"Content-Type": "application/json", "X-API-Key": APIConfig.API_KEY}
    payload = {"message": prompt, "model": "llama2"}
    response = requests.post(ChatGenerationConfig.CHAT_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        logger.info("Chatted successfully")
        data = response.json()
        generated_code = data.get("response")
        generation_time = data.get("generation_time")
        source = data.get("source")
        return generated_code
    else:
        logger.error(f"Failed to chat. Status code: {response.status_code}")
        return None
