ELARA — Security Policy

1. Overview

Security and privacy are important considerations in the development of ELARA AI & OS.

ELARA is an actively developed desktop assistant project that may interact with AI services, local files, microphones, cameras, screen content, and operating-system features.

Users should understand the permissions and external services involved before enabling individual features.

2. API Keys and Credentials

Never commit or publish:

- OpenRouter API keys.
- OpenAI API keys.
- Weather service API keys.
- Access tokens.
- Passwords.
- Private ".env" files.
- Other confidential configuration data.

Recommended practices

- Store credentials in local environment variables or a private ".env" file.
- Add ".env" to ".gitignore".
- Never paste credentials into public issues or discussions.
- Rotate credentials immediately if they become exposed.

Removing a secret from the latest commit does not necessarily remove it from Git history. Previously exposed credentials should be revoked or replaced.

3. Camera and Microphone Permissions

Some ELARA components may use camera or microphone input.

Users should:

- Grant permissions only when required.
- Keep monitoring features under their control.
- Avoid recording or monitoring people without their knowledge and consent.
- Review local storage for captured media and temporary recordings.

4. Screen and File Privacy

Some assistant workflows may process screenshots, selected files, images, and other user-provided content.

Depending on the enabled module and configuration, data may be processed locally or transmitted to an external AI service.

Do not assume all processing is offline.

Avoid submitting passwords, financial information, private documents, or other sensitive information to external services.

5. Local Data Storage

ELARA may store application data locally, including:

- Chat history.
- Configuration data.
- Temporary audio.
- Images and other media.
- Module-specific information.

Not every local storage component is verified to provide encryption by default.

Protect access to your device and review stored application data periodically.

6. Third-Party Services

Some ELARA features depend on external services and packages.

Their privacy policies, security practices, availability, and terms may differ from ELARA's own project policies.

Review third-party requirements before enabling integrations.

7. Reporting Security Vulnerabilities

If you discover a security vulnerability:

1. Do not publish API keys or personal information.
2. Avoid sharing exploit details publicly before the issue is addressed.
3. Contact the project maintainer through the repository's available private communication channel, if provided.
4. Include a clear description and the affected component.

Do not include real credentials or private user data in reports.

8. Development Status

ELARA is under active development.

This project should not be considered a security-certified operating system or a production-grade security platform.

Features and security controls may change as development progresses.

9. Responsible Use

Use ELARA responsibly.

Do not use its camera, microphone, screen-analysis, automation, or monitoring components to access another person's data or monitor someone without appropriate permission.

---

Repository: https://github.com/saxenasparsh421-sketch/ELARA-AI-OS

Developer: Sparsh Saxena
