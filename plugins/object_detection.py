import requests
from plugins.utils import capture_image
from config.config import ObjectDetectionConfig, logger

def execute(user_command):
    logger.info("Executing object detector plugin.")
    try:
        image_path = capture_image()

        files = {"file": open(image_path, "rb")}
        response = requests.post(
            ObjectDetectionConfig.OBJECT_API_URL,
            headers={"Content-Type": "multipart/form-data"},
            files=files
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("response")
        else:
            return f"Failed to detect object. Status code: {response.status_code}"
    except Exception as e:
        logger.error(f"Error in object detector plugin: {str(e)}")
        return "An error occurred while detecting objects."
    finally:
        if files and files["file"]:
            files["file"].close()
