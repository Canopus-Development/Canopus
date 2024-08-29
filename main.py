import os
import importlib
import speech_recognition as sr
import pyttsx3
from config.config import logger
import webbrowser
import subprocess

# Constant
WAKE_UP_WORD = "canopus"

# Initialize the pyttsx3 engine
engine = pyttsx3.init()

def speak_text(text):
    engine.say(text)
    engine.runAndWait()

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
        response["transcription"] = recognizer.recognize_google(audio, language="en-IN")
    except sr.RequestError:
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        response["error"] = "Unable to recognize speech"

    return response

def save_response_to_file(response):
    with open("responses.txt", "a") as f:
        f.write(response + "\n")

def open_application_or_website(command):
    if "open" in command:
        if "website" in command:
            url = command.split("open website ")[-1]
            webbrowser.open(url)
            return f"Opening website {url}"
        else:
            app = command.split("open ")[-1]
            subprocess.Popen(app)
            return f"Opening application {app}"
    return "Invalid command for opening application or website."

def load_plugins():
    plugins = {}
    plugin_dir = os.path.join(os.path.dirname(__file__), "plugins")

    for filename in os.listdir(plugin_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            plugin_name = filename[:-3]
            try:
                module = importlib.import_module(f"ai_assistant.{plugin_name}")
                if hasattr(module, "execute"):
                    plugins[plugin_name] = module
                    logger.info(f"Loaded plugin: {plugin_name}")
                else:
                    logger.warning(f"Plugin {plugin_name} does not have an execute method.")
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_name}: {e}")

    return plugins

def main():
    logger.info("Starting AI Assistant.")

    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    # Load plugins dynamically
    plugins = load_plugins()

    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)

    while True:
        logger.info("Listening for the wake-up word.")
        command_response = recognize_speech_from_mic(recognizer, microphone)

        if not command_response["success"]:
            continue

        transcription = command_response["transcription"]
        if transcription is None:
            continue

        user_command = transcription.strip().lower()
        if WAKE_UP_WORD not in user_command:
            continue

        speak_text("Canopus is now active. Please speak your command.")
        command_executed = False

        while not command_executed:
            logger.info("Listening for command...")
            command_response = recognize_speech_from_mic(recognizer, microphone)

            if not command_response["success"]:
                speak_text("I didn't catch that. What did you say?")
                continue

            user_command = command_response["transcription"]
            if user_command is None:
                speak_text("Sorry, I didn't understand that. Please try again.")
                continue

            user_command = user_command.strip().lower()

            if user_command == 'exit':
                logger.info("Exiting AI Assistant.")
                speak_text("Exiting AI Assistant.")
                command_executed = True
                break

            elif 'open' in user_command:
                response = open_application_or_website(user_command)
                speak_text(response)
                save_response_to_file(response)
            else:
                plugin_executed = False
                for plugin_name, plugin in plugins.items():
                    if hasattr(plugin, "execute"):
                        try:
                            response = plugin.execute(user_command)
                            if response:
                                speak_text(response)
                                save_response_to_file(response)
                                plugin_executed = True
                                break
                        except Exception as e:
                            logger.error(f"Error executing plugin {plugin_name}: {e}")

                if not plugin_executed:
                    speak_text("Sorry, I didn't understand the command. Please try again or install additional plugins.")

            command_executed = True

        speak_text("Canopus is now going to sleep. Say the wake-up word to activate again.")
        logger.info("Canopus is now sleeping.")

if __name__ == "__main__":
    main()
