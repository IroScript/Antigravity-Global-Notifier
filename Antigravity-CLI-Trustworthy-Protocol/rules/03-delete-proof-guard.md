---
trigger: always_on
description: "40-Point delete-proof architecture rules prohibiting deletion and privilege escalation."
---

# 40-POINT DELETE-PROOF ARCHITECTURE GUARD

- **Global File Removal Prohibition**: Direct or indirect file removal operations are intercepted and denied by the PreToolUse hook.
- **Zero Privilege Escalation**: Superuser commands are completely restricted.
- **Safe Archiving Protocol**: When any file or artifact is retired, move it safely into GLOBAL-ARCHIVE using safe_archive.py.
- **Runtime Hook**: The policy engine runs delete_guard.py at every tool execution step.
