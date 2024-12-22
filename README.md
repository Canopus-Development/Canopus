# Canopus - A Professional AI-Driven Voice Assistant for Developers

Canopus is a cutting-edge, voice-powered AI assistant designed to streamline software development and project management processes through intuitive and efficient natural language interfaces.

## Features

### Core Development Capabilities
- **Intelligent Code Navigation and Semantic Search**  
  Quickly locate classes, functions, and references using natural language requests.
- **On-Demand Code Review and Static Analysis**  
  Receive immediate feedback on code quality, potential errors, and optimization tips.
- **Automated Documentation**  
  Generate and maintain comprehensive documentation for classes, functions, and modules.
- **Debugging Assistance**  
  Analyze exceptions, suggest potential fixes, and track error histories.
- **Performance Monitoring**  
  Continuously monitor critical system metrics (CPU, memory, etc.) for proactive optimization.
- **Dependency and Security Checks**  
  Identify outdated libraries and known vulnerabilities to maintain a secure environment.
- **Project & Task Automation**  
  Efficiently manage tasks and projects, integrating seamlessly with CI/CD pipelines.

### AI Capabilities
- **Advanced Speech Recognition**  
  Leverages noise reduction and Voice Activity Detection to enhance transcription accuracy.
- **Natural Language Understanding (NLU)**  
  Interprets user requests and maps them to development-related commands.
- **Multimodal AI Integration**  
  Configurable with GPT-4, LLaMA, Cohere, and other models for diverse tasks.
- **Visual Search & Image Analysis**  
  Uses image-based recognition (e.g., Azure Computer Vision) to enable visual context search.

### IDE Integration
- **Supported IDEs**  
  Seamless integration with VSCode, PyCharm, and Atom for quick file navigation.
- **In-IDE Code Actions**  
  Open files, locate symbols, and perform code completion directly from your voice commands.
- **Built-In Documentation Lookup**  
  Retrieve relevant documentation snippets and references within your IDE.

### Development Tools
- **Automated Testing & Coverage**  
  Instantly run tests and generate coverage reports to maintain code quality.
- **Git Workflow Management**  
  Perform version control operations (commit, push, pull) with spoken commands.
- **Workspace Monitoring & Indexing**  
  Continuously index your workspace for faster search and insights.
- **Performance Profiling & Optimization**  
  Track resource utilization and identify bottlenecks with integrated profiling tools.

## Prerequisites

- **Python 3.8+**  
  The application is tested and maintained for Python 3.8 and above.
- **Azure AI Services Account**  
  Required for advanced AI features (computer vision, LLM inference, etc.).
- **Development Environment**  
  VSCode, PyCharm, or Atom installations recommended but not strictly required.
- **Microphone**  
  Essential for voice input functionality.
- **Git**  
  Necessary for version control commands and project management.

### Audio Setup

For Linux users, ensure ALSA and PulseAudio are properly configured:

```bash
# Install required packages
sudo apt-get install pulseaudio alsa-utils portaudio19-dev

# Configure ALSA
sudo modprobe snd-aloop
sudo usermod -aG audio $USER

# Test audio setup
arecord -l  # List recording devices
```

Create or edit `/etc/asound.conf`:
```
pcm.!default {
    type pulse
    fallback "sysdefault"
    hint {
        show on
        description "Default ALSA Output (PulseAudio Sound Server)"
    }
}

ctl.!default {
    type pulse
    fallback "sysdefault"
}
```

## Installation

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/Canopus-Development/Canopus.git
   cd Canopus
   ```

2. **Create and Activate a Virtual Environment**  
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install Dependencies and Language Model**  
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

4. **Configure Environment Variables**  
   ```bash
   cp .env.example .env
   # Update .env with your Azure keys and other configurations
   ```

## Project Structure

```
Canopus/
├── input/                   # Input handling modules
│   ├── stt.py              # Speech-to-text with noise reduction & VAD
├── processing/             # Core logic for command processing
│   ├── nlu.py             # Natural Language Understanding
│   ├── dispatcher.py      # Command dispatcher with plugin loading
├── modules/               # Core functionality modules
│   ├── code_search.py     # Semantic code search
│   ├── code_reviewer.py   # Automated code analysis
│   ├── debug_assistant.py # Debugging support and error tracking
│   ├── doc_generator.py   # Documentation generation for Python modules
│   └── ...                # Additional modules
├── plugins/               # Plugin system for extensibility
├── output/                # Output handling (TTS, logs, etc.)
├── utils/                 # Utility functions (logging, config, etc.)
└── config/                # Configuration files and environment settings
```

## Usage

Launch Canopus from the terminal:
```bash
python main.py
```

### Common Voice Commands

- **Code Navigation**  
  "Hey Canopus, find references to ‘UserController’."
- **Code Review**  
  "Hey Canopus, review file ‘main.py’."
- **Documentation**  
  "Hey Canopus, generate docs for the ‘auth’ module."
- **Debugging**  
  "Hey Canopus, debug the last error."
- **System Status**  
  "Hey Canopus, show system metrics."
- **Dependencies**  
  "Hey Canopus, check dependencies."

## Plugin System

Extend Canopus to suit your project needs:

1. **Create a Plugin File** in `plugins/` to implement new functionalities.  
2. **Implement the BasePlugin Interface** for seamless integration.  
3. **Register Commands** in your plugin module.  
4. **Restart Canopus** to load new plugins automatically.

## Configuration

Configure Canopus in `config/settings.json` for:

- **AI Model Selection** (GPT-4, LLaMA, Cohere, etc.)  
- **IDE & Workspace Path**  
- **Voice Settings** (input, output, language)  
- **Plugin Activation**  
- **Logging Levels & Options**

## Development

### Adding or Modifying Features

1. Choose an existing module or create a new plugin.  
2. Implement or extend functionalities.  
3. Add tests in the `tests/` directory to validate features.  
4. Update this README or project documentation as needed.

### Testing

Run automated tests:
```bash
pytest tests/
```

## Contributing

1. **Fork the Repository** and clone it locally.  
2. **Create a New Feature Branch**:
   ```bash
   git checkout -b feature-name
   ```
3. **Commit Your Changes**:
   ```bash
   git commit -m "Implement new feature"
   ```
4. **Push to Your Fork**:
   ```bash
   git push origin feature-name
   ```
5. **Open a Pull Request** on the main repository.

## License

This project is licensed under the Canopus License(DAOSL v2). See [LICENSE](LICENSE) for complete details.

## Acknowledgments

- **OpenAI** for GPT-based models.  
- **Azure AI Services** for advanced computer vision and LLM services.  
- **Hugging Face** for the Whisper speech recognition tools.  
- **Community Contributors** for continuous improvements and feedback.

---
