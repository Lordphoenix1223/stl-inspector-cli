# Security Policy

This repository contains a local-only Python CLI. It should never contain secrets, private URLs, unpublished prompts, or credentials of any kind.

## Reporting

- Prefer GitHub private vulnerability reporting if it is enabled for this repository.
- If private reporting is not available, open a minimal issue requesting contact and keep the report high level.
- Do not post API keys, auth tokens, local filesystem paths, or private files in issues or pull requests.

## Scope Notes

- The CLI has no network behavior, no auth system, and no provider integration.
- Relevant controls here are input validation, bounded file handling, dependency hygiene, and publication safety.
