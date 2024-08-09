import speech_recognition as sr
import time
from ai_assistant.voice_auth import VoiceAuthenticator
from ai_assistant.object_detection import ObjectDetector
from ai_assistant.sos_command import send_sos_email
from ai_assistant.code_generation import generate_code
from ai_assistant.information_retrieval import retrieve_information
from ai_assistant.utils import capture_image
from config.config import logger
import os
from mozilla_voice_tts import tts



# Initialize TTS engine
tts_engine = tts.Mozilla_TTS(tts_type='wav')

def main():
    logger.info("Starting AI Voice Assistant.")

    # Voice Authentication
    voice_authenticator = VoiceAuthenticator()
    voice_authenticator.enroll_user()
    is_authenticated = voice_authenticator.authenticate_user()
    if not is_authenticated:
        logger.error("Voice authentication failed.")
        return

    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    wake_word = "Canopus"  # Replace with your desired wake word

    while True:
        print("Listening for wake word...")
        command_response = recognize_speech_from_mic(recognizer, microphone)

        if command_response.get("success"):
            user_command = command_response.get("transcription", "").strip().lower()
            if wake_word in user_command:
                tts_engine.tts_to_file(f"I am fine. {wake_word.capitalize()} is now active. Please speak your command.", "response.wav")
                os.system("play response.wav")

                while True:
                    print("Listening for command...")
                    command_response = recognize_speech_from_mic(recognizer, microphone)

                    if command_response.get("success"):
                        user_command = command_response.get("transcription", "").strip().lower()
                        print(f"Recognized command: {user_command}")
                    else:
                        print("Failed to recognize the command.")
                        continue

                    if user_command == 'exit':
                        logger.info("Exiting AI Voice Assistant.")
                        break

                    # Capture Image
                    print("Capturing image...")
                    capture_image()
                    logger.info("Image captured. timestamp: " + str(time.time()))

                    # Object Detection
                    if 'detect object' in user_command:
                        object_detector = ObjectDetector()
                        object_info = object_detector.detect_objects()
                        if object_info:
                            logger.info(f"Object information: {object_info}")
                            tts_engine.tts_to_file(f"Object information: {object_info}", "response.wav")
                            os.system("play response.wav")
                        else:
                            tts_engine.tts_to_file("No object detected or failed to retrieve information.", "response.wav")
                            os.system("play response.wav")

                    # Code Generation
                    elif 'generate code' in user_command:
                        tts_engine.tts_to_file("Please speak the prompt for code generation:", "response.wav")
                        os.system("play response.wav")
                        prompt_response = recognize_speech_from_mic(recognizer, microphone)
                        prompt = prompt_response.get("transcription", "")
                        if not prompt:
                            tts_engine.tts_to_file("Failed to recognize the prompt.", "response.wav")
                            os.system("play response.wav")
                            continue

                        generated_code = generate_code(prompt)
                        if generated_code:
                            tts_engine.tts_to_file(f"Generated code: {generated_code}", "response.wav")
                            os.system("play response.wav")
                        else:
                            tts_engine.tts_to_file("Failed to generate code.", "response.wav")
                            os.system("play response.wav")
                            time.sleep(300)  # Hold back for 5 minutes

                    # Information Retrieval
                    elif 'retrieve information' in user_command:
                        tts_engine.tts_to_file("Please speak the topic for information retrieval:", "response.wav")
                        os.system("play response.wav")
                        topic_response = recognize_speech_from_mic(recognizer, microphone)
                        topic = topic_response.get("transcription", "")
                        if not topic:
                            tts_engine.tts_to_file("Failed to recognize the topic.", "response.wav")
                            os.system("play response.wav")
                            continue

                        information = retrieve_information(topic)
                        if information:
                            logger.info(f"Information retrieved: {information}")
                            tts_engine.tts_to_file(f"Information retrieved: {information}", "response.wav")
                            os.system("play response.wav")
                        else:
                            tts_engine.tts_to_file("Failed to retrieve information.", "response.wav")
                            os.system("play response.wav")

                    # SOS Command
                    elif 'sos' in user_command:
                        send_sos_email()
                        tts_engine.tts_to_file("SOS email sent.", "response.wav")
                        os.system("play response.wav")

                    else:
                        tts_engine.tts_to_file("Invalid command.", "response.wav")
                        os.system("play response.wav")

                    print("Sleeping...")
                    time.sleep(5)  # Sleep for 5 seconds before listening for wake word again

def recognize_speech_from_mic(recognizer, microphone):
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        transcription = recognizer.recognize_google(audio)
        return {"success": True, "transcription": transcription}
    except sr.UnknownValueError:
        return {"success": False}

if __name__ == "__main__":
    main()
