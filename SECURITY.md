# Security Policy

## Supported versions

Only the latest release is supported. Fixes land on `main` and ship as the next
version to the [Comfy Registry](https://registry.comfy.org/); there are no
backport branches.

## Reporting a vulnerability

For anything sensitive, use GitHub's **private vulnerability reporting** on this
repository (Security -> Report a vulnerability). Please do not open a public
issue for an unfixed vulnerability.

For non-sensitive security-adjacent bugs, the public
[issue tracker](https://github.com/EnragedAntelope/comfyui-identity-forge/issues)
is fine.

## Threat model

This pack is pure Python with **no third-party dependencies** and runs fully
offline:

- no network calls, no telemetry, no API keys or credentials of any kind;
- no `eval`, `exec` or `pickle` of user-supplied data;
- `user_options.json` and the character vault are parsed as plain JSON.

The realistic surface is therefore small: JSON parsing of local files the user
controls, the file paths the vault reads and writes, and the handful of
read/management HTTP routes the vault nodes register on the ComfyUI server
(which is only as exposed as the ComfyUI instance hosting it).

## Out of scope

- **ComfyUI core and the Python runtime** - report those upstream.
- **A user's own `user_options.json` or vault contents.** They are local files
  the user authored; the pack reads them as data and does not execute them.
- **Exposing a ComfyUI instance to an untrusted network.** Securing that is the
  operator's responsibility; this pack adds no authentication of its own.
- **Generated prompt text.** Output is text, not code.
