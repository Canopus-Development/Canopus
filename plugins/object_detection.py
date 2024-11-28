# plugins/object_detection.py
import threading
import requests
import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import (
    SystemMessage, UserMessage, TextContentItem,
    ImageContentItem, ImageUrl, ImageDetailLevel
)
from azure.core.credentials import AzureKeyCredential
from config.config import AIModelsConfig, logger
from plugins.utils import capture_image

class ObjectDetector:
    def __init__(self):
        self.client = ChatCompletionsClient(
            endpoint=AIModelsConfig.AZURE_ENDPOINT,
            credential=AzureKeyCredential(AIModelsConfig.AZURE_API_KEY)
        )

    def detect_objects(self, image_path=None):
        if not image_path:
            image_path = capture_image()

        response = self.client.complete(
            messages=[
                SystemMessage(content="You are a helpful assistant that describes images in details."),
                UserMessage(content=[
                    TextContentItem(text="What's in this image?"),
                    ImageContentItem(
                        image_url=ImageUrl.load(
                            image_file=image_path,
                            image_format="jpg",
                            detail=ImageDetailLevel.LOW
                        )
                    )
                ])
            ],
            model=AIModelsConfig.MODELS["llama"]
        )
        return response.choices[0].message.content

object_detector = ObjectDetector()
def execute(command): return object_detector.detect_objects()
