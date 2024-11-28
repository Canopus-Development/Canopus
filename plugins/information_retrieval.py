# plugins/information_retrieval.py
import threading
import requests
from config.config import InformationGeneratorConfig, logger
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from config.config import AIConfig, logger
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import UserMessage

class InformationRetriever:
    def __init__(self):
        self.client = ChatCompletionsClient(
            endpoint=AIConfig.ENDPOINT,
            credential=AzureKeyCredential(AIConfig.API_KEY)
        )

    def retrieve_information(self, query):
        try:
            response = self.client.complete(
                messages=[
                    UserMessage(content=query)
                ],
                temperature=AIConfig.TEMPERATURE,
                top_p=AIConfig.TOP_P,
                max_tokens=AIConfig.MAX_TOKENS,
                model=AIConfig.MODELS["o1-mini"]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Azure AI inference error: {e}")
            return "Sorry, I couldn't retrieve that information."

info_retriever = InformationRetriever()
def execute(command): return info_retriever.retrieve_information(command)
