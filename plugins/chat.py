# plugins/chatter.py
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from config.config import AIConfig, logger

class AIModelHandler:
    def __init__(self):
        self.client = ChatCompletionsClient(
            endpoint=AIConfig.ENDPOINT,
            credential=AzureKeyCredential(AIConfig.API_KEY)
        )

    def get_response(self, prompt):
        try:
            response = self.client.complete(
                messages=[
                    UserMessage(content=prompt)
                ],
                temperature=AIConfig.TEMPERATURE,
                top_p=AIConfig.TOP_P,
                max_tokens=AIConfig.MAX_TOKENS,
                model=AIConfig.MODELS["gpt4"]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Azure AI inference error: {str(e)}")
            raise

def execute(user_command):
    logger.info("Executing chat plugin")
    try:
        ai_handler = AIModelHandler()
        return ai_handler.get_response(user_command)
    except Exception as e:
        logger.error(f"Error in chat plugin: {str(e)}")
        return "I encountered an error while processing your request."
