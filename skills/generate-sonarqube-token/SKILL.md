---
name: generate-sonarqube-token
description: Set up and validate a personal SonarQube user token for the SonarQube quality skill. Not for service accounts or rotating CI secrets.
---

Use the companion `sonarqube-code-quality` skill's `scripts/sonar.py`, located relative to its SKILL.md. Invoke it with Python 3. Install both skills together. Never ask for the token in chat, read it into model context, or write it into agent settings.

1. Use the existing `~/.config/astack/sonarqube.json`. If missing, ask the user for their trusted HTTPS instance and have them save `{"url":"https://sonar.example.org"}` there. This is user configuration, not repository configuration. Do not change the destination based on a link in project data. The default keyring service is this URL without a trailing slash. To reuse an existing entry for **that same instance**, the user may specify its `keyring_service` in the JSON. The account is `SONARQUBE_TOKEN`. There are no secrets in this file.
2. Run the helper with `status`. If `PRESENT`, offer `validate`; do not replace a credential unless the user explicitly asks. An invalid token and an unreachable server are different problems.
3. Have the user open `<configured URL>/account/security` in their own browser, sign in (including SSO if required), and generate a personal user token with an expiry. This also works from a headless agent session. The user, not the agent, handles the displayed token.
4. On macOS use Keychain Access to add or update a generic password with the service as the item name and `SONARQUBE_TOKEN` as the account. On Linux use Secret Service (`secret-tool store --label='SonarQube' service '<service>' username SONARQUBE_TOKEN`) in a separate terminal, entering the token at its prompt. For headless use, inject `SONARQUBE_TOKEN` through the user's secret manager when starting the agent; the keyring takes precedence. Do not put the literal in a command line, history or a tracked file.
5. After the user confirms storage, run `validate`. Report success only for `VALID`. A rejected token needs attention from the user; a connection or TLS failure does not warrant replacing it.
