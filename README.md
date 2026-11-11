<div align="center">

# ✦ ELARA AI & OS

### **Enhanced Learning And Researching Assistant**

**An AI-powered desktop assistant combining intelligence, voice, vision, automation, and an OS-style interface.**

[![Python](https://img.shields.io/badge/Python-Desktop%20Project-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![AI](https://img.shields.io/badge/AI-Hybrid%20Architecture-7C3AED?style=for-the-badge)](#-ai-intelligence)
[![Voice](https://img.shields.io/badge/Voice-Assistant-0EA5E9?style=for-the-badge)](#-voice--wake-system)
[![Vision](https://img.shields.io/badge/Vision-OCR%20%7C%20Screen%20Analysis-0F766E?style=for-the-badge)](#-vision--screen-intelligence)
[![Status](https://img.shields.io/badge/Status-Active%20Development-orange?style=for-the-badge)](#-project-status)

**Developed by [Sparsh Saxena](https://github.com/saxenasparsh421-sketch)**

[GitHub Repository](https://github.com/saxenasparsh421-sketch/ELARA-AI-OS) · [Official Website](https://saxenasparsh421-sketch.github.io/elara-ai-os-website/)

</div>

---

## ✧ About ELARA

**ELARA AI & OS** is a Python-based desktop assistant project designed to bring multiple AI-powered capabilities together in one environment. It combines voice interaction, an AI brain, command routing, computer vision, automation, a desktop dashboard, maps, skills, plugins, and device-related components.

The project is being developed as a modular assistant that can work with configured online AI services as well as local AI components. Its long-term direction is to provide a unified assistant experience across desktop, vision, navigation, automation, and connected devices.

> **Project idea:** One assistant. Multiple capabilities. A smarter desktop experience.

## ✦ Table of Contents

- [AI Intelligence](#-ai-intelligence)
- [Voice & Wake System](#-voice--wake-system)
- [Vision & Screen Intelligence](#-vision--screen-intelligence)
- [Desktop Control & Automation](#-desktop-control--automation)
- [Sleep-Time Security & Motion Detection](#-sleep-time-security--motion-detection)
- [Gesture Interface & 3D Interaction](#-gesture-interface--3d-interaction)
- [Dashboard, GUI & Chat](#-dashboard-gui--chat)
- [ELARA Maps & Location](#-elara-maps--location)
- [Web & Developer Tools](#-web--developer-tools)
- [Phone & Device Components](#-phone--device-components)
- [Privacy, Configuration & Security](#-privacy-configuration--security)
- [Architecture & Project Structure](#-architecture--project-structure)
- [Installation & Setup](#-installation--setup)
- [Project Status](#-project-status)
- [Roadmap](#-roadmap)
- [Developer](#-developer)

## 🧠 AI Intelligence

ELARA is designed around a configurable AI layer that can connect to different model providers and local inference components.

- **Hybrid AI approach** — cloud-based AI services alongside local AI components, depending on configuration.
- **OpenRouter integration** — access to supported models through the OpenRouter API.
- **OpenAI API support** — provider integration through API configuration.
- **Ollama integration** — support for connecting to locally hosted models.
- **AI brain service** — a dedicated service responsible for generating assistant responses.
- **Natural-language question answering** — ask questions and receive AI-generated responses.
- **Context-aware conversations** — conversational interaction through the assistant and chat components.
- **Research and learning assistance** — an assistant workflow for information, explanations, and learning-related queries.
- **Zero-click / low-friction Q&A concept** — a streamlined question-answering experience intended to reduce unnecessary interface steps.
- **Provider flexibility** — the available model and online/offline behavior depend on the configured provider and installed model.

## 🎙️ Voice & Wake System

ELARA includes a voice-oriented assistant loop and supporting speech components.

- Voice-based interaction with the assistant.
- Speech-to-text (STT) input.
- Text-to-speech (TTS) responses.
- Wake-word / voice-listening workflow.
- **Double-clap listener** for activating the assistant workflow.
- Background listener support through the clap-listener startup flow.
- Voice command recognition and command routing.
- Spoken assistant responses.
- Pause and resume controls.
- Standby mode and standby exit workflow.
- Global hotkey support for assistant controls.
- Speech and microphone test utilities are included in the repository.

## 👁️ Vision & Screen Intelligence

ELARA's vision-related components are intended to help the assistant work with visual information.

- Optical Character Recognition (OCR).
- Screenshot capture and analysis.
- Image understanding and image-based question answering.
- Screen-content analysis.
- Live screen-understanding capability (where the relevant module is enabled).
- Visual context extraction for AI-assisted interaction.
- Camera-based input for supported vision and gesture modules.

## ⚙️ Desktop Control & Automation

The project includes separate command and automation components intended to connect natural-language requests with desktop actions.

- Command routing and intent-based command handling.
- Desktop-assistant control workflows.
- Voice-driven laptop operations (for supported commands and configured permissions).
- GUI-connected assistant interactions.
- Automation modules for supported tasks.
- OS-style assistant background workflow.
- Pause, resume, and standby controls.
- Expandable command, skill, and plugin architecture.

> Available actions depend on the operating system, installed dependencies, enabled modules, and permissions granted by the user.

## 🌙 Sleep-Time Security & Motion Detection

ELARA's sleep-time security concept is intended to let a computer act as a user-enabled monitoring station when the user is resting or away.

- **Sleep-Time Monitoring Mode** — a dedicated mode for monitoring during selected rest periods.
- **Motion / Movement Detection** — detect movement within the supported camera or sensor view.
- **Night-Time Activity Monitoring** — observe activity during the enabled monitoring session.
- **Movement Event Awareness** — identify when movement is detected during monitoring.
- **Security Monitoring Workflow** — a separate security-oriented feature area within the project.

**Privacy note:** Monitoring should be enabled deliberately by the device owner, with clear camera/sensor permissions and an appropriate visible indication. Do not use this feature to monitor people without their knowledge or consent. Exact detection, alerting, and recording behavior depends on the implemented security module and its configuration.

## 🖐️ Gesture Interface & 3D Interaction

The repository's existing project description identifies the camera-based floating interface as an **experimental / private-development** feature.

- Camera-based interaction.
- Hand-gesture interaction.
- Floating desktop interface elements.
- Gesture-controlled movement and repositioning.
- Gesture-controlled resizing.
- Touch-free interaction with supported interface elements.
- Experimental 3D / gesture modules.

## 🖥️ Dashboard, GUI & Chat

- ELARA desktop dashboard.
- GUI-based assistant experience.
- Chat interface and assistant conversation flow.
- Saved user and assistant messages through the chat bridge.
- Shared chat storage component.
- Chat-history support for returning to previous conversations (where enabled by the UI/storage module).
- Modular GUI components for future expansion.

## 🗺️ ELARA Maps & Location

- ELARA Maps project components.
- Online and offline map capability as supported by the selected data source.
- PMTiles-based offline map data support (for configured map datasets).
- Satellite-map data catalog.
- Local / home-town map data support.
- Location-related components.
- Expandable navigation and map integration.

Offline map availability depends on the map files and datasets installed locally. Large map datasets are not necessarily included in every source download.

## 🧩 Web & Developer Tools

- AI-assisted website generation.
- Website-building workflow for supported HTML, CSS, and JavaScript outputs.
- AI-assisted coding and development support.
- Research-oriented assistant workflows.
- Modular skills and plugin components.
- Expandable command and service integrations.

## 📱 Phone & Device Components

- Phone-related and device-integration components are present in the repository.
- Device-oriented features can be expanded through the modular architecture.
- Android companion experience is part of the broader project direction / roadmap.

## 🔐 Privacy, Configuration & Security

- Environment-based configuration for API credentials and service settings.
- `.env` support where required by the configured modules.
- `.gitignore` support to help keep local configuration and secrets out of source control.
- Local AI components through supported local providers.
- User-controlled permissions for camera, microphone, screen, and system interactions.
- Sleep-time monitoring and movement detection as described in the security section.
- Encryption and secure data handling should be enabled only for modules that implement them; do not assume every stored item is encrypted by default.

**Important:** Never publish API keys, access tokens, passwords, private datasets, or personal recordings in this repository. Rotate any key that has been accidentally committed.

## 🏗️ Architecture & Project Structure

ELARA is organized into separate modules so capabilities can be maintained and expanded independently.

| Directory / File | Purpose |
|---|---|
| `ai/` | AI-related components |
| `automation/` | Automation workflows |
| `commands/` | Command handling and routing |
| `core/` | Core runtime and kernel components |
| `elara_os/` | ELARA OS and assistant integration components |
| `gui/` | Desktop dashboard and interface |
| `location/` | Location-related components |
| `maps/` | Map and map-data components |
| `phone/` | Phone / device-related components |
| `plugins/` | Plugin integrations |
| `security/` | Security-related components, including the sleep-time monitoring feature area |
| `services/` | Supporting services, including speech and AI brain services |
| `shared/` | Shared components and storage utilities |
| `skills/` | Assistant skills |
| `speech/` | Speech-related components |
| `utils/` | Utility modules |
| `vision/` | Vision and image-related components |
| `assistant.py` | Main assistant controller |
| `main.py` | Application entry point and startup orchestration |
| `clap_listener.py` | Double-clap listener entry point |
| `config.py` | Application configuration |
| `requirements.txt` | Python dependencies |

## 🚀 Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/saxenasparsh421-sketch/ELARA-AI-OS.git
cd ELARA-AI-OS
```

### 2. Create a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure services

Set up the API credentials and local service settings required by the modules you intend to use. Follow the variable names expected by the project's configuration and service files. Keep private credentials in your local environment / `.env` file and never commit them.

### 5. Start ELARA

```bash
python main.py
```

Some features may require additional models, map datasets, device permissions, or optional dependencies. Enable only the components your system supports.

## 💾 Resource & Storage Notes

ELARA can use additional storage for local AI models, offline map tiles, voice assets, and optional dependencies. The project footprint has been estimated at **around 8.5 GB** when larger optional assets are included; the actual size varies with the models, map datasets, and modules installed. This is an approximate project-side estimate, not a fixed minimum requirement.

## 📌 Project Status

ELARA AI & OS is an actively developed project. The repository contains multiple feature areas, test utilities, and experimental components. Not every capability described here should be considered production-ready on every device.

| Status | Meaning |
|---|---|
| **In repository** | A corresponding module, component, or entry point is present in the public repository. |
| **Experimental** | A feature is being tested or is not yet part of the stable everyday workflow. |
| **Configuration-dependent** | Requires a provider key, local model, dataset, permission, or optional dependency. |
| **Roadmap** | A future direction rather than a claim of a completed implementation. |

The camera-based gesture-controlled floating interface is described by the project as experimental / private development. Sleep-time motion monitoring is included in this README as a project feature description; its exact implementation and alert behavior should be checked against the current `security/` source before describing it as production-ready.

## 🧭 Roadmap

- Expand the hybrid online / offline AI experience.
- Improve local model support and resource efficiency.
- Extend voice interaction and background assistant controls.
- Improve live vision and screen-understanding workflows.
- Expand sleep-time monitoring and motion-detection capabilities.
- Develop advanced gesture and 3D interface modules.
- Expand ELARA Maps and offline map coverage.
- Develop the Android companion experience.
- Add more skills, plugins, and device integrations.

## 👨‍💻 Developer

**Sparsh Saxena**  
Project developer — ELARA AI & OS

- GitHub: [@saxenasparsh421-sketch](https://github.com/saxenasparsh421-sketch)
- Repository: [ELARA-AI-OS](https://github.com/saxenasparsh421-sketch/ELARA-AI-OS)
- Official Website: [ELARA AI & OS](https://saxenasparsh421-sketch.github.io/elara-ai-os-website/)

---

<div align="center">

### **ELARA AI & OS**

*Intelligence beyond the interface.*

</div>
