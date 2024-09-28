# plugins/chatter.py
import requests
from config.config import ChatGenerationConfig, logger

def execute(user_command):
    logger.info("Executing chatter plugin.")
    try:
        headers = {"Content-Type": "application/json"}
        payload = {"message": user_command, "model": "vicuna:7b-q4_0"}
        response = requests.post(ChatGenerationConfig.CHAT_API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()
            generated_code = data.get("response")
            return generated_code
        else:
            return f"Failed to chat. Status code: {response.status_code}"
    except Exception as e:
        logger.error(f"Error in chatter plugin: {str(e)}")
        return "An error occurred while generating the chat response."
