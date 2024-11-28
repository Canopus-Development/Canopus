# plugins/sos.py
from plugins.utils import capture_image
from config.config import EmailConfig, logger
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

def execute(user_command):
    logger.info("Executing SOS plugin.")
    # Define keywords that trigger the SOS plugin
    sos_commands = ["send sos", "help me", "emergency"]

    if any(cmd in user_command.lower() for cmd in sos_commands):
        try:
            sender_email = EmailConfig.SENDER_EMAIL
            sender_password = EmailConfig.SENDER_PASSWORD
            recipient_email = EmailConfig.RECIPIENT_EMAIL
            subject = "SOS - Urgent Assistance Required! 🚨"
            body = "Dear Pradyumn Tandon,\n\nI hope this email finds you in good health and spirits..."  # Trimmed for brevity

            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = recipient_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            image_path = capture_image()
            with open(image_path, "rb") as f:
                img_data = f.read()
            image = MIMEImage(img_data, name="user_image.jpg")
            msg.attach(image)

            with smtplib.SMTP(SOSConfig.SMTP_SERVER, SOSConfig.SMTP_PORT) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)

            return "SOS email sent successfully."
        except Exception as e:
            logger.error(f"Error in SOS plugin: {str(e)}")
            return "An error occurred while sending the SOS email."
    else:
        logger.info("No SOS command detected.")
        return None  # Return None if not handling the command
