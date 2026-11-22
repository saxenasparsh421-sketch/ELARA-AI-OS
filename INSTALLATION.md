ELARA — Installation Guide

This guide explains how to download the ELARA source code and prepare its Python environment on Windows and Android Termux.

1. Platform Support

Platform| Status
Windows 10 / 11| Primary development target
Android Termux| Experimental — source setup only
Linux| Experimental
macOS| Experimental

The desktop application uses GUI, desktop-control, and Windows-specific components. Termux does not currently have a verified full desktop installation path.

2. Prerequisites

Windows

Install the following:

- Git
- Python
- Windows 10 or Windows 11
- Internet connection

Verify the installations in Command Prompt:

git --version
python --version

If either command is not recognised, install the missing program and reopen the terminal.

Android Termux

Install and open Termux, then update its package index:

pkg update && pkg upgrade

Install Git and Python:

pkg install git python

Verify:

git --version
python --version

3. Download ELARA

The following command downloads the public repository.

Windows — Command Prompt / PowerShell

git clone https://github.com/saxenasparsh421-sketch/ELARA-AI-OS.git

Enter the project directory:

cd ELARA-AI-OS

Android — Termux

git clone https://github.com/saxenasparsh421-sketch/ELARA-AI-OS.git

Enter the project directory:

cd ELARA-AI-OS

4. Create a Python Virtual Environment

A virtual environment keeps project packages separate from the system Python installation.

Windows — Command Prompt

python -m venv .venv

Activate it:

.venv\Scripts\activate.bat

Windows — PowerShell

python -m venv .venv

Activate it:

.venv\Scripts\Activate.ps1

Android — Termux

python -m venv .venv

Activate it:

source .venv/bin/activate

5. Dependency Installation

ELARA's current public "requirements.txt" is empty. It does not yet provide a complete, verified list of dependencies required by the application.

For this reason, a complete dependency installation command is not provided here. Installing an incomplete or unverified package list may cause import errors or runtime failures.

A verified dependency file will be required before a clean installation can be considered ready.

6. Running ELARA

Windows: The desktop application is the primary target, but a clean installation and full startup test are still required before a reliable launch command can be published.

Termux: The current repository does not provide a verified Android-compatible version of the full desktop interface. Cloning the repository and preparing a Python environment does not mean the Windows desktop application can run on Android.

Do not treat "python main.py" as a verified Termux launch command.

7. Termux Compatibility Notes

Termux provides a Linux-like command-line environment on Android. However, it is not equivalent to a Windows desktop environment.

The current ELARA source contains components that depend on desktop GUI functionality and Windows-specific APIs.

A separate Android-compatible command-line mode would need to be developed and tested before full Termux support can be announced.

8. API Configuration and Security

Some ELARA features require external AI or other service credentials.

- Keep API keys private.
- Store credentials in local environment configuration.
- Never upload ".env" files containing real credentials.
- Never publish passwords, access tokens, or personal data.
- Revoke and replace credentials if they have been exposed.

Do not copy credentials from old examples or archives without confirming that they are still safe to use.

9. Troubleshooting

"git is not recognized"

Install Git and reopen the terminal.

"python is not recognized"

Install Python and ensure it is available in the system PATH.

"No module named ..."

The required dependency may not be installed. The project's dependency list must be completed and verified before a reliable package installation can be provided.

Application fails during startup

The source may contain an unresolved import, missing package, platform-specific dependency, or incomplete feature module.

Check the complete error message before changing or deleting project files.

Termux does not support a desktop feature

Some desktop features rely on Windows APIs or desktop GUI components. They require separate Android-compatible implementations.

10. Project Status

ELARA is actively being developed. Not all modules are production-ready or supported on every platform.

Installation instructions will be updated as dependencies are verified, platform support improves, and clean installation tests are completed.

---

Repository: https://github.com/saxenasparsh421-sketch/ELARA-AI-OS

Developer: Sparsh Saxena
