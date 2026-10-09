/**
 * Prompt Delivery Manager for WhatsApp Bridge
 *
 * Implements the robust delivery lifecycle:
 * RECEIVED -> PERSISTED -> ROUTED -> READY -> PASTING -> PASTED -> SUBMITTING -> SUBMISSION_CONFIRMED -> EXECUTING -> COMPLETED
 *
 * Fault & Recovery States:
 * WAITING_FOR_SAME_PROJECT_ZIP_CAPTURE, RETRYABLE_FAILURE, RECOVERY_IN_PROGRESS,
 * EXECUTION_UNCERTAIN, TERMINAL_UNAVAILABLE, FAILED_WITH_EVIDENCE
 *
 * Invariants:
 * 1. ZERO USER DECISIONS: All decisions deterministic based on machine evidence.
 * 2. BRACKETED-PASTE SETTLING: Dynamic, bounded, asynchronous settling delay before Enter.
 * 3. TELEMETRY-FIRST VERIFICATION: Authoritative history for Codex & AGY + supporting pane state.
 * 4. DUPLICATE-SAFE: Never blind repeated Enters; at most one bounded retry only when submission is definitely absent.
 * 5. CONCURRENT ACROSS TARGETS, SERIALIZED PER TARGET PANE.
 * 6. SAME-PROJECT ZIP CAPTURE HOLD: Holds only when same project is in source ZIP capture critical section.
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const { execFileSync, execSync } = require('child_process');

const USER_HOME = process.env.HOME || os.homedir();

const DELIVERY_STATES = {
  RECEIVED: 'RECEIVED',
  PERSISTED: 'PERSISTED',
  ROUTED: 'ROUTED',
  READY: 'READY',
  WAITING_FOR_SAME_PROJECT_ZIP_CAPTURE: 'WAITING_FOR_SAME_PROJECT_ZIP_CAPTURE',
  HELD_FOR_ZIP: 'HELD_FOR_ZIP', // Backward compatibility alias
  PASTING: 'PASTING',
  PASTED: 'PASTED',
  SUBMITTING: 'SUBMITTING',
  SUBMISSION_CONFIRMED: 'SUBMISSION_CONFIRMED',
  EXECUTING: 'EXECUTING',
  COMPLETED: 'COMPLETED',
  RETRYABLE_FAILURE: 'RETRYABLE_FAILURE',
  RECOVERY_IN_PROGRESS: 'RECOVERY_IN_PROGRESS',
  EXECUTION_UNCERTAIN: 'EXECUTION_UNCERTAIN',
  TERMINAL_UNAVAILABLE: 'TERMINAL_UNAVAILABLE',
  FAILED_WITH_EVIDENCE: 'FAILED_WITH_EVIDENCE'
};

// Per-window serialization structures
const windowDeliveryQueues = {};
const windowDeliveryActive = {};

/**
 * Dynamic bounded settling delay based on prompt size
 * Short prompts (<500 bytes): ~150ms
 * 14 KB prompts: ~640ms
 * 100 KB prompts: ~2500ms (capped)
 */
function calculateSettlingDelayMs(promptByteLength, targetWindow) {
  const baseDelay = 150;
  const perKbDelay = 35;
  const kb = Math.ceil(promptByteLength / 1024);
  const computed = baseDelay + (kb * perKbDelay);
  return Math.min(2500, Math.max(150, computed));
}

/**
 * Authoritative Codex Telemetry Check
 * Inspects ~/.codex/history.jsonl for exact prompt submission record
 */
function checkCodexSubmissionTelemetry(promptText, submitTimeEpochMs) {
  const historyFile = path.join(USER_HOME, '.codex', 'history.jsonl');
  if (!fs.existsSync(historyFile)) return null;
  try {
    const content = fs.readFileSync(historyFile, 'utf8');
    const lines = content.trim().split('\n');
    const submitSec = Math.floor(submitTimeEpochMs / 1000);
    const cleanPrompt = (promptText || '').trim();
    const promptPrefix = cleanPrompt.substring(0, 45);

    for (let i = lines.length - 1; i >= Math.max(0, lines.length - 15); i--) {
      try {
        const item = JSON.parse(lines[i]);
        if (item && item.ts && (item.ts >= submitSec - 3)) {
          const textVal = item.text || item.display || '';
          if (textVal && (textVal.includes(promptPrefix) || promptPrefix.includes(textVal.substring(0, 35)))) {
            return {
              confirmed: true,
              source: 'codex_history',
              ts: item.ts,
              sessionId: item.session_id,
              textMatched: promptPrefix
            };
          }
        }
      } catch (e) {}
    }
  } catch (e) {}
  return null;
}

/**
 * Authoritative Antigravity (AGY) Telemetry Check
 * Inspects ~/.gemini/antigravity-cli/history.jsonl for exact prompt submission record
 */
function checkAgySubmissionTelemetry(promptText, submitTimeEpochMs) {
  const historyFile = path.join(USER_HOME, '.gemini', 'antigravity-cli', 'history.jsonl');
  if (!fs.existsSync(historyFile)) return null;
  try {
    const content = fs.readFileSync(historyFile, 'utf8');
    const lines = content.trim().split('\n');
    const cleanPrompt = (promptText || '').trim();
    const promptPrefix = cleanPrompt.substring(0, 45);

    for (let i = lines.length - 1; i >= Math.max(0, lines.length - 15); i--) {
      try {
        const item = JSON.parse(lines[i]);
        if (item && item.timestamp && (item.timestamp >= submitTimeEpochMs - 4000)) {
          const textVal = item.display || item.text || '';
          if (textVal && (textVal.includes(promptPrefix) || promptPrefix.includes(textVal.substring(0, 35)))) {
            return {
              confirmed: true,
              source: 'agy_history',
              timestamp: item.timestamp,
              conversationId: item.conversationId,
              textMatched: promptPrefix
            };
          }
        }
      } catch (e) {}
    }
  } catch (e) {}
  return null;
}

/**
 * Visual Supporting Evidence via tmux capture-pane
 */
function inspectPaneState(targetWindow) {
  try {
    const pane = execSync(`tmux capture-pane -p -t ${targetWindow} -S -25`, {
      encoding: 'utf8',
      timeout: 2500
    });
    const isExecuting = pane.includes('Working...') ||
                        pane.includes('Thinking...') ||
                        pane.includes('Generating...') ||
                        pane.includes('◦ Working') ||
                        pane.includes('• Working') ||
                        pane.includes('esc to interrupt') ||
                        pane.includes('esc to cancel') ||
                        /[⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏]/.test(pane);

    const isIdle = pane.includes('› Ask Codex to do anything') ||
                   pane.includes('Your move, teammate.') ||
                   pane.includes('? for shortcuts') ||
                   /(?:^|\n)\s*>\s*$/.test(pane);

    const hasPastedPill = pane.includes('[Pasted Content ') || pane.includes('chars]');

    return {
      success: true,
      isExecuting,
      isIdle,
      hasPastedPill,
      rawTail: pane.split('\n').filter(Boolean).slice(-6).join('\n')
    };
  } catch (err) {
    return { success: false, error: err.message };
  }
}

/**
 * Check if the target terminal is available
 */
function ensureTargetTerminalAvailable(targetWindow) {
  try {
    execFileSync('tmux', ['list-panes', '-t', targetWindow], { stdio: 'ignore' });
    return true;
  } catch (e) {
    // Attempt session init
    try {
      const initScript = path.join(USER_HOME, '.webterminal', 'init_agy_sessions.sh');
      if (fs.existsSync(initScript)) {
        execFileSync('/bin/bash', [initScript], { stdio: 'ignore', timeout: 5000 });
        execFileSync('tmux', ['list-panes', '-t', targetWindow], { stdio: 'ignore' });
        return true;
      }
    } catch (initErr) {
      return false;
    }
    return false;
  }
}

/**
 * Execute actual terminal transport for a single item
 */
async function executeTerminalDelivery(item, handlers) {
  const { target_window: targetWindow, prompt, message_id: mId } = item;
  const cleanPrompt = (prompt || '').trim();
  const safeTarget = targetWindow.replace(/[^a-zA-Z0-9]/g, '_');
  const cmdFile = path.join(USER_HOME, '.webterminal', `incoming_cmd_${safeTarget}.txt`);

  // Step 1: Ensure terminal is available
  if (!ensureTargetTerminalAvailable(targetWindow)) {
    const errorMsg = `Target window ${targetWindow} not accessible in tmux`;
    console.error(`[PromptDelivery] ❌ ${errorMsg}`);
    handlers.updateStatus(mId, DELIVERY_STATES.TERMINAL_UNAVAILABLE, { error: errorMsg });
    return { success: false, state: DELIVERY_STATES.TERMINAL_UNAVAILABLE, error: errorMsg };
  }

  handlers.updateStatus(mId, DELIVERY_STATES.READY);

  const isSlashCommand = /^\/[a-zA-Z0-9_-]+(\s+[\s\S]*)?$/.test(cleanPrompt);

  if (isSlashCommand) {
    // Slash command fast path (literal keystroke typing)
    handlers.updateStatus(mId, DELIVERY_STATES.SUBMITTING);
    try {
      execFileSync('tmux', ['send-keys', '-t', targetWindow, '-l', cleanPrompt]);
      execFileSync('tmux', ['send-keys', '-t', targetWindow, 'Enter']);
      console.log(`[PromptDelivery] ⌨️ Forwarded slash command to ${targetWindow}: ${cleanPrompt}`);

      await new Promise(r => setTimeout(r, 250));
      handlers.updateStatus(mId, DELIVERY_STATES.SUBMISSION_CONFIRMED, { method: 'slash_keystroke' });
      handlers.updateStatus(mId, DELIVERY_STATES.EXECUTING);
      if (handlers.onConfirmed) handlers.onConfirmed(item);
      return { success: true, state: DELIVERY_STATES.SUBMISSION_CONFIRMED };
    } catch (err) {
      handlers.updateStatus(mId, DELIVERY_STATES.FAILED_WITH_EVIDENCE, { error: err.message });
      return { success: false, state: DELIVERY_STATES.FAILED_WITH_EVIDENCE, error: err.message };
    }
  }

  // Step 2: Buffer preparation (PASTING)
  handlers.updateStatus(mId, DELIVERY_STATES.PASTING);
  const normalizedPrompt = cleanPrompt.replace(/\r\n/g, '\n');
  const promptBytes = Buffer.byteLength(normalizedPrompt, 'utf8');

  try {
    const dir = path.dirname(cmdFile);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(cmdFile, normalizedPrompt, 'utf8');
  } catch (err) {
    handlers.updateStatus(mId, DELIVERY_STATES.FAILED_WITH_EVIDENCE, { error: `Failed to write cmd file: ${err.message}` });
    return { success: false, state: DELIVERY_STATES.FAILED_WITH_EVIDENCE, error: err.message };
  }

  const bufName = `wa_cmd_${safeTarget}_${Date.now()}`;
  try {
    execFileSync('tmux', ['load-buffer', '-b', bufName, cmdFile]);
    execFileSync('tmux', ['paste-buffer', '-p', '-r', '-b', bufName, '-t', targetWindow]);
    try { execFileSync('tmux', ['delete-buffer', '-b', bufName]); } catch (e) {}
  } catch (err) {
    handlers.updateStatus(mId, DELIVERY_STATES.FAILED_WITH_EVIDENCE, { error: `Tmux paste error: ${err.message}` });
    return { success: false, state: DELIVERY_STATES.FAILED_WITH_EVIDENCE, error: err.message };
  }

  // Step 3: Bounded Asynchronous Settling Delay (PASTED)
  handlers.updateStatus(mId, DELIVERY_STATES.PASTED);
  const settlingDelayMs = calculateSettlingDelayMs(promptBytes, targetWindow);
  console.log(`[PromptDelivery] ⏳ Settling delay on ${targetWindow}: ${settlingDelayMs}ms for ${promptBytes} bytes`);
  await new Promise(resolve => setTimeout(resolve, settlingDelayMs));

  // Step 4: Submission (SUBMITTING)
  handlers.updateStatus(mId, DELIVERY_STATES.SUBMITTING);
  const submitTime = Date.now();
  try {
    execFileSync('tmux', ['send-keys', '-t', targetWindow, 'Enter']);
    console.log(`[PromptDelivery] ⏎ Pressed Enter on ${targetWindow} after ${settlingDelayMs}ms settling`);
  } catch (err) {
    handlers.updateStatus(mId, DELIVERY_STATES.FAILED_WITH_EVIDENCE, { error: `Tmux send-keys Enter error: ${err.message}` });
    return { success: false, state: DELIVERY_STATES.FAILED_WITH_EVIDENCE, error: err.message };
  }

  // Step 5: Authoritative Telemetry & Execution Verification
  const isCodex = targetWindow.includes('codex');
  let confirmed = false;
  let evidence = null;
  const maxVerificationTimeMs = 3500;
  const pollIntervalMs = 200;
  const startPoll = Date.now();

  while (Date.now() - startPoll < maxVerificationTimeMs) {
    await new Promise(r => setTimeout(r, pollIntervalMs));

    // Telemetry check
    if (isCodex) {
      const cCheck = checkCodexSubmissionTelemetry(normalizedPrompt, submitTime);
      if (cCheck && cCheck.confirmed) {
        confirmed = true;
        evidence = cCheck;
        break;
      }
    } else {
      const aCheck = checkAgySubmissionTelemetry(normalizedPrompt, submitTime);
      if (aCheck && aCheck.confirmed) {
        confirmed = true;
        evidence = aCheck;
        break;
      }
    }

    // Supporting visual state check
    const pState = inspectPaneState(targetWindow);
    if (pState.success && pState.isExecuting) {
      confirmed = true;
      evidence = { confirmed: true, source: 'pane_visual_executing', rawTail: pState.rawTail };
      break;
    }
  }

  if (confirmed) {
    console.log(`[PromptDelivery] ✅ Submission confirmed on ${targetWindow} via ${evidence.source}`);
    handlers.updateStatus(mId, DELIVERY_STATES.SUBMISSION_CONFIRMED, { evidence });
    handlers.updateStatus(mId, DELIVERY_STATES.EXECUTING);
    if (handlers.onConfirmed) handlers.onConfirmed(item);
    return { success: true, state: DELIVERY_STATES.SUBMISSION_CONFIRMED, evidence };
  }

  // Step 6: Safe Autonomous Recovery Check
  console.log(`[PromptDelivery] ⚠️ Submission not detected after ${maxVerificationTimeMs}ms on ${targetWindow}. Auditing pane state...`);
  const finalPaneCheck = inspectPaneState(targetWindow);

  // If the composer definitely still holds the unsubmitted prompt or pill and NO execution occurred:
  if (finalPaneCheck.success && (finalPaneCheck.hasPastedPill || finalPaneCheck.isIdle) && !finalPaneCheck.isExecuting) {
    console.log(`[PromptDelivery] 🔄 Pane audit confirms prompt still sitting in composer on ${targetWindow}. Initiating safe single Enter recovery...`);
    handlers.updateStatus(mId, DELIVERY_STATES.RECOVERY_IN_PROGRESS, { attempt: 1 });

    await new Promise(r => setTimeout(r, 400));
    try {
      execFileSync('tmux', ['send-keys', '-t', targetWindow, 'Enter']);
    } catch (e) {}

    // Check confirmation again
    await new Promise(r => setTimeout(r, 1500));
    let recoverConfirmed = false;
    if (isCodex) {
      const c2 = checkCodexSubmissionTelemetry(normalizedPrompt, submitTime);
      if (c2 && c2.confirmed) recoverConfirmed = true;
    } else {
      const a2 = checkAgySubmissionTelemetry(normalizedPrompt, submitTime);
      if (a2 && a2.confirmed) recoverConfirmed = true;
    }
    const p2 = inspectPaneState(targetWindow);
    if (p2.success && p2.isExecuting) recoverConfirmed = true;

    if (recoverConfirmed) {
      console.log(`[PromptDelivery] ✅ Autonomous recovery succeeded on ${targetWindow}!`);
      handlers.updateStatus(mId, DELIVERY_STATES.SUBMISSION_CONFIRMED, { recovered: true });
      handlers.updateStatus(mId, DELIVERY_STATES.EXECUTING);
      if (handlers.onConfirmed) handlers.onConfirmed(item);
      return { success: true, state: DELIVERY_STATES.SUBMISSION_CONFIRMED, recovered: true };
    }
  }

  // Step 7: Preserve Explicit Uncertainty (Never blind retry, never duplicate execute)
  const uncertaintyEvidence = {
    paneState: finalPaneCheck,
    promptBytes,
    submitTime: new Date(submitTime).toISOString()
  };
  console.warn(`[PromptDelivery] 🚨 Execution uncertain on ${targetWindow}. Preserving message state without duplicate replay.`);
  handlers.updateStatus(mId, DELIVERY_STATES.EXECUTION_UNCERTAIN, { evidence: uncertaintyEvidence });
  if (handlers.onUncertain) handlers.onUncertain(item, uncertaintyEvidence);
  return { success: false, state: DELIVERY_STATES.EXECUTION_UNCERTAIN, evidence: uncertaintyEvidence };
}

/**
 * Process the queue for a given target window sequentially
 */
async function processWindowQueue(targetWindow, handlers) {
  if (windowDeliveryActive[targetWindow]) return;
  windowDeliveryActive[targetWindow] = true;

  try {
    const queue = windowDeliveryQueues[targetWindow] || [];
    while (queue.length > 0) {
      const item = queue.shift();
      if (!item) continue;

      try {
        await executeTerminalDelivery(item, handlers);
      } catch (err) {
        console.error(`[PromptDelivery] Unexpected error processing ${item.message_id} on ${targetWindow}:`, err);
        handlers.updateStatus(item.message_id, DELIVERY_STATES.FAILED_WITH_EVIDENCE, { error: err.message });
      }
    }
  } finally {
    windowDeliveryActive[targetWindow] = false;
  }
}

/**
 * Main Entry Point for Dispatching a Prompt
 */
function enqueueAndDeliverPrompt(item, handlers) {
  const targetWindow = item.target_window || 'agy:0';
  if (!windowDeliveryQueues[targetWindow]) {
    windowDeliveryQueues[targetWindow] = [];
  }

  // Enqueue in memory queue for serialized execution on this window
  windowDeliveryQueues[targetWindow].push(item);

  // Trigger processing asynchronously without blocking caller
  setImmediate(() => {
    processWindowQueue(targetWindow, handlers).catch(err => {
      console.error(`[PromptDelivery] Queue error on ${targetWindow}:`, err);
    });
  });

  return true;
}

module.exports = {
  DELIVERY_STATES,
  calculateSettlingDelayMs,
  checkCodexSubmissionTelemetry,
  checkAgySubmissionTelemetry,
  inspectPaneState,
  ensureTargetTerminalAvailable,
  executeTerminalDelivery,
  enqueueAndDeliverPrompt
};
