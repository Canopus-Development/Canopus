# plugins/object_detection.py
import threading
import requests
from plugins.utils import capture_image
from config.config import ObjectDetectionConfig, logger

class ObjectDetectionService:
    def __init__(self):
        self.api_url = ObjectDetectionConfig.OBJECT_API_URL

    def detect_objects(self):
        logger.info("Capturing image for object detection.")
        try:
            # Capture image using a utility function
            image_path = capture_image()

            # Open the image file and send it as part of a POST request
            with open(image_path, "rb") as image_file:
                files = {"file": image_file}
                response = requests.post(
                    self.api_url,
                    headers={"Content-Type": "multipart/form-data"},
                    files=files
                )

                # Process the response
                if response.status_code == 200:
                    data = response.json()
                    logger.info("Object detection successful.")
                    return data.get("response", "No response from server.")
                else:
                    logger.error(f"Failed to detect objects. Status code: {response.status_code}")
                    return f"Failed to detect objects. Status code: {response.status_code}"
        except Exception as e:
            logger.error(f"Error during object detection: {e}")
            return "An error occurred during object detection."

    def execute(self, command):
        # Check if the command contains the phrase "detect object"
        if "detect object" in command.lower():
            logger.info("Executing object detection based on command.")
            return self.detect_objects()
        else:
            logger.info("No 'detect object' command detected.")
            return None  # Return None if not handling the command

# Initialize the Object Detection service once
object_detection_service = ObjectDetectionService()

def execute(command):
    return object_detection_service.execute(command)
