# Antigravity CLI Trustworthy Protocol

Machine-authoritative trust, governance, and 10-layer verification architecture for Google Antigravity CLI (`agy`).

---

## 1. Architecture Overview
This repository serves as the central source-of-truth for all Antigravity CLI trust, safety, governance, lifecycle hooks, and verification configurations.
Live AGY runtime configurations (`~/.gemini/config/`, `~/.agents/`, and workspace root) are linked to these files via resilient filesystem symlinks.

---

## 2. Directory Structure
- [`docs/antigravity/`](docs/antigravity/): Local archive of 10 official Google Antigravity documentation files (`rules.md`, `hooks.md`, `cli.md`, `skills.md`, `plugins.md`, `mcp_servers.md`, `json_configs.md`, `ide.md`, `app.md`, `sdk.md`) + `MANIFEST.sha256`.
- [`governance/`](governance/): Master system governance containing 56 Mandatory Truth & Anti-Hallucination Directives (`AGENTS.md`, `GEMINI.md`).
- [`rules/`](rules/): Modular AGY rule specifications (`01` through `06-additive-governance.md`).
- [`hooks/`](hooks/): Native AGY PreToolUse Delete Guard (`delete_guard.py`), Completion Gate Stop Hook (`completion_gate_stop_hook.py`), and hook registration manifest (`hooks.json`).
- [`interceptors/`](interceptors/): Scoped OS binary wrappers (`scoped_rm.py`, `unzip`).
- [`scripts/`](scripts/): Hardened 10-fold verification engine (`verify_10_fold.py`) and safe archive engine (`safe_archive.py`).
- [`install.sh`](install.sh): Automated idempotent installer for fresh machine bootstrap.

---

## 3. Fresh Machine Installation (One-Click Setup)
If you clone this repository onto a fresh machine with Google Antigravity CLI installed:

```bash
git clone https://github.com/IroScript/Antigravity-Global-Notifier.git
cd Antigravity-Global-Notifier/Antigravity-CLI-Trustworthy-Protocol
bash install.sh
```

The script will automatically:
1. Establish all runtime symlinks in `~/.gemini/`, `~/.agents/rules/`, and `~/.local/bin/`.
2. Configure `settings.json` with trusted workspace boundaries.
3. Generate a secure HMAC-SHA256 verification secret key.
4. Execute self-testing and output initial 10-level verification proof.

---

## 4. Secret Separation & Safety
Runtime cryptographic keys (`.verification_secret.key`), single-use consumed nonces (`consumed_nonces.jsonl`), and dynamic verification states (`verification_state.json`) remain strictly outside version control, enforced by `.gitignore` and PreToolUse access barriers.
