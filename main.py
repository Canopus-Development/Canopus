# main.py
import os
import importlib
import speech_recognition as sr
import pyttsx3
import webbrowser
import subprocess
from config.config import logger

WAKE_UP_WORD = "canopus"

# Initialize the pyttsx3 engine
engine = pyttsx3.init()

def speak_text(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

def recognize_speech_from_mic(recognizer, microphone):
    """
    Capture speech from the microphone and transcribe it.

    Args:
        recognizer (sr.Recognizer): An instance of Recognizer.
        microphone (sr.Microphone): An instance of Microphone.

    Returns:
        dict: A dictionary containing success status, error message, and transcription.
    """
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
    """Append the response to a text file."""
    with open("responses.txt", "a") as f:
        f.write(response + "\n")

def open_application_or_website(command):
    """
    Open an application or website based on the command.

    Args:
        command (str): The user's command.

    Returns:
        str: Response message.
    """
    if "open" in command:
        if "website" in command:
            url = command.split("open website ")[-1].strip()
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "https://" + url  # Ensure the URL has a proper scheme
            webbrowser.open(url)
            return f"Opening website {url}"
        else:
            app = command.split("open ")[-1].strip()
            try:
                subprocess.Popen(app)
                return f"Opening application {app}"
            except FileNotFoundError:
                return f"Application {app} not found. Please check the application name or path."
            except Exception as e:
                return f"Failed to open application {app}: {e}"
    return "Invalid command for opening application or website."

def load_plugins():
    """
    Dynamically load all plugins from the plugins directory.

    Returns:
        tuple: A tuple containing a list of general plugins and the chatter plugin.
    """
    plugins = []
    chatter_plugin = None
    plugin_dir = os.path.join(os.path.dirname(__file__), "plugins")

    if not os.path.isdir(plugin_dir):
        logger.error(f"Plugins directory not found at {plugin_dir}")
        return plugins, chatter_plugin

    for filename in os.listdir(plugin_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            plugin_name = filename[:-3]
            try:
                module = importlib.import_module(f"plugins.{plugin_name}")
                if hasattr(module, "execute"):
                    if plugin_name.lower() == "chatter":  # Identify the chatter plugin by name
                        chatter_plugin = module
                        logger.info(f"Loaded chatter plugin: {plugin_name}")
                        print(f"Loaded chatter plugin: {plugin_name}")
                    else:
                        plugins.append(module)
                        logger.info(f"Loaded plugin: {plugin_name}")
                        print(f"Loaded plugin: {plugin_name}")
                else:
                    logger.warning(f"Plugin {plugin_name} does not have an execute method.")
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_name}: {e}")

    return plugins, chatter_plugin

def process_commands():
    """
    Main loop to process voice commands using loaded plugins.
    """
    logger.info("Processing commands.")
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    try:
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
    except Exception as e:
        logger.error(f"Error initializing microphone: {e}")
        speak_text("Failed to initialize the microphone. Please check your microphone settings.")
        return

    # Load plugins dynamically
    general_plugins, chatter_plugin = load_plugins()

    running = True  # Flag to control the main loop

    while running:
        # Listen for the wake-up word
        logger.info("Listening for the wake-up word...")
        speak_text("Waiting for wake-up word.")

        while True:
            wake_word_response = recognize_speech_from_mic(recognizer, microphone)

            if wake_word_response["transcription"]:
                user_input = wake_word_response["transcription"].strip().lower()
                logger.info(f"Wake-up word detected: {user_input}")

                if WAKE_UP_WORD in user_input:
                    speak_text(f"{WAKE_UP_WORD} activated. Please speak your command.")
                    break  # Exit the loop to start processing commands
                else:
                    speak_text("Waiting for the wake-up word.")

        command_executed = False

        while not command_executed and running:
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
            logger.info(f"User command: {user_command}")

            if user_command == 'exit':
                logger.info("Exiting AI Assistant.")
                speak_text("Exiting AI Assistant.")
                running = False  # Set flag to False to exit the outer loop
                command_executed = True
                break  # Exit the inner loop

            # Attempt to execute the command with the loaded general plugins
            command_handled = False
            for plugin in general_plugins:
                if hasattr(plugin, "execute"):
                    try:
                        response = plugin.execute(user_command)
                        if response:
                            speak_text(response)
                            save_response_to_file(response)
                            command_handled = True
                            # Continue to allow multiple plugins to handle the command if needed
                    except Exception as e:
                        logger.error(f"Error executing plugin {plugin.__name__}: {e}")

            if not command_handled and chatter_plugin:
                # Use the chatter plugin as a fallback
                try:
                    response = chatter_plugin.execute(user_command)
                    if response:
                        speak_text(response)
                        save_response_to_file(response)
                except Exception as e:
                    logger.error(f"Error executing chatter plugin: {e}")

            elif not command_handled and not chatter_plugin:
                speak_text("Sorry, I didn't understand the command. Please try again or install additional plugins.")
                logger.info(f"Command not found: {user_command}")
                logger.info("Please try again or install additional plugins.")

            command_executed = True  # Proceed to the next command cycle

def main():
    """Entry point for the AI Assistant."""
    logger.info("Starting AI Assistant.")

    try:
        # Start the command processing loop
        process_commands()
    except KeyboardInterrupt:
        logger.info("AI Assistant terminated by user.")
        speak_text("AI Assistant terminated. Goodbye!")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        speak_text("An unexpected error occurred. Please check the logs for more details.")

if __name__ == "__main__":
    main()
