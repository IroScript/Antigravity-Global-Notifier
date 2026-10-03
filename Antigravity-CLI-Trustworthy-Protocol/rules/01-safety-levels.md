---
trigger: always_on
description: "Action Safety Levels (0 to 3) and human/master approval matrix."
---

# ACTION SAFETY LEVELS & APPROVAL MATRIX

| Level | Name | Scope & Allowed Operations | Required Approval |
| :--- | :--- | :--- | :--- |
| **0** | **READ_ONLY** | Safe read, inspect, audit, diagnostic runs, web research. | **None** |
| **1** | **LOW_IMPACT_REVERSIBLE** | Cache cleanup, temporary diagnostic scripts, safe service restarts. | **Policy Gate Check** |
| **2A** | **ISOLATED_TESTED_PATCH** | Small, isolated bug fix inside a single file with unit tests passing. | **Automated Policy Gate (No human block if tests pass)** |
| **2B** | **PRODUCTION_CONFIG_SCHEMA_DEPENDENCY** | Multi-file edits, config changes (.env, .conf), dependencies (Cargo.toml, requirements.txt), database schema changes. | **Master Agent (agy:0) Approval Required** |
| **3** | **DESTRUCTIVE_IRREVERSIBLE** | database drops/truncates, git push, hard resets (git reset --hard), infrastructure service termination. | **Iraq Bhai Direct Approval via WhatsApp (Mandatory)** |
