import requests
from config.config import InformationRetrievalConfig, logger

def retrieve_information(query):
    logger.info("Retrieving information.")
    headers = {"Content-Type": "application/json"}
    payload = {
        "input": {
            "text": query
        },
        "model": "gemini-1.5-flash",
        "key": InformationRetrievalConfig.GEMINI_API_KEY
    }
    response = requests.post(InformationRetrievalConfig.GEMINI_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        logger.info("Information retrieval successful.")
        return response.json().get("content")
    logger.error("Information retrieval failed.")
    return None