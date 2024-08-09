# AI Assistant

## Overview
This AI assistant project helps with daily chores, voice authentication, object detection, information retrieval, and sending SOS emails. It uses a variety of APIs and machine learning models to provide these functionalities.

## Project Structure

```sh
Canopus/
├── ai_assistant/
│ ├── init.py
│ ├── voice_auth.py
│ ├── object_detection.py
│ ├── sos_command.py
│ ├── code_generation.py
│ ├── information_retrieval.py
│ └── utils.py
├── config/
│ └── config.py
├── models/
│ ├── deploy.prototxt
│ └── mobilenet.caffemodel
├── logs/
│ └── ai_assistant.log
├── main.py
├── requirements.txt
└── README.md
````


## Setup

1. **Clone the Repository**: Clone the repository from GitHub or download the project files.
   ```sh
   git clone https://github.com/Gamecooler19/Canopus-Assistant.git
   cd ai_assistant
   ```
2. **Create and Activate Virtual Environment**:
    ```sh
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```
3. **Run the Main Script**:
   ```sh
   python main.py
   ```
   
## Configuration
The configuration settings are stored in config/config.py. Adjust the settings as needed.

## Logging
Logs are stored in logs/ai_assistant.log.

## Modules
- **Voice Authentication** :
Handles voice authentication using Euclidean distance between MFCC features.

- **Object Detection** :
Detects objects using a pre-trained MobileNet model and retrieves information using Google Gemini API.

- **SOS Command** :
Captures an image and sends an SOS email with the user's image.

- **Code Generation** :
Generates code using a provided API.

- **Information Retrieval** :
Retrieves information about objects using Google Gemini API.

- **Contributing** :
Feel free to contribute by submitting a pull request or opening an issue.

## License
- [Unlicensed License](LICENSE)
