#!/usr/bin/env python3
"""
Linux Landlock LSM Kernel Sandbox (Points 19-24 of Delete-Proof Specification)
Enforces kernel-level restriction denying REMOVE_FILE, REMOVE_DIR, REFER, and TRUNCATE.
Inherited irreversibly by all child processes via PR_SET_NO_NEW_PRIVS.
"""

import os
import sys
import ctypes

SYS_landlock_create_ruleset = 444
SYS_landlock_add_rule = 445
SYS_landlock_restrict_self = 446
PR_SET_NO_NEW_PRIVS = 38
LANDLOCK_RULE_PATH_BENEATH = 1

# Landlock Access Flags
LANDLOCK_ACCESS_FS_EXECUTE     = (1 << 0)
LANDLOCK_ACCESS_FS_WRITE_FILE  = (1 << 1)
LANDLOCK_ACCESS_FS_READ_FILE   = (1 << 2)
LANDLOCK_ACCESS_FS_READ_DIR    = (1 << 3)
LANDLOCK_ACCESS_FS_REMOVE_DIR  = (1 << 4)
LANDLOCK_ACCESS_FS_REMOVE_FILE = (1 << 5)
LANDLOCK_ACCESS_FS_MAKE_CHAR   = (1 << 6)
LANDLOCK_ACCESS_FS_MAKE_DIR    = (1 << 7)
LANDLOCK_ACCESS_FS_MAKE_REG    = (1 << 8)
LANDLOCK_ACCESS_FS_MAKE_SOCK   = (1 << 9)
LANDLOCK_ACCESS_FS_MAKE_FIFO   = (1 << 10)
LANDLOCK_ACCESS_FS_MAKE_BLOCK  = (1 << 11)
LANDLOCK_ACCESS_FS_MAKE_SYM    = (1 << 12)
LANDLOCK_ACCESS_FS_REFER       = (1 << 13)
LANDLOCK_ACCESS_FS_TRUNCATE    = (1 << 14)

class LandlockRulesetAttr(ctypes.Structure):
    _fields_ = [('handled_access_fs', ctypes.c_uint64)]

class LandlockPathBeneathAttr(ctypes.Structure):
    _fields_ = [
        ('allowed_access', ctypes.c_uint64),
        ('parent_fd', ctypes.c_int32),
    ]

def apply_delete_proof_landlock(root_paths=None):
    """
    Applies kernel-level Landlock restrictions preventing all deletion, rmdir, and truncation.
    """
    if root_paths is None:
        root_paths = ["/"]

    libc = ctypes.CDLL(None, use_errno=True)

    # All filesystem actions handled by ruleset
    handled = (
        LANDLOCK_ACCESS_FS_EXECUTE |
        LANDLOCK_ACCESS_FS_WRITE_FILE |
        LANDLOCK_ACCESS_FS_READ_FILE |
        LANDLOCK_ACCESS_FS_READ_DIR |
        LANDLOCK_ACCESS_FS_REMOVE_DIR |
        LANDLOCK_ACCESS_FS_REMOVE_FILE |
        LANDLOCK_ACCESS_FS_MAKE_DIR |
        LANDLOCK_ACCESS_FS_MAKE_REG |
        LANDLOCK_ACCESS_FS_MAKE_SYM |
        LANDLOCK_ACCESS_FS_REFER |
        LANDLOCK_ACCESS_FS_TRUNCATE
    )

    # Allowed: Execution, reading, writing, creating files/dirs/symlinks.
    # EXCLUDED: REMOVE_DIR, REMOVE_FILE, REFER (rename/relink bypass), TRUNCATE
    allowed = (
        LANDLOCK_ACCESS_FS_EXECUTE |
        LANDLOCK_ACCESS_FS_WRITE_FILE |
        LANDLOCK_ACCESS_FS_READ_FILE |
        LANDLOCK_ACCESS_FS_READ_DIR |
        LANDLOCK_ACCESS_FS_MAKE_DIR |
        LANDLOCK_ACCESS_FS_MAKE_REG |
        LANDLOCK_ACCESS_FS_MAKE_SYM
    )

    attr = LandlockRulesetAttr(handled)
    ruleset_fd = libc.syscall(
        SYS_landlock_create_ruleset,
        ctypes.byref(attr),
        ctypes.sizeof(attr),
        0
    )
    if ruleset_fd < 0:
        err = ctypes.get_errno()
        raise OSError(err, f"landlock_create_ruleset failed: errno {err}")

    try:
        for p in root_paths:
            if not os.path.exists(p):
                continue
            fd = os.open(p, os.O_PATH | os.O_CLOEXEC)
            try:
                pb = LandlockPathBeneathAttr(allowed, fd)
                ret = libc.syscall(
                    SYS_landlock_add_rule,
                    ruleset_fd,
                    LANDLOCK_RULE_PATH_BENEATH,
                    ctypes.byref(pb),
                    0
                )
                if ret < 0:
                    err = ctypes.get_errno()
                    raise OSError(err, f"landlock_add_rule for {p} failed: errno {err}")
            finally:
                os.close(fd)

        # Enforce PR_SET_NO_NEW_PRIVS (mandatory before landlock_restrict_self)
        if libc.prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0:
            err = ctypes.get_errno()
            raise OSError(err, f"prctl(PR_SET_NO_NEW_PRIVS) failed: errno {err}")

        # Restrict self
        if libc.syscall(SYS_landlock_restrict_self, ruleset_fd, 0) != 0:
            err = ctypes.get_errno()
            raise OSError(err, f"landlock_restrict_self failed: errno {err}")

    finally:
        os.close(ruleset_fd)

    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <command> [args...]")
        sys.exit(1)

    try:
        apply_delete_proof_landlock()
        # Execute the requested command with Landlock permanently active
        os.execvp(sys.argv[1], sys.argv[1:])
    except Exception as e:
        sys.stderr.write(f"Landlock initialization failed: {e}\n")
        sys.exit(1)
