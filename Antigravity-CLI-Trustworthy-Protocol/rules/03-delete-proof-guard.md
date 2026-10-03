---
trigger: always_on
description: "Delete feature approved architecture: file removal and maintenance operations authorized across project workspaces."
---

# DELETE FEATURE APPROVED ARCHITECTURE GUARD

- **Delete Feature Approved**: File removal operations (`rm`, `rmdir`, `unlink`, `shutil.rmtree`, `git clean`, etc.) requested by the user or required for workspace cleanup, refactoring, and maintenance are APPROVED and permitted across project workspaces.
- **Delete Lock Lifted**: The legacy hard fail-closed delete lock has been replaced with user-authorized deletion across all workspaces.
- **OS Root Protection**: Critical operating system root directories (`/etc`, `/boot`, `/usr`, `/bin`, `/sbin`, `/root`, `/`) remain protected from accidental destruction.
- **Runtime Hook**: The policy engine runs `delete_guard.py` at tool execution with the delete feature approved.
