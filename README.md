# Canopus - AI Voice Assistant

Canopus is a voice-activated AI assistant that can handle various tasks through voice commands. It uses Azure AI services for natural language processing and various other AI capabilities.

## Features

- Voice activation with customizable wake word
- Object detection and image description
- Information retrieval
- Code generation
- Emergency SOS system
- Natural conversation capabilities

## Prerequisites

- Python 3.8+
- Microphone access
- Camera access (for object detection and SOS)
- Azure AI account
- Environment variables setup

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Canopus-Development/Canopus.git
   cd Canopus
   ```

2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the main application:
   ```bash
   python main.py
   ```

---

## Usage

Once installed, you can interact with Canopus using voice commands via the terminal. The default plugins include capabilities for:

- **Code generation** (`code_generation.py`)
- **Object detection** (`object_detection.py`)
- **Chatbot functionalities** (`chat.py`)
- **Voice authentication** (`voice_auth.py`)
- **Spotify control** (`spotify_service.py`)
- **SOS commands** (`sos_command.py`)
- **Information retrieval** (`information_retrieval.py`)

You can trigger these by specifying the appropriate commands through the Canopus CLI interface.

For additional functionality, you can install more plugins directly from our [website](https://canopus.software).

---

## Plugins

Canopus is built to be highly extensible through its plugin system. By adding or modifying plugins, users can customize Canopus to meet their specific needs.

### Pre-installed Plugins

The following plugins are included with Canopus out-of-the-box:

- **voice_auth.py**: Handles secure voice-based authentication.
- **object_detection.py**: Utilizes AI models to detect objects from input sources.
- **sos_command.py**: Sends urgent notifications or executes critical commands.
- **code_generation.py**: Assists with generating code snippets based on user input.
- **information_retrieval.py**: Retrieves information from web or local repositories.
- **spotify_service.py**: Integrates with Spotify for music control via voice commands.
- **chat.py**: Provides a simple chatbot interaction service.
- **utils.py**: Contains utility functions to support the plugins.

### Additional Plugins

More plugins can be added through our official [plugin repository](https://github.com/Canopus-Development/Canopus-Plugins). Users can browse, download, and install plugins to extend Canopus' functionality based on their specific needs.

### Creating a Custom Plugin

1. Navigate to the `plugins/` directory:
   ```bash
   cd plugins
   ```

2. Create a new plugin, for example `my_custom_plugin.py`, and define your custom logic:
   ```python
   def execute_command(args):
       # Custom logic here
       print("Executing custom command")
   ```

3. Register your plugin within the Canopus framework by adding it to the `config/config.py` file.

---

## Project Structure

The following is the structure of the Canopus project directory:

```
Canopus/
├── plugins/                       # Contains all pre-installed and custom plugins
│   ├── init.py                    # Initialization and registration logic
│   ├── voice_auth.py              # Plugin for voice authentication
│   ├── object_detection.py        # Plugin for object detection
│   ├── sos_command.py             # Plugin for SOS emergency commands
│   ├── code_generation.py         # Plugin for AI code generation
│   ├── information_retrieval.py   # Plugin for information retrieval
│   ├── spotify_service.py         # Plugin to control Spotify services
│   ├── chat.py                    # Plugin for chatbot functionalities
│   └── utils.py                   # Utilities and helper functions for plugins
├── config/
│   └── config.py                  # Configuration file for plugin registration
├── models/                        # Pre-trained models and AI components (e.g., object detection models)
├── main.py                        # Entry point of the application
├── requirements.txt               # Dependencies and packages required for Canopus
└── README.md                      # Project documentation
```

---

## Contributing

We welcome contributions to **Canopus**! If you would like to contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request, detailing the changes you have made.

Please ensure your code adheres to the project’s coding standards and includes appropriate tests.

For more details, please refer to our [Code of Conduct](#code-of-conduct).

---

## License

This project is licensed under the **Developer Assistant Open Source License (DAOSL v2.0)**. For more details, please refer to the [LICENSE](LICENSE) file.

---

## Code of Conduct

All participants in this project are expected to follow our **Code of Conduct**. The goal of this Code of Conduct is to ensure a respectful, inclusive, and productive environment for everyone involved.

Please review the full [Code of Conduct](CODE_OF_CONDUCT.md) to understand our standards and expectations.

---
