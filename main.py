import speech_recognition as sr
from ai_assistant.voice_auth import VoiceAuthenticator
from ai_assistant.object_detection import ObjectDetector
from ai_assistant.sos_command import send_sos_email
from ai_assistant.code_generation import generate_code
from ai_assistant.information_retrieval import retrieve_information
from ai_assistant.utils import capture_image
from config.config import logger
from TTS.api import TTS

# Initialize TTS
tts_model = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False, gpu=False)

def recognize_speech_from_mic(recognizer, microphone):
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")
    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    try:
        response["transcription"] = recognizer.recognize_google(audio)
    except sr.RequestError:
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        response["error"] = "Unable to recognize speech"

    return response

def speak_text(text):
    tts_model.tts_to_file(text=text, file_path="response.wav")
    os.system("aplay response.wav")

def main():
    logger.info("Starting AI Assistant.")
<<<<<<< Updated upstream
    
=======

>>>>>>> Stashed changes
    voice_authenticator = VoiceAuthenticator()
    voice_authenticator.enroll_user()
    is_authenticated = voice_authenticator.authenticate_user()
    if not is_authenticated:
        logger.error("Voice authentication failed.")
        speak_text("Voice authentication failed.")
        return

    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    speak_text("Voice assistant is now active. Please speak your command.")

    while True:
        speak_text("Listening for command...")
        command_response = recognize_speech_from_mic(recognizer, microphone)

        if not command_response["success"]:
            speak_text("I didn't catch that. What did you say?")
            continue

        user_command = command_response["transcription"].strip().lower()
        speak_text(f"Recognized command: {user_command}")

        if user_command == 'exit':
            logger.info("Exiting AI Assistant.")
            speak_text("Exiting AI Assistant.")
            break
        elif 'detect object' in user_command:
            object_detector = ObjectDetector()
            object_info = object_detector.detect_objects()
            if object_info:
                logger.info(f"Object information: {object_info}")
                speak_text(f"Object information: {object_info}")
            else:
                speak_text("No object detected or failed to retrieve information.")
        elif 'generate code' in user_command:
            speak_text("Please speak the prompt for code generation:")
            prompt_response = recognize_speech_from_mic(recognizer, microphone)
            prompt = prompt_response["transcription"]
            if not prompt:
                speak_text("Failed to recognize the prompt for code generation.")
                continue
            code = generate_code(prompt)
            if code:
                logger.info(f"Generated code: {code}")
                speak_text(f"Generated code:\n{code}")
            else:
                speak_text("Failed to generate code.")
        elif 'retrieve information' in user_command:
            speak_text("Please speak the query for information retrieval:")
            query_response = recognize_speech_from_mic(recognizer, microphone)
            query = query_response["transcription"]
            if not query:
                speak_text("Failed to recognize the query for information retrieval.")
                continue
            info = retrieve_information(query)
            if info:
                logger.info(f"Retrieved information: {info}")
                speak_text(f"Retrieved information:\n{info}")
            else:
                speak_text("Failed to retrieve information.")
        elif 'sos' in user_command:
            image_path = capture_image()
            if image_path:
                send_sos_email(image_path)
                speak_text("SOS email sent successfully.")
            else:
                speak_text("Failed to capture image.")
        else:
            speak_text("Invalid command. Please try again.")

if __name__ == "__main__":
    main()
