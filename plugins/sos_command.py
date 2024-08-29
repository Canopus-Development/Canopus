import cv2
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from config.config import SOSConfig, logger
from plugins.utils import capture_image

def send_sos_email(image_path):
    logger.info("Sending SOS email.")
    sender_email = SOSConfig.SENDER_EMAIL
    sender_password = SOSConfig.SENDER_PASSWORD
    recipient_email = SOSConfig.RECIPIENT_EMAIL
    subject = "Subject: SOS - Urgent Assistance Required! 🚨"
    body = f"Dear Pradyumn Tandon,\n\nI hope this email finds you in good health and spirits. I am writing to you as your AI-powered assistant, tasked with monitoring and  managing various aspects of your life. Unfortunately, I have some distressing news to share with you. \n\nAs you may be aware, Pradyumn has been experiencing some cognitive difficulties lately. These challenges have significantly impacted their daily functioning, including their ability to manage their finances, maintain their living space, and engage in social activities. I have tried my best to support them, but the situation is becoming increasingly dire.\n\nI am reaching out to you as a close relative for urgent assistance. I kindly request your presence at Pradyumn's residence as soon as possible to help address this crisis. Your support and guidance are crucial in ensuring their well-being and safety. \n\nPlease let me know if you can arrive within the next 24 hours, so we can make arrangements for your visit. I will provide you with all the necessary details and information upon your arrival. \n\nThank you for your prompt attention to this matter. I am confident that together, we can find a suitable solution for Pradyumn's benefit. \n\nWarm regards,\nCanopus 🤖"

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