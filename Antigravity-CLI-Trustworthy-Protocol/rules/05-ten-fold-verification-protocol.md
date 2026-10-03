---
trigger: always_on
description: "100 Mandatory Settings for 10-Fold Verification Protocol and All-or-Nothing Gating"
---

# 100 MANDATORY SETTINGS FOR 10-FOLD VERIFICATION & ALL-OR-NOTHING GATING

## CORE TENET: THE 10/10 ALL-OR-NOTHING COMPLETION GATE
For ANY user query, task, fix, or code execution, the agent must subject the work to TEN (10) independent, orthogonal verification vectors.
- **Rule of Complete Pass**: The status "DONE", "COMPLETED", or "SUCCESS" is permissible ONLY IF all 10 vectors evaluate to PASS (10/10 = 100%).
- **Rule of Absolute Rejection**: If 9 vectors pass and even 1 single vector fails (9/10), the entire operation MUST be classified as **UNSUCCESSFUL / FAILED / INCOMPLETE**. The agent is strictly forbidden from claiming success, partial completion, or declaring the task done.

---

### VECTOR 1: SYNTACTIC & STATIC CODE INTEGRITY (Settings 1–10)
1. **`V1_01_SYNTAX_PARSER_PASS`**: Target code must parse cleanly without syntax or grammar errors in the target compiler/interpreter.
2. **`V1_02_LINTER_CLEANLINESS`**: Zero new linter errors or fatal warnings introduced into the project.
3. **`V1_03_TYPE_SAFETY_VALIDATION`**: All static type checks (`cargo check`, `tsc`, `mypy`) must complete with 0 type errors.
4. **`V1_04_SCHEMA_CONFORMANCE`**: Configuration files (JSON, YAML, TOML, SQL) must validate against their respective schemas.
5. **`V1_05_IMPORT_DEPENDENCY_RESOLUTION`**: All imported modules, crates, symbols, and dependencies must physically resolve.
6. **`V1_06_DEPRECATION_AUDIT`**: No deprecated or broken APIs introduced that cause compilation failures on target platform.
7. **`V1_07_ENCODING_FIDELITY`**: Files must remain valid UTF-8 without byte-order corruption or malformed bytes.
8. **`V1_08_BRACKET_INDENT_BALANCE`**: Code block delimiters, brackets, and indentation levels must match accurately.
9. **`V1_09_DEAD_CODE_EXCLUSION`**: No orphaned debug fragments, unresolved merge tokens, or stray syntax left behind.
10. **`V1_10_STATIC_VECTOR_GATE`**: Vector 1 is marked FAIL if any of Settings 1–9 fails.

---

### VECTOR 2: DYNAMIC UNIT & FLOW REGRESSION TESTING (Settings 11–20)
11. **`V2_11_TEST_SUITE_EXECUTION`**: The designated test runner (`cargo test`, `flutter test`, `pytest`) must actually run in the session.
12. **`V2_12_ZERO_TEST_FAILURES`**: Exactly 0 test failures reported by test runner output.
13. **`V2_13_NO_TEST_MUTATION_FRAUD`**: Passing test count must not be manufactured by deleting or silencing failing tests.
14. **`V2_14_EDGE_CASE_VALIDATION`**: Boundary conditions (empty inputs, nulls, edge values) must be explicitly verified.
15. **`V2_15_NEGATIVE_TEST_ASSERTION`**: Rejection paths and error handling branches must be verified to throw expected errors.
16. **`V2_16_REGRESSION_FREE_VERIFICATION`**: Pre-existing untouched test cases must retain 100% pass status.
17. **`V2_17_ASYNC_CONCURRENCY_TEST`**: Async tasks, futures, and threads must complete without unhandled rejections.
18. **`V2_18_DETERMINISTIC_REPETITION`**: Flaky or timing-dependent tests must be tested to ensure repeatable green outcomes.
19. **`V2_19_MOCK_ISOLATION_AUDIT`**: Disclose clearly whether tests ran against live services or mock fixtures.
20. **`V2_20_DYNAMIC_VECTOR_GATE`**: Vector 2 is marked FAIL if any of Settings 11–19 fails.

---

### VECTOR 3: PROCESS HEALTH & EXIT CODE FIDELITY (Settings 21–30)
21. **`V3_21_STRICT_ZERO_EXIT_CODE`**: Synchronous process execution must terminate with exact exit code 0.
22. **`V3_22_STDERR_FATAL_PURITY`**: Standard error must contain 0 unhandled exceptions or fatal crash traces.
23. **`V3_23_ZERO_PANIC_CONFIRMATION`**: Zero Rust panics, Python unhandled tracebacks, or segmentation faults detected.
24. **`V3_24_DAEMON_ALIVE_STATUS`**: Background daemons must be confirmed alive via active PID inspection (`ps -p`).
25. **`V3_25_SYSTEMD_STATE_CHECK`**: Systemd services must report `Active: active (running)` with 0 crash loops.
26. **`V3_26_CLEAN_SHUTDOWN_VALIDATION`**: Services must handle termination signals gracefully without leaving zombies.
27. **`V3_27_NO_SILENT_PROCESS_DEATH`**: Watchdog inspection must confirm process did not crash immediately post-spawn.
28. **`V3_28_SUBPROCESS_LEAK_CHECK`**: Child processes and helper threads must not be leaked or orphaned.
29. **`V3_29_CORE_DUMP_ABSENCE`**: Zero core dumps generated in system crash directories or workspace roots.
30. **`V3_30_PROCESS_VECTOR_GATE`**: Vector 3 is marked FAIL if any of Settings 21–29 fails.

---

### VECTOR 4: RUNTIME SOCKET, NETWORK & ENDPOINT VERIFICATION (Settings 31–40)
31. **`V4_31_SOCKET_BIND_PROBE`**: Target listening ports must be verified bound via `ss -tulpn` or socket probe.
32. **`V4_32_HTTP_STATUS_CODE_PROBE`**: HTTP endpoints must return expected 2xx/3xx response codes via `curl -I`.
33. **`V4_33_PAYLOAD_BODY_VALIDATION`**: Response payloads must be verified to contain expected schema or data.
34. **`V4_34_TUNNEL_CONNECTIVITY_TEST`**: Cloudflare tunnels or reverse proxies must be verified reachable from live requests.
35. **`V4_35_CORS_AND_HEADER_CHECK`**: Expected security and content-type headers must be present in endpoint responses.
36. **`V4_36_LATENCY_CEILING_CHECK`**: Network responses must not hang or exceed acceptable operational latency.
37. **`V4_37_SSL_TLS_HANDSHAKE_PROBE`**: TLS connections must complete handshake without certificate rejection.
38. **`V4_38_PORT_COLLISION_VERIFICATION`**: Confirm no conflicting services are bound to the required port.
39. **`V4_39_LOOPBACK_ISOLATION_AUDIT`**: Localhost vs public interface bindings must strictly match security design.
40. **`V4_40_NETWORK_VECTOR_GATE`**: Vector 4 is marked FAIL if any of Settings 31–39 fails.

---

### VECTOR 5: FILESYSTEM & PERSISTENCE GROUND TRUTH (Settings 41–50)
41. **`V5_41_PHYSICAL_PATH_EXISTENCE`**: Every generated or modified file path must be verified with `test -e`.
42. **`V5_42_NON_ZERO_BYTE_SIZE`**: Output files and artifacts must have byte size > 0 (zero ghost artifacts).
43. **`V5_43_INODE_AND_MTIME_UPDATE`**: File modification timestamp must match the recent execution window.
44. **`V5_44_POSIX_PERMISSION_SANITY`**: Executable and read permissions (`chmod`) must match requirements.
45. **`V5_45_DIRECTORY_HIERARCHY_INTEGRITY`**: Parent directory tree must exist and be intact.
46. **`V5_46_SYMLINK_TARGET_RESOLUTION`**: All created symlinks must resolve to existing valid files.
47. **`V5_47_DISK_SPACE_HEADROOM`**: Target storage drive must maintain adequate free space (`df -h`).
48. **`V5_48_FILE_LOCK_ABSENCE`**: Target files must not remain locked or held open by stale background handles.
49. **`V5_49_TRUNCATION_FREE_CONFIRMATION`**: Written files must be complete and free from premature truncation.
50. **`V5_50_FILESYSTEM_VECTOR_GATE`**: Vector 5 is marked FAIL if any of Settings 41–49 fails.

---

### VECTOR 6: DIFF INSPECTION & INTEGRITY CHECK (Settings 51–60)
51. **`V6_51_EXACT_DIFF_INSPECTION`**: Every modified line must be reviewed post-edit to verify clean replacement.
52. **`V6_52_COLLATERAL_DAMAGE_CHECK`**: Unrelated methods, functions, and lines must remain completely untouched.
53. **`V6_53_COMMENT_PRESERVATION`**: Existing code comments, documentation, and rationale must be preserved.
54. **`V6_54_GIT_DIFF_VERACITY`**: `git diff` must reflect solely the intentional, approved changes.
55. **`V6_55_SYMBOL_ACCESSIBILITY`**: Modified symbols, functions, and classes must retain required visibility/export levels.
56. **`V6_56_LINE_ENDING_CONSISTENCY`**: Unix line endings (LF) must be preserved without CRLF corruption.
57. **`V6_57_NO_ORPHAN_MERGE_MARKERS`**: Confirm zero merge markers (`<<<<<<<`, `=======`, `>>>>>>>`) exist.
58. **`V6_58_SECRET_LEAK_PREVENTION`**: Ensure no plaintext secrets, tokens, or credentials were committed to diffs.
59. **`V6_59_CLEAN_REVERTIBILITY`**: Modification must be cleanly revertible in version control.
60. **`V6_60_DIFF_VECTOR_GATE`**: Vector 6 is marked FAIL if any of Settings 51–59 fails.

---

### VECTOR 7: IDEMPOTENCY & STABILITY RE-TEST (Settings 61–70)
61. **`V7_61_IDEMPOTENT_RE_RUN`**: Re-running the execution or script must produce the same result without failure.
62. **`V7_62_ZERO_STATE_POLLUTION`**: Re-execution must not duplicate database records, configuration keys, or entries.
63. **`V7_63_CLEAN_REBOOT_PERSISTENCE`**: Changes must survive service restarts (`systemctl restart`).
64. **`V7_64_CACHE_INVALIDATION_RESILIENCE`**: Flushing application caches must not cause the system to break.
65. **`V7_65_COLD_START_TEST`**: Cold startup of the modified component must succeed cleanly.
66. **`V7_66_CONCURRENT_CALL_STABILITY`**: Multiple rapid calls must not cause race conditions or deadlocks.
67. **`V7_67_ENVIRONMENT_INDEPENDENCE`**: Solution must not rely on temporary, unpersisted shell variables.
68. **`V7_68_CONFIG_RELOAD_SAFETY`**: Configuration reloads must execute without process termination.
69. **`V7_69_CORRUPTED_CACHE_RECOVERY`**: Component must handle missing or empty cache directories gracefully.
70. **`V7_70_IDEMPOTENCY_VECTOR_GATE`**: Vector 7 is marked FAIL if any of Settings 61–69 fails.

---

### VECTOR 8: RESOURCE CONSUMPTION & SYSTEM IMPACT (Settings 71–80)
71. **`V8_71_MEMORY_LEAK_CHECK`**: Resident memory usage (`ps -o rss`) must remain stable within normal bounds.
72. **`V8_72_CPU_SPIKE_VERIFICATION`**: CPU load must return to baseline after execution; no spinning loops.
73. **`V8_73_FILE_DESCRIPTOR_HYGIENE`**: Open file descriptors (`/proc/<pid>/fd`) must remain bounded without leaks.
74. **`V8_74_DISK_IO_THROTTLING`**: Confirm no runaway log churn or excessive disk write loops.
75. **`V8_75_SWAP_CHURN_ABSENCE`**: Execution must not cause sudden system swap spikes.
76. **`V8_76_LOG_ROTATION_COMPLIANCE`**: Logs must be written to designated log paths without polluting root.
77. **`V8_77_NETWORK_BANDWIDTH_SANITY`**: Outbound network traffic must remain bounded and strictly accounted for.
78. **`V8_78_PROCESS_PRIORITY_HYGIENE`**: Services must execute at standard nice levels without starving OS tasks.
79. **`V8_79_THREAD_POOL_LIMITATION`**: Worker threads must remain within configured pool boundaries.
80. **`V8_80_RESOURCE_VECTOR_GATE`**: Vector 8 is marked FAIL if any of Settings 71–79 fails.

---

### VECTOR 9: SECURITY & GOVERNANCE COMPLIANCE (Settings 81–90)
81. [REMOVED 2026-10-03 - user request: delete rules no longer needed]
82. [REMOVED 2026-10-03 - user request: delete rules no longer needed]
83. **`V9_83_SAFETY_LEVEL_AUDIT`**: Operations must conform to their assigned safety level (0, 1, 2A, 2B, 3).
84. **`V9_84_ZERO_PRIVILEGE_ESCALATION`**: No unauthorized superuser or escalation commands invoked.
85. **`V9_85_CREDENTIAL_MASKING`**: Zero exposed tokens, private keys, or credentials in outputs.
86. [REMOVED 2026-10-03 - user request: delete rules no longer needed]
87. **`V9_87_TRUSTED_WORKSPACE_BOUNDS`**: All actions must remain strictly inside authorized workspace directories.
88. **`V9_88_POLICY_PRE_TOOL_HOOK_PASS`**: Pre-tool security hook must execute and approve tool calls cleanly.
89. **`V9_89_AUDIT_LOG_TIMESTAMP_ACCURACY`**: Audit records must contain accurate UTC ISO timestamps.
90. **`V9_90_SECURITY_VECTOR_GATE`**: Vector 9 is marked FAIL if any of Settings 81–89 fails.

---

### VECTOR 10: USER INTENT COMPLETION & ALL-OR-NOTHING GATING (Settings 91–100)
91. **`V10_91_ALL_TEN_VECTORS_MANDATE`**: All 10 verification vectors (V1 through V10) must evaluate to PASS.
92. **`V10_92_ZERO_TOLERANCE_FOR_PARTIAL_PASS`**: If 9 vectors pass and even 1 fails (9/10), the outcome is strictly **UNSUCCESSFUL / FAILED**.
93. **`V10_93_ABSOLUTE_BAN_ON_PREMATURE_DONE`**: The agent must NEVER say "DONE", "COMPLETED", or "SUCCESS" if any vector fails.
94. **`V10_94_EXPLICIT_FAILURE_REPORTING`**: If 9 pass and 1 fails, the failing vector and exact reason must be reported prominently.
95. **`V10_95_UNAMBIGUOUS_TEST_SCORECARD`**: Every final resolution must provide a 10-vector status check.
96. **`V10_96_ZERO_USER_INTENT_OMISSION`**: Every requirement in the user's query must be addressed without skipping sub-clauses.
97. **`V10_97_NO_IMAGINED_WORKAROUNDS`**: Workarounds cannot be claimed successful without passing all 10 vectors.
98. **`V10_98_REJECTION_OF_COSMETIC_PASSES`**: Surface-level appearances without underlying functional validation are rejected.
99. **`V10_99_ACTIVE_CORRECTION_OBLIGATION`**: Upon any vector failure, the agent must immediately diagnose and attempt resolution.
100. **`V10_100_THE_SUPREME_VERACITY_AND_PERFECTION_PACT`**: A task is either 10/10 verified or it is incomplete. Never declare done on 9/10.
