# plugins/code_generation.py
import requests
from config.config import CodeGenerationConfig, logger

def execute(user_command):
    logger.info("Processing user command for code generation plugin.")

    # Check if the user command contains the phrase "generate code"
    if "generate code" in user_command.lower():
        logger.info("Detected 'generate code' in user command. Executing code generation plugin.")
        try:
            headers = {"Content-Type": "application/json"}
            payload = {"prompt": user_command, "model": "codellama:7b-instruct-q4_0"}
            response = requests.post(CodeGenerationConfig.GENERATE_API_URL, headers=headers, json=payload)

            if response.status_code == 200:
                data = response.json()
                generated_code = data.get("response")
                return generated_code
            else:
                return f"Failed to generate code. Status code: {response.status_code}"
        except Exception as e:
            logger.error(f"Error in code generation plugin: {str(e)}")
            return "An error occurred while generating code."
    else:
        logger.info("'generate code' command not detected. No action taken.")
        return None  # Return None if not handling the command
