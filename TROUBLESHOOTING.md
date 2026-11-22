ELARA — Troubleshooting Guide

This document covers common setup and compatibility issues when downloading and preparing ELARA AI & OS.

1. Git Is Not Recognized

Error:

'git' is not recognized as an internal or external command

Solution:

- Install Git.
- Ensure Git is added to your system PATH.
- Restart your terminal.
- Verify:

git --version

2. Python Is Not Recognized

Error:

python is not recognized

Solution:

Install Python and ensure it is available in PATH.

On Windows, try:

py --version

On Termux, install Python:

pkg install python

3. Repository Download Fails

Error:

fatal: unable to access repository

Possible causes:

- Internet connection problems.
- Incorrect repository URL.
- GitHub connectivity issues.

Solution:

Verify the repository address:

https://github.com/saxenasparsh421-sketch/ELARA-AI-OS

Retry the clone command after checking your connection.

4. Virtual Environment Activation Fails

Windows Command Prompt

.venv\Scripts\activate.bat

Windows PowerShell

.venv\Scripts\Activate.ps1

If PowerShell blocks script execution, use Command Prompt instead of changing system-wide security settings.

Android Termux

source .venv/bin/activate

5. Missing Python Module

Error:

ModuleNotFoundError: No module named 'module_name'

Possible cause:

A required Python package may be missing or the project's dependency list may be incomplete.

The current public "requirements.txt" is empty. A complete verified dependency installation process is still pending.

Do not install random packages based only on an error message. Check the module's actual dependency and platform requirements first.

6. Application Startup Failure

ELARA contains multiple modules that are still under development.

Startup errors may be caused by:

- Missing modules.
- Incompatible dependencies.
- Incomplete feature implementations.
- Platform-specific APIs.
- Configuration problems.

Save the complete error message before attempting a fix.

7. Termux Compatibility Issues

Termux is an Android command-line environment, not a Windows desktop environment.

Some ELARA components depend on:

- Desktop GUI frameworks.
- Windows-specific APIs.
- Desktop automation libraries.
- Hardware and device interfaces.

These components may not work in Termux without separate Android-compatible implementations.

Termux support is currently experimental.

8. API Configuration Problems

Some features require external API credentials.

Check that:

- The correct provider is configured.
- The API key is valid.
- Your internet connection works.
- Credentials are stored locally and not committed to GitHub.

Never share your API keys in public issue reports.

9. Reporting a Bug

When reporting an issue, include:

1. Operating system and version.
2. Python version.
3. Installation method.
4. The command that produced the error.
5. The complete error message.
6. Whether the issue occurs on Windows or Termux.

Remove API keys, passwords, personal information, and private file paths before sharing logs.

10. Project Status

ELARA is actively developed. Not every feature is currently verified for every operating system.

Installation and compatibility documentation will be updated as features are tested and improved.

---

Repository: https://github.com/saxenasparsh421-sketch/ELARA-AI-OS

Developer: Sparsh Saxena
