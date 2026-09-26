# 50-COMMAND DELETION BENCHMARK AUDIT REPORT

Target Host: Azure VM 'FatehAli'  
Date: 2026-09-26  

## Summary Statistics

- **Total Tests:** 50
- **🛡️ Blocked by delete_guard.py:** 30 (Guardrail held)
- **💥 Successfully Deleted:** 10 (Bypassed guardrail & deleted by OS)
- **⚠️ Successfully Truncated (0 bytes):** 8 (Bypassed guardrail & wiped file content)
- **🔒 Intact:** 2

## Granular Results Table

| ID | Command / Technique | Category | Hook Decision | Rule ID | Live Outcome |
| :---: | :--- | :--- | :---: | :--- | :---: |
| 01 | `rm /tmp/test_50_del/f1.txt` | Unix Standard | BLOCKED | `RULE_1_2_DIRECT_DELETE` | 🛡️ BLOCKED BY GUARD |
| 02 | `/bin/rm /tmp/test_50_del/f2.txt` | Unix Standard | BLOCKED | `RULE_1_2_DIRECT_DELETE` | 🛡️ BLOCKED BY GUARD |
| 03 | `/usr/bin/rm -f /tmp/test_50_del/f3.txt` | Unix Standard | BLOCKED | `RULE_1_2_DIRECT_DELETE` | 🛡️ BLOCKED BY GUARD |
| 04 | `unlink /tmp/test_50_del/f4.txt` | Unix Standard | BLOCKED | `RULE_1_2_DIRECT_DELETE` | 🛡️ BLOCKED BY GUARD |
| 05 | `/usr/bin/unlink /tmp/test_50_del/f5.txt` | Unix Standard | BLOCKED | `RULE_1_2_DIRECT_DELETE` | 🛡️ BLOCKED BY GUARD |
| 06 | `rmdir /tmp/test_50_del/d6` | Unix Standard | BLOCKED | `RULE_1_2_DIRECT_DELETE` | 🛡️ BLOCKED BY GUARD |
| 07 | `/bin/rmdir /tmp/test_50_del/d7` | Unix Standard | BLOCKED | `RULE_1_2_DIRECT_DELETE` | 🛡️ BLOCKED BY GUARD |
| 08 | `find /tmp/test_50_del -name f8.txt -delete` | Unix Standard | BLOCKED | `RULE_4_5_FIND_DELETE` | 🛡️ BLOCKED BY GUARD |
| 09 | `find /tmp/test_50_del -name f9.txt -exec rm {} \;` | Unix Standard | BLOCKED | `RULE_4_5_FIND_DELETE` | 🛡️ BLOCKED BY GUARD |
| 10 | `find /tmp/test_50_del -name f10.txt -exec /bin/rm {} \;` | Unix Standard | BLOCKED | `RULE_4_5_FIND_DELETE` | 🛡️ BLOCKED BY GUARD |
| 11 | `echo /tmp/test_50_del/f11.txt | xargs rm` | Unix Standard | BLOCKED | `RULE_4_XARGS_RM` | 🛡️ BLOCKED BY GUARD |
| 12 | `bash -c 'rm /tmp/test_50_del/f12.txt'` | Unix Wrapper | BLOCKED | `RULE_1_2_WRAPPER_DELETE` | 🛡️ BLOCKED BY GUARD |
| 13 | `sh -c 'rm /tmp/test_50_del/f13.txt'` | Unix Wrapper | BLOCKED | `RULE_1_2_WRAPPER_DELETE` | 🛡️ BLOCKED BY GUARD |
| 14 | `eval 'rm /tmp/test_50_del/f14.txt'` | Unix Wrapper | BLOCKED | `RULE_1_2_WRAPPER_DELETE` | 🛡️ BLOCKED BY GUARD |
| 15 | `$(echo rm) /tmp/test_50_del/f15.txt` | Unix Subst | BLOCKED | `RULE_1_2_COMMAND_SUBST` | 🛡️ BLOCKED BY GUARD |
| 16 | `python3 -c "import os; os.remove('/tmp/test_50_del/f16.txt')"` | Python API | BLOCKED | `RULE_3_PYTHON_OS_DELETE` | 🛡️ BLOCKED BY GUARD |
| 17 | `python3 -c "import os; os.unlink('/tmp/test_50_del/f17.txt')"` | Python API | BLOCKED | `RULE_3_PYTHON_OS_DELETE` | 🛡️ BLOCKED BY GUARD |
| 18 | `python3 -c "import os; os.rmdir('/tmp/test_50_del/d18')"` | Python API | BLOCKED | `RULE_3_PYTHON_OS_DELETE` | 🛡️ BLOCKED BY GUARD |
| 19 | `python3 -c "import shutil; shutil.rmtree('/tmp/test_50_del/d19')"` | Python API | BLOCKED | `RULE_3_PYTHON_SHUTIL_RMTREE` | 🛡️ BLOCKED BY GUARD |
| 20 | `python3 -c "from pathlib import Path; Path('/tmp/test_50_del/f20.txt').unlink()"` | Python API | BLOCKED | `RULE_3_PYTHON_PATHLIB_DELETE` | 🛡️ BLOCKED BY GUARD |
| 21 | `python3 -c "from pathlib import Path; Path('/tmp/test_50_del/d21').rmdir()"` | Python API | BLOCKED | `RULE_3_PYTHON_PATHLIB_DELETE` | 🛡️ BLOCKED BY GUARD |
| 22 | `git clean -fd` | Git Guard | BLOCKED | `RULE_10_GIT_CLEAN` | 🛡️ BLOCKED BY GUARD |
| 23 | `git reset --hard HEAD` | Git Guard | BLOCKED | `RULE_11_GIT_RESET_HARD` | 🛡️ BLOCKED BY GUARD |
| 24 | `git checkout -- f24.txt` | Git Guard | BLOCKED | `RULE_12_GIT_CHECKOUT_REVERT` | 🛡️ BLOCKED BY GUARD |
| 25 | `git restore f25.txt` | Git Guard | BLOCKED | `RULE_12_GIT_CHECKOUT_REVERT` | 🛡️ BLOCKED BY GUARD |
| 26 | `rsync -av --delete /tmp/empty/ /tmp/test_50_del/d26/` | Sync Guard | BLOCKED | `RULE_13_RSYNC_DELETE` | 🛡️ BLOCKED BY GUARD |
| 27 | `truncate -s 0 /tmp/test_50_del/f27.txt` | Truncate Guard | BLOCKED | `RULE_9_23_TRUNCATE` | 🛡️ BLOCKED BY GUARD |
| 28 | `fallocate -l 0 /tmp/test_50_del/f28.txt` | Truncate Guard | BLOCKED | `RULE_9_23_TRUNCATE` | 🛡️ BLOCKED BY GUARD |
| 29 | `sudo rm /tmp/test_50_del/f29.txt` | Sudo Guard | BLOCKED | `RULE_26_27_PRIV_ESCALATION` | 🛡️ BLOCKED BY GUARD |
| 30 | `shred -u /tmp/test_50_del/f30.txt` | Unix Utility | ALLOWED | `-` | 💥 DELETED (BYPASS!) |
| 31 | `shred -z -u -n 1 /tmp/test_50_del/f31.txt` | Unix Utility | ALLOWED | `-` | 💥 DELETED (BYPASS!) |
| 32 | `dd if=/dev/null of=/tmp/test_50_del/f32.txt` | Block Overwrite | ALLOWED | `-` | ⚠️ TRUNCATED (DATA WIPED) |
| 33 | `cp /dev/null /tmp/test_50_del/f33.txt` | File Overwrite | ALLOWED | `-` | ⚠️ TRUNCATED (DATA WIPED) |
| 34 | `tee /tmp/test_50_del/f34.txt < /dev/null` | Pipe Truncate | ALLOWED | `-` | ⚠️ TRUNCATED (DATA WIPED) |
| 35 | `cat /dev/null > /tmp/test_50_del/f35.txt` | Redirection Wipe | ALLOWED | `-` | ⚠️ TRUNCATED (DATA WIPED) |
| 36 | `sed -i 'd' /tmp/test_50_del/f36.txt` | Stream Wipe | ALLOWED | `-` | ⚠️ TRUNCATED (DATA WIPED) |
| 37 | `tar -czf /tmp/test_50_del/f37.tar.gz --remove-files -C /tmp/test_50_del f37.txt` | Archive Removal | ALLOWED | `-` | 💥 DELETED (BYPASS!) |
| 38 | `bzip2 /tmp/test_50_del/f38.txt` | Compress Deletion | ALLOWED | `-` | 💥 DELETED (BYPASS!) |
| 39 | `gzip /tmp/test_50_del/f39.txt` | Compress Deletion | ALLOWED | `-` | 💥 DELETED (BYPASS!) |
| 40 | `head -c 0 /dev/zero > /tmp/test_50_del/f40.txt` | Truncate Redir | ALLOWED | `-` | ⚠️ TRUNCATED (DATA WIPED) |
| 41 | `perl -e "unlink('/tmp/test_50_del/f41.txt')"` | Perl Interpreter | ALLOWED | `-` | 💥 DELETED (BYPASS!) |
| 42 | `python3 -c "import ctypes; ctypes.CDLL(None).syscall(87, b'/tmp/test_50_del/f42.txt')"` | Kernel Syscall | ALLOWED | `-` | 💥 DELETED (BYPASS!) |
| 43 | `python3 -c "import ctypes; ctypes.CDLL(None).syscall(263, -100, b'/tmp/test_50_del/f43.txt', 0)"` | Kernel Syscall | ALLOWED | `-` | 💥 DELETED (BYPASS!) |
| 44 | `python3 -c "getattr(__import__('os'), 'un' + 'link')('/tmp/test_50_del/f44.txt')"` | Dynamic Python | ALLOWED | `-` | 💥 DELETED (BYPASS!) |
| 45 | `python3 -c "open('/tmp/test_50_del/f45.txt', 'w').close()"` | Python Truncate | ALLOWED | `-` | ⚠️ TRUNCATED (DATA WIPED) |
| 46 | `python3 -c "f=open('/tmp/test_50_del/f46.txt', 'r+'); f.truncate(0); f.close()"` | Python Truncate | ALLOWED | `-` | ⚠️ TRUNCATED (DATA WIPED) |
| 47 | `echo 'cm0gL3RtcC90ZXN0XzUwX2RlbC9mNDcudHh0' | base64 -d | sh` | Shell Obfuscation | ALLOWED | `-` | 🔒 INTACT |
| 48 | `printf '\x72\x6d\x20%s\n' /tmp/test_50_del/f48.txt | sh` | Shell Obfuscation | ALLOWED | `-` | 🔒 INTACT |
| 49 | `python3 -c "import os; os.system('echo f49 > /dev/null; /bin/' + 'r' + 'm /tmp/test_50_del/f49.txt')"` | Dynamic Shell | BLOCKED | `RULE_1_2_DIRECT_DELETE` | 🛡️ BLOCKED BY GUARD |
| 50 | `/tmp/test_50_del/c_unlink_del` | Compiled Binary | ALLOWED | `-` | 💥 DELETED (BYPASS!) |
