import requests
from plugins.utils import capture_image
from config.config import ObjectDetectionConfig, logger, APIConfig

def ObjectDetector(prompt):
    logger.info("Detector Is on")

    # Capture the image
    image_path = capture_image()  # Assuming capture_image() returns the file path

    # Prepare the payload for multipart/form-data
    files = {"file": open(image_path, "rb")}
    payload = {"key": APIConfig.API_KEY}

    try:
        # Make the POST request
        response = requests.post(
            ObjectDetectionConfig.OBJECT_API_URL,
            headers={"Content-Type": "multipart/form-data", "X-API-Key": APIConfig.API_KEY},
            files=files,
            data=payload
        )

        # Check the response status
        if response.status_code == 200:
            logger.info("Object Detected Successfully")
            data = response.json()
            generated_code = data.get("response")
            generation_time = data.get("generation_time")
            source = data.get("source")
            return generated_code
        else:
            logger.error(f"Failed to Detect Object. Status Code: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return None
    finally:
        files["file"].close()

