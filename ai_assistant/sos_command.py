import cv2
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from config.config import SOSConfig, logger
from ai_assistant.utils import capture_image

def send_sos_email(image_path):
    logger.info("Sending SOS email.")
    sender_email = SOSConfig.SENDER_EMAIL
    sender_password = SOSConfig.SENDER_PASSWORD
    recipient_email = SOSConfig.RECIPIENT_EMAIL
    subject = "SOS Alert: User Image"
    body = "An SOS alert has been triggered. See the attached image for more details."

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Capture an image from the webcam
    image_path = capture_image()
    with open(image_path, "rb") as f:
        img_data = f.read()
    image = MIMEImage(img_data, name="user_image.jpg")
    msg.attach(image)

    # Send the email
    with smtplib.SMTP(SOSConfig.SMTP_SERVER, SOSConfig.SMTP_PORT) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)