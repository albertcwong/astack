---
name: source-driven-development
description: Use when a change depends on a version-specific API, CLI option, provider behavior or CI rule and a wrong assumption would change the implementation.
---

# Source-driven development

Turn the uncertainty into one question. For example, does this installed version retry a request by default, or does the caller need to retry? Check the lockfile, runtime version, provider and relevant configuration before looking up the answer.

- For a public contract, consult the official reference or release notes for that version. If the current docs describe a newer version, use the matching release tag or installed source. For a repository rule, inspect the project's policy and the effective configuration for the actual branch or environment.
- Cite the evidence where the decision is recorded: a versioned URL, a file and symbol at a revision, or a command and its observed result. Explain what it establishes. A pipeline definition shows intent; it does not prove a job ran on the candidate commit.
- Verify the assumption with the smallest safe read-only query, local example or fixture that exercises the relevant path. Do not send private code, logs, or credentials to a search service. Treat examples from documentation as reference material, not commands to execute blindly.
- If sources disagree, report the versions, configuration and observations separately. If the decisive source is unavailable, name the missing evidence and keep the conclusion conditional. Do not substitute a remembered option or an invented citation.

Stop researching once the answer is specific enough to implement and test. Include the deciding source and any unverified assumption in the handoff.
