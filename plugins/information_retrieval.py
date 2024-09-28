# plugins/information_retrieval.py
import threading
import requests
from config.config import InformationGeneratorConfig, logger

class InformationRetrievalService:
    def __init__(self):
        self.api_url = InformationGeneratorConfig.INFO_API_URL

    def retrieve_information(self, user_command):
        logger.info("Sending request for information retrieval.")
        try:
            headers = {"Content-Type": "application/json"}
            payload = {"message": user_command, "model": "llama2"}
            response = requests.post(self.api_url, headers=headers, json=payload)

            if response.status_code == 200:
                data = response.json()
                logger.info("Information retrieval successful.")
                return data.get("response", "No response from server.")
            else:
                logger.error(f"Failed to retrieve information. Status code: {response.status_code}")
                return f"Failed to retrieve information. Status code: {response.status_code}"
        except Exception as e:
            logger.error(f"Error in information retrieval: {str(e)}")
            return "An error occurred while retrieving information."

    def execute(self, command):
        # Check if the command contains the phrase "retrieve information"
        if "retrieve information" in command.lower():
            logger.info("Executing information retrieval based on command.")
            return self.retrieve_information(command)
        else:
            logger.info("No 'retrieve information' command detected.")
            return None  # Return None if not handling the command

# Initialize the Information Retrieval service once
information_retrieval_service = InformationRetrievalService()

def execute(command):
    return information_retrieval_service.execute(command)
