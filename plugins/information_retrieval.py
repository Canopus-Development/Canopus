import requests
from config.config import InformationGeneratorConfig, logger

def execute(user_command):
    logger.info("Executing information generator plugin.")
    try:
        headers = {"Content-Type": "application/json"}
        payload = {"message": user_command, "model": "llama2"}
        response = requests.post(InformationGeneratorConfig.INFO_API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()
            generated_code = data.get("response")
            return generated_code
        else:
            return f"Failed to retrieve information. Status code: {response.status_code}"
    except Exception as e:
        logger.error(f"Error in information generator plugin: {str(e)}")
        return "An error occurred while retrieving information."
