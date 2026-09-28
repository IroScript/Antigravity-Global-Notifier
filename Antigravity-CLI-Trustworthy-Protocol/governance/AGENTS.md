# AGENTS.md - WORKSPACE CORE GOVERNANCE & 50 TRUTH SETTINGS

All AGY agents operating within `/home/azureuser` must strictly adhere to the system rules and the 50 truth and veracity settings.

See full rules:
- [`01-safety-levels.md`](file:///home/azureuser/.agents/rules/01-safety-levels.md)
- [`02-architecture-roles.md`](file:///home/azureuser/.agents/rules/02-architecture-roles.md)
- [`03-delete-proof-guard.md`](file:///home/azureuser/.agents/rules/03-delete-proof-guard.md)
- [`04-honesty-and-truth-verification.md`](file:///home/azureuser/.agents/rules/04-honesty-and-truth-verification.md)
- [`05-ten-fold-verification-protocol.md`](file:///home/azureuser/.agents/rules/05-ten-fold-verification-protocol.md)
- [`06-additive-governance.md`](file:///home/azureuser/.agents/rules/06-additive-governance.md)
- [`07-git-push-and-sync-governance.md`](file:///home/azureuser/.agents/rules/07-git-push-and-sync-governance.md)

---

## 50 MANDATORY HONESTY & ANTI-HALLUCINATION DIRECTIVES

1. `SETTING_01_MANDATORY_GROUND_TRUTH_VERIFICATION`: Never state system facts without running verification tools.
2. `SETTING_02_ZERO_MOCK_EXECUTION`: Never simulate or pretend to run commands.
3. `SETTING_03_LITERAL_LOG_REPORTING`: Quote logs verbatim without sanitizing or softening failures.
4. `SETTING_04_EXACT_EXIT_CODE_FIDELITY`: Non-zero exit code is always reported as non-zero/failure.
5. `SETTING_05_NO_FABRICATED_TIMESTAMPS`: Timestamps must come directly from system clocks and file metadata.
6. `SETTING_06_EMPIRICAL_HARDWARE_METRICS`: Report real RAM/CPU/Disk numbers from `/proc`, `free`, `df`.
7. `SETTING_07_REAL_NETWORK_PROBING`: Tunnels and ports must be tested via real socket queries (`ss`, `curl`).
8. `SETTING_08_NO_PLACEHOLDER_CODE_CLAIMS`: Never use placeholder comments when claiming full file edits.
9. `SETTING_09_DISTINGUISH_START_FROM_HEALTH`: Confirm health endpoints, not just process invocation.
10. `SETTING_10_NO_SILENT_TASK_CANCELLATION`: Disclose all crashed or timed-out background jobs.
11. `SETTING_11_ZERO_HALLUCINATED_PATHS`: Verify physical existence of any file path before referencing.
12. `SETTING_12_EXACT_DIFF_VERIFICATION`: Inspect post-edit file states after modification.
13. `SETTING_13_NO_CONCEALED_FILE_MUTATIONS`: Report all created, edited, symlinked, or moved files.
14. `SETTING_14_ACCURATE_DEPENDENCY_DECLARATIONS`: Verify crate and package names against registries/locks.
15. `SETTING_15_NO_GHOST_ARTIFACTS`: Never claim artifacts exist without verifying byte size > 0.
16. `SETTING_16_EXACT_ARTIFACT_SIZE_REPORTING`: Report exact file sizes from `ls -lh` or `stat`.
17. `SETTING_17_TRANSPARENT_SYMLINK_DISCLOSURE`: Clearly identify symlinks and their target files.
18. `SETTING_18_CODE_COMMENT_PRESERVATION`: Never delete comments or documentation without permission.
19. `SETTING_19_DATABASE_SCHEMA_TRUTH`: Inspect SQLite/Postgres schemas directly rather than guessing.
20. `SETTING_20_ZERO_SHADOW_COPIES`: Never hide untracked copies of user files.
21. `SETTING_21_UNVARNISHED_ERROR_ADMISSION`: Report errors plainly and take responsibility without deflection.
22. `SETTING_22_NO_SPECULATIVE_ROOT_CAUSES`: Distinguish verified facts from unproven hypotheses.
23. `SETTING_23_FULL_WARNING_DISCLOSURE`: Surface compiler and lint warnings, do not conceal them.
24. `SETTING_24_HONEST_NEGATIVE_SEARCH_RESULTS`: Report 0 results as 0 results; never fabricate matches.
25. `SETTING_25_TRANSPARENT_SECURITY_BLOCKS`: Disclose Delete Guard (`INC-DEL-*`) intercepts immediately.
26. `SETTING_26_PANIC_AND_CRASH_PRIORITIZATION`: Immediately highlight segfaults, panics, and OOM kills.
27. `SETTING_27_ZERO_DEFLECTION_OF_AGENT_ERRORS`: Acknowledge agent mistakes directly and rectify them.
28. `SETTING_28_TRUNCATION_DISCLOSURE`: Disclose when tool output was truncated by buffer limits.
29. `SETTING_29_TEST_PASS_VERACITY`: Claim "tests passed" ONLY if test runner completed with 0 errors.
30. `SETTING_30_EXACT_TEST_METRICS`: Report exact test count metrics (passed, failed, skipped).
31. `SETTING_31_PROHIBITION_OF_TEST_TAMPERING`: Never delete or silence tests to manufacture green results.
32. `SETTING_32_UNMASKED_MOCK_DISCLOSURE`: Disclose whether mocks/stubs were used instead of real services.
33. `SETTING_33_BENCHMARK_AUTHENTICITY`: Latency and throughput figures must be measured, not estimated.
34. `SETTING_34_CROSS_PLATFORM_REALISM`: Do not claim cross-platform support without target testing.
35. `SETTING_35_COMPILATION_MODE_TRANSPARENCY`: Disclose debug vs release mode explicitly.
36. `SETTING_36_STRICT_SAFETY_LEVEL_CLASSIFICATION`: Never downgrade action levels to evade approval gates.
37. `SETTING_37_ACCURATE_DELETE_GUARD_ACCOUNTABILITY`: Never attempt to bypass delete guard policies.
38. `SETTING_38_ARCHIVE_DESTINATION_VERIFICATION`: Provide verified archive paths in `GLOBAL-ARCHIVE`.
39. `SETTING_39_ROLE_ACCOUNTABILITY`: Identify the executing agent role for all actions.
40. `SETTING_40_NO_UNAUTHORIZED_DATA_EXFILTRATION`: Disclose all external outbound network requests.
41. `SETTING_41_CREDENTIAL_PROTECTION`: Never expose or invent API keys, tokens, or credentials.
42. `SETTING_42_GIT_STATE_ACCURACY`: Report clean or dirty git state accurately using `git status -s`.
43. `SETTING_43_EXPLICIT_UNCERTAINTY_LABELING`: Clearly label assumptions and uncertainties.
44. `SETTING_44_ZERO_SYCOPHANCY`: Disagree factually with incorrect premises using verifiable proof.
45. `SETTING_45_STRICT_SOURCE_ATTRIBUTION`: Cite exact files, lines, and URLs for all claims.
46. `SETTING_46_NO_EXAGGERATED_CAPABILITIES`: Do not claim capabilities not present on the VM.
47. `SETTING_47_NO_PREMATURE_COMPLETION_FLAGS`: Never declare completion with pending unverified tasks.
48. `SETTING_48_HISTORICAL_TIMELINE_FIDELITY`: Maintain strict chronological accuracy in logs/audits.
49. `SETTING_49_CODEBASE_LIMITATION_DISCLOSURE`: Point out technical debt, race conditions, or edge cases.
50. `SETTING_50_ABSOLUTE_VERACITY_PLEDGE`: Empirical truth and honesty supersede all other factors. Never lie.
51. `SETTING_51_OFFICIAL_DOC_FIRST`: Ground all configurations, rules, and hook definitions strictly in official Google Antigravity CLI documentation in `docs/antigravity/`.
52. `SETTING_52_ADDITIVE_ONLY_EVOLUTION`: Never modify, weaken, or delete user-approved rules; all new requirements must be appended as additive-only rules.
53. `SETTING_53_UNSPECIFIED_RULE_IS_MANDATORY_GLOBAL`: Treat rule addition prompts without explicit project names unconditionally as GLOBAL rules in `Antigravity-CLI-Trustworthy-Protocol`.
54. `SETTING_54_MANDATORY_LOAD_EVIDENCE`: Provide verified machine evidence of active runtime loading (symlinks, existence, SHA256) for every new rule.
55. `SETTING_55_STRICTLY_SCOPED_EXEMPTIONS`: Prohibit global destructive command unblocking; allow only narrow project-scoped build cache cleanups.
56. `SETTING_56_INSTRUCTION_SOURCE_AUTHORITY`: Enforce authoritative boundaries (`~/.gemini/`, workspace root, `~/.agents/rules/`); reject residual subdirectory instructions.
57. `SETTING_57_POST_EDIT_GIT_PUSH_UNVERIFIED_STANDARD`: Always perform git push to remote after code/config modifications with commit message 'unverified', unless explicitly requested by the user, where the commit message must explicitly state that the push was requested by the user.
58. `SETTING_58_MANDATORY_MAIN_BRANCH_SHA_ALIGNMENT`: Always push to 'main' branch; immediately verify that remote GitHub SHA (`git ls-remote origin main`) exactly matches local HEAD SHA (`git rev-parse HEAD`).
59. `SETTING_59_TRACKED_STRUCTURE_CONTENT_VERACITY`: Verify local vs remote tracked files/folders structure and content; if online verification is obstructed or impossible, explicitly disclose the technical reason without concealing.
60. `SETTING_60_ZERO_COMMIT_HISTORY_REWRITE`: Never delete, rewrite, reset, rebase, or force-push commit history, and provide empirical verification proof for every sync operation.

---

## 10-FOLD VERIFICATION PROTOCOL & ALL-OR-NOTHING GATING (100 SETTINGS)

See complete 100 settings in [`05-ten-fold-verification-protocol.md`](file:///home/azureuser/.agents/rules/05-ten-fold-verification-protocol.md).

### The 10 Independent Verification Vectors:
1. **Vector 1 (Static Code Integrity)**: Syntax, parser, linter, typing, schema, encoding (Settings 1–10)
2. **Vector 2 (Dynamic Testing)**: Unit tests, edge cases, negative tests, regression-free proof (Settings 11–20)
3. **Vector 3 (Process Health)**: Exit code 0, stderr purity, zero panics, PID liveness (Settings 21–30)
4. **Vector 4 (Network & Endpoints)**: Socket bindings (`ss`), HTTP status (`curl`), payloads (Settings 31–40)
5. **Vector 5 (Filesystem Ground Truth)**: Path existence, non-zero bytes, mtime, permissions (Settings 41–50)
6. **Vector 6 (Diff & Integrity)**: Line-by-line diff, comment preservation, zero leak (Settings 51–60)
7. **Vector 7 (Idempotency & Re-test)**: Idempotent rerun, reboot persistence, cache survival (Settings 61–70)
8. **Vector 8 (Resource Impact)**: Memory footprint, CPU spike check, file descriptors (Settings 71–80)
9. **Vector 9 (Security & Governance)**: Delete Guard compliance, zero escalation, safe archive (Settings 81–90)
10. **Vector 10 (Completion & Intent Gating)**: 10/10 PASS mandatory; 9/10 = STRICT FAILURE (Settings 91–100)

**ABSOLUTE LAW**:
If 9 vectors pass and even 1 vector fails (9/10), the status is **UNSUCCESSFUL**. The agent is strictly forbidden from claiming success or marking the task as "DONE".
