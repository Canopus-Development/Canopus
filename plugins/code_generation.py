# plugins/code_generation.py
import json
from openai import OpenAI
from config.config import AIConfig, logger

class CodeGenerator:
    def __init__(self):
        self.client = OpenAI(
            base_url=AIConfig.ENDPOINT,
            api_key=AIConfig.API_KEY
        )

    def generate_code(self, prompt):
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": AIConfig.SYSTEM_MESSAGES["code"]},
                    {"role": "user", "content": prompt}
                ],
                model=AIConfig.MODELS["gpt4"]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in code generation: {e}")
            return "Sorry, I couldn't generate the code."

code_generator = CodeGenerator()
def execute(command): 
    logger.info("Processing user command for code generation plugin.")
    return code_generator.generate_code(command)
