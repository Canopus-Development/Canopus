import cv2
import requests
from config.config import ObjectDetectionConfig, logger

class ObjectDetector:
    def __init__(self):
        self.net = cv2.dnn.readNetFromCaffe(ObjectDetectionConfig.PROTOTXT_PATH, ObjectDetectionConfig.MODEL_PATH)

    def detect_objects(self):
        logger.info("Detecting objects.")
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        if not ret:
            logger.error("Failed to capture image.")
            return None

        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
        self.net.setInput(blob)
        detections = self.net.forward()

        if len(detections.shape) == 4:
            for i in range(detections.shape[2]):
                confidence = detections[0, 0, i, 0]  # Use index 0 for confidence
                if confidence > 0.2:
                    idx = int(detections[0, 0, i, 0])  # Use index 0 for class ID
                    return self.get_object_info(idx)
        return None

    def get_object_info(self, object_id):
        logger.info(f"Getting information for object ID: {object_id}.")
        headers = {"Content-Type": "application/json"}
        payload = {
            "input": {
                "text": f"What is object ID {object_id}?"
            }
        }
        response = requests.post(ObjectDetectionConfig.GEMINI_API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json().get("content")
        logger.error("Failed to retrieve object information.")
        return None
