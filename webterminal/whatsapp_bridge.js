const fs = require('fs');
const path = require('path');
const https = require('https');
const { execSync, exec, execFile } = require('child_process');

const baileysPath = path.join(__dirname, 'node_modules/@whiskeysockets/baileys');
const baileys = require(baileysPath);
const { default: makeWASocket, useMultiFileAuthState, DisconnectReason } = baileys;
const pino = require('pino');
const { defaultController: autoController } = require('./autonomous_interaction_controller');

const AUTH_DIR = '/home/azureuser/.webterminal/wa_auth';
const TARGET_PHONE_FILE = '/home/azureuser/.webterminal/target_phone.txt';
const PAIRING_FILE = '/home/azureuser/.webterminal/pairing_code.txt';
const LATEST_REPLY_FILE = '/home/azureuser/.webterminal/latest_reply.json';
const WA_OUTBOX_DIR = '/home/azureuser/.webterminal/wa_outbox';

function getTargetPhone() {
  if (fs.existsSync(TARGET_PHONE_FILE)) {
    const p = fs.readFileSync(TARGET_PHONE_FILE, 'utf8').trim().replace(/[^0-9]/g, '');
    if (p.length >= 10) return p;
  }
  return '8801955333555';
}

const TARGET_PHONE = getTargetPhone();
const ALLOWED_NUMBERS = ['8801955333555', '8801966608406', '206343935946909', '82935919157317', TARGET_PHONE];
let TARGET_JID = `${TARGET_PHONE}@s.whatsapp.net`;

const BRIDGE_START_TIME = Math.floor(Date.now() / 1000);
const sentMessageIds = new Set();
const processedIncomingMessageIds = new Set();
const PROCESSED_MSG_FILE = '/home/azureuser/.webterminal/processed_msg_ids.json';

function loadProcessedMessageIds() {
  try {
    if (fs.existsSync(PROCESSED_MSG_FILE)) {
      const data = JSON.parse(fs.readFileSync(PROCESSED_MSG_FILE, 'utf8'));
      if (Array.isArray(data)) {
        data.forEach(id => processedIncomingMessageIds.add(id));
      }
    }
  } catch (e) {
    console.warn('[WA Bridge] Could not load processed_msg_ids.json:', e.message);
  }
}

function saveProcessedMessageIds() {
  try {
    const list = Array.from(processedIncomingMessageIds).slice(-3000);
    fs.writeFileSync(PROCESSED_MSG_FILE, JSON.stringify(list), 'utf8');
  } catch (e) {}
}

loadProcessedMessageIds();

let sock = null;
let lastActiveJid = '82935919157317@lid';
let lastPersonalLid = '82935919157317@lid';
let isWsConnected = false;
let lastUserMsgKey = null;
let lastUserMsg = null;
const lastUserMsgByWindow = {};
const lastUserMsgKeyByWindow = {};
const lastUserPromptByWindow = {};
const auditInProgressByWindow = {};
const auditCycleByWindow = {};

const windowBusy = {};
const windowBusySince = {};
const lastWaDispatchedPromptByWindow = {};
const os = require('os');
const QUEUE_FILE = process.env.PROMPT_QUEUE_FILE || path.join(os.homedir(), '.webterminal', 'prompt_queue.json');

// Bangla notification constants (Authoritative from ORIGINAL_REQUEST.md & PROJECT.md)
const BANGLA_ZIP_HOLD_NOTICE = "এই project-এর ZIP backup চলছে।\nআপনার prompt নিরাপদে queued আছে।\nZIP capture শেষ হলেই স্বয়ংক্রিয়ভাবে পাঠানো হবে।";
const BANGLA_ZIP_COMPLETE_NOTICE = "ZIP capture শেষ হয়েছে। অপেক্ষমান prompt পাঠানো হয়েছে।";
const BANGLA_RECONNECT_TEMPLATE = "WhatsApp সংযোগ ফিরে এসেছে।\nঅপেক্ষমান {count}টি message আবার processing শুরু হয়েছে।";

let promptQueue = []; // In-memory mirror for backward compatibility
let mediaBatch = [];
let mediaBatchTimer = null;

function loadDurableQueue() {
  try {
    if (fs.existsSync(QUEUE_FILE)) {
      const data = JSON.parse(fs.readFileSync(QUEUE_FILE, 'utf8'));
      if (Array.isArray(data)) return data;
    }
  } catch (err) {
    console.error('[WA Bridge] Error loading durable queue:', err.message);
  }
  return [];
}

function saveDurableQueue(queue) {
  try {
    const dir = path.dirname(QUEUE_FILE);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    const tmp = `${QUEUE_FILE}.${process.pid}.${Date.now()}.tmp`;
    fs.writeFileSync(tmp, JSON.stringify(queue, null, 2), 'utf8');
    fs.renameSync(tmp, QUEUE_FILE);
  } catch (err) {
    console.error('[WA Bridge] Error saving durable queue:', err.message);
  }
}

function enqueueDurablePrompt(item) {
  const queue = loadDurableQueue();
  const existingIdx = queue.findIndex(q => q.message_id === item.message_id);
  if (existingIdx !== -1) {
    queue[existingIdx] = { ...queue[existingIdx], ...item, updated_at: new Date().toISOString() };
  } else {
    const maxSeq = queue.reduce((m, q) => Math.max(m, q.sequence || 0), 0);
    queue.push({
      ...item,
      sequence: maxSeq + 1,
      received_at: item.received_at || new Date().toISOString(),
      updated_at: new Date().toISOString()
    });
  }
  saveDurableQueue(queue);
}

function updateDurablePromptStatus(messageId, status, extra = {}) {
  const queue = loadDurableQueue();
  const item = queue.find(q => q.message_id === messageId);
  if (item) {
    item.status = status;
    item.updated_at = new Date().toISOString();
    Object.assign(item, extra);
    saveDurableQueue(queue);
  }
}

function checkZipGate(targetWindow, projectUuid = null) {
  const sotPath = process.env.SOT_PATH || '/home/azureuser/IroScript_Projects/Infrastructure-Source-of-Truth/sot';
  if (!fs.existsSync(sotPath)) {
    // Daemon-Independent Ordinary Delivery: if SOT binary missing, default to ALLOW_NOW
    return { action: 'ALLOW_NOW', zip_gate: 'ZIP_GATE_OPEN' };
  }
  try {
    const { execFileSync } = require('child_process');
    const args = ['backup-orchestrator', 'gate-check'];
    if (projectUuid) {
      args.push('--project-uuid', projectUuid);
    } else {
      args.push('--route', targetWindow);
    }
    args.push('--json');
    const out = execFileSync('/usr/bin/python3', [sotPath, ...args], {
      encoding: 'utf8',
      timeout: 3000,
      stdio: ['ignore', 'pipe', 'ignore']
    });
    const parsed = JSON.parse(out.trim());
    return parsed || { action: 'ALLOW_NOW', zip_gate: 'ZIP_GATE_OPEN' };
  } catch (err) {
    // Daemon-Independent Ordinary Delivery:
    // If sot CLI errors, times out, or backup daemon is stopped: default to ALLOW_NOW!
    return { action: 'ALLOW_NOW', zip_gate: 'ZIP_GATE_OPEN' };
  }
}

function drainNextPromptForWindow(targetWindow) {
  const queue = loadDurableQueue();
  const heldItems = queue.filter(item => item.target_window === targetWindow && item.status === 'HELD_FOR_ZIP');
  if (heldItems.length > 0) {
    const gateCheck = checkZipGate(targetWindow);
    if (gateCheck && (gateCheck.action === 'ALLOW_NOW' || gateCheck.zip_gate === 'ZIP_GATE_OPEN')) {
      console.log(`[WA Bridge] 🔓 ZIP capture finished for ${targetWindow}. Releasing ${heldItems.length} held prompts.`);
      for (const item of heldItems) {
        item.status = 'RECEIVED';
        item.updated_at = new Date().toISOString();
      }
      saveDurableQueue(queue);

      const recipient = lastActiveJid;
      if (recipient) {
        sendWhatsAppMessage(BANGLA_ZIP_COMPLETE_NOTICE, { to: recipient }).catch(() => {});
      }
    }
  }

  const nextItem = queue.find(item => item.target_window === targetWindow && (item.status === 'RECEIVED' || item.status === 'RETRYING'));
  if (nextItem) {
    console.log(`[WA Bridge] 🔄 Dequeuing durable prompt for ${targetWindow} (${nextItem.message_id}):`, (nextItem.prompt || '').substring(0, 60));
    setTimeout(() => {
      dispatchToTmux(nextItem.prompt, targetWindow, nextItem.message_id, nextItem.reply_context);
    }, 100);
  }
}

function isAgyActuallyIdle(targetWindow = 'agy:0') {
  try {
    const pane = execSync(`tmux capture-pane -p -t ${targetWindow} | tail -n 8`, { encoding: 'utf8', timeout: 2000 });
    if (pane.includes('esc to cancel') || pane.includes('Working...') || pane.includes('Generating...') || pane.includes('Running command') || pane.includes('esc to interrupt') || pane.includes('◦ Working')) {
      return false;
    }
    return pane.includes('? for shortcuts') || pane.includes('Ask Codex to do anything') || pane.includes('Your move, teammate.');
  } catch (e) {
    return false;
  }
}

function isWindowBusy(targetWindow = 'agy:0') {
  if (!windowBusy[targetWindow]) return false;
  if (isAgyActuallyIdle(targetWindow) || (windowBusySince[targetWindow] && Date.now() - windowBusySince[targetWindow] > 180000)) {
    console.log(`[WA Bridge] ℹ️ Detected AGY idle prompt in ${targetWindow} or timeout; clearing stale busy state`);
    windowBusy[targetWindow] = false;
    return false;
  }
  return true;
}

function getWindowForSender(sender) {
  if (!sender) return 'agy:0';
  if (sender.endsWith('@g.us')) {
    const groups = getProjectGroupMap();
    for (const [k, g] of Object.entries(groups)) {
      if (g && g.id === sender) {
        if (k === 'yt') return 'agy:yt';
        if (k === 'frappe') return 'agy:frappe';
        if (k === 'tg') return 'agy:tg';
        if (k === 'history') return 'agy:history';
        if (k === 'kids') return 'agy:kids';
        if (k === 'rust') return 'agy:rust';
        if (k === 'article') return 'agy:article';
        if (k === 'game') return 'agy:game';
        if (k === 'research') return 'agy:research';
        if (k === 'reporting') return 'agy:report';
        if (k === 'codex') return 'agy:codex';
      }
    }
    return 'agy:0';
  }
  // Personal 1-on-1 WhatsApp Chat is with Master Agent (agy:0)
  return 'agy:0';
}

function dispatchToTmux(promptText, targetWindow = 'agy:0', msgId = null, replyContext = null) {
  const cleanPrompt = (promptText || '').trim();
  if (!cleanPrompt) return false;

  const mId = msgId || `wa_${Date.now()}`;

  // 1. Duplicate suppression
  if (msgId && processedIncomingMessageIds.has(msgId)) {
    console.log(`[WA Bridge] 🔁 Prompt ${msgId} was already processed/delivered. Duplicate suppressed.`);
    return false;
  }

  // 2. Gate Inspection (Non-blocking: fallback open if SOT offline or error)
  const gateCheck = checkZipGate(targetWindow);
  if (gateCheck && (gateCheck.action === 'HOLD_FOR_ZIP' || gateCheck.zip_gate === 'ZIP_GATE_CLOSED')) {
    console.log(`[WA Bridge] ⏸️ Prompt gate is CLOSED for ${targetWindow} (project: ${gateCheck.project_uuid || targetWindow}). Holding prompt in durable queue.`);
    enqueueDurablePrompt({
      message_id: mId,
      project_uuid: gateCheck.project_uuid || targetWindow,
      target_window: targetWindow,
      prompt: cleanPrompt,
      status: 'HELD_FOR_ZIP',
      reply_context: replyContext ? { sender: replyContext.sender } : null
    });

    const targetRecipient = (replyContext && replyContext.sender) || lastActiveJid;
    if (targetRecipient) {
      sendWhatsAppMessage(BANGLA_ZIP_HOLD_NOTICE, {
        to: targetRecipient,
        quoted: replyContext ? replyContext.msg : undefined
      }).catch(err => console.error('[WA Bridge] Error sending Bangla ZIP hold notice:', err.message));
    }
    return false;
  }

  // Hold prompts while set_agy_model.sh has the /model picker open on this window
  const modelLock = `/home/azureuser/.webterminal/model_switch_${targetWindow.replace(/[^a-zA-Z0-9]/g, '_')}.lock`;
  try {
    if (fs.existsSync(modelLock) && (Date.now() - fs.statSync(modelLock).mtimeMs) < 60000) {
      console.log(`[WA Bridge] 🧠 Model switch in progress on ${targetWindow}; retrying prompt in 3s`);
      setTimeout(() => dispatchToTmux(promptText, targetWindow, msgId, replyContext), 3000);
      return false;
    }
  } catch (e) {}

  // 3. Busy coding agent handling (Safe input boundary queuing)
  if (isWindowBusy(targetWindow)) {
    console.log(`[WA Bridge] ⏳ AGY is currently busy on ${targetWindow}. Queued prompt into durable queue:`, cleanPrompt.substring(0, 60));
    enqueueDurablePrompt({
      message_id: mId,
      project_uuid: (gateCheck && gateCheck.project_uuid) || targetWindow,
      target_window: targetWindow,
      prompt: cleanPrompt,
      status: 'RECEIVED',
      reply_context: replyContext ? { sender: replyContext.sender } : null
    });
    return false;
  }

  // 4. Sole Terminal Delivery Owner: Bridge directly executes terminal injection
  windowBusy[targetWindow] = true;
  windowBusySince[targetWindow] = Date.now();
  lastWaDispatchedPromptByWindow[targetWindow] = cleanPrompt.replace(/\s+/g, ' ').trim();
  if (!cleanPrompt.startsWith('[OpenAI Codex Peer-Review Audit]')) {
    lastUserPromptByWindow[targetWindow] = cleanPrompt;
    auditCycleByWindow[targetWindow] = 0;
  }

  // Record in durable queue as DELIVERING
  enqueueDurablePrompt({
    message_id: mId,
    project_uuid: (gateCheck && gateCheck.project_uuid) || targetWindow,
    target_window: targetWindow,
    prompt: cleanPrompt,
    status: 'DELIVERING',
    last_attempt_at: new Date().toISOString(),
    reply_context: replyContext ? { sender: replyContext.sender } : null
  });

  // Activate Universal Autonomous Interaction Controller for this target terminal
  autoController.startTracking(targetWindow, cleanPrompt);

  const safeTarget = targetWindow.replace(/[^a-zA-Z0-9]/g, '_');
  const cmdFile = `/home/azureuser/.webterminal/incoming_cmd_${safeTarget}.txt`;
  try {
    fs.writeFileSync(cmdFile, cleanPrompt, 'utf8');
  } catch (e) {}

  try {
    // Ensure target session and window exist before dispatching
    try {
      execSync(`tmux list-panes -t ${targetWindow}`, { stdio: 'ignore' });
    } catch (e) {
      console.log(`[WA Bridge] 🔄 Target ${targetWindow} not ready! Running init_agy_sessions.sh...`);
      try {
        execSync(`/bin/bash /home/azureuser/.webterminal/init_agy_sessions.sh`, { stdio: 'ignore' });
      } catch (err) {}
    }

    const isSlashCommand = /^\/[a-zA-Z0-9_-]+(\s+[\s\S]*)?$/.test(cleanPrompt);
    if (isSlashCommand) {
      // Send string literally, emulating physical keyboard typing with zero shell injection risk
      const { execFileSync } = require('child_process');
      try {
        execFileSync('tmux', ['send-keys', '-t', targetWindow, '-l', cleanPrompt]);
        execFileSync('tmux', ['send-keys', '-t', targetWindow, 'Enter']);
        console.log(`[WA Bridge] ⌨️ Forwarded native slash command to ${targetWindow} via literal keystroke: ${cleanPrompt}`);
      } catch (e) {
        console.error(`[WA Bridge] ❌ Keystroke send error on ${targetWindow}:`, e.message);
      }

      if (cleanPrompt.startsWith('/clear') && replyContext && replyContext.sender) {
        setTimeout(async () => {
          await sendWhatsAppMessage(`🧹 *[সেশন রিস্টার্ট/ক্লিয়ার]*\n> \`${targetWindow}\` সেশনটি ক্লিয়ার করা হয়েছে। নতুন প্রম্পট পাঠাতে পারেন।`, { to: replyContext.sender, quoted: replyContext.msg }).catch(() => {});
        }, 600);
      }
    } else {
      const bufName = `wa_cmd_${safeTarget}`;
      execSync(`tmux load-buffer -b ${bufName} "${cmdFile}" && tmux paste-buffer -p -r -b ${bufName} -t ${targetWindow}`);
      setTimeout(() => {
        try {
          execSync(`tmux send-keys -t ${targetWindow} Enter`);
          console.log(`[WA Bridge] ✅ Forwarded prompt to ${targetWindow} via bracketed paste & pressed Enter!`);
        } catch (e) {
          console.error(`[WA Bridge] ❌ Enter key send error on ${targetWindow}:`, e.message);
        }
        setTimeout(() => {
          try {
            const paneText = execSync(`tmux capture-pane -p -t ${targetWindow} | tail -n 6`, { encoding: 'utf8', timeout: 2000 });
            if (paneText.includes('> ') && !paneText.includes('esc to cancel') && !paneText.includes('Working...') && !paneText.includes('Loading...')) {
              console.log(`[WA Bridge] ⚠️ Prompt still sitting in input prompt on ${targetWindow}, sending backup Enter...`);
              execSync(`tmux send-keys -t ${targetWindow} Enter`);
            }
          } catch (e) {}
        }, 500);
      }, 250);
    }

    // Terminal transport successful: transition DELIVERING -> DELIVERED
    updateDurablePromptStatus(mId, 'DELIVERED');
    if (mId) {
      processedIncomingMessageIds.add(mId);
      saveProcessedMessageIds();
    }
    return true;
  } catch (err) {
    console.error(`[WA Bridge] ❌ Tmux forward error on ${targetWindow}:`, err.message);
    windowBusy[targetWindow] = false;
    updateDurablePromptStatus(mId, 'RETRYING', { last_error: err.message, retry_count: 1 });
    return false;
  }
}

function getVerifiedModelInfo(targetWindow = 'agy:0') {
  let modelCandidates = [];

  // 1. Way 1: Live Tmux Status Bar Pane inspection
  try {
    const paneLines = execSync(`tmux capture-pane -p -t ${targetWindow} | tail -n 8`, { encoding: 'utf8', timeout: 3000 }).split('\n');
    for (let i = paneLines.length - 1; i >= 0; i--) {
      const line = paneLines[i].trim();
      if (line.includes('Gemini') || line.includes('Flash') || line.includes('Pro') || line.includes('Claude') || line.includes('GPT')) {
        const parts = line.split(/\s{2,}/);
        const candidate = parts[parts.length - 1].trim();
        if (candidate && !candidate.startsWith('>') && !candidate.startsWith('esc')) {
          modelCandidates.push({ source: 'tmux', val: candidate });
          break;
        }
      }
    }
  } catch (e) {}

  // 2. Way 2: Antigravity CLI Settings (settings.json)
  try {
    const settingsPath = '/home/azureuser/.gemini/antigravity-cli/settings.json';
    if (fs.existsSync(settingsPath)) {
      const settings = JSON.parse(fs.readFileSync(settingsPath, 'utf8'));
      if (settings.model) {
        modelCandidates.push({ source: 'settings', val: settings.model.trim() });
      }
    }
  } catch (e) {}

  // 3. Way 3: Antigravity CLI Runtime Log
  try {
    const logCmd = `ls -t /home/azureuser/.gemini/antigravity-cli/log/cli-*.log 2>/dev/null | head -n 1`;
    const latestLog = execSync(logCmd, { encoding: 'utf8' }).trim();
    if (latestLog && fs.existsSync(latestLog)) {
      const logContent = execSync(`grep -i 'Propagating selected model override' "${latestLog}" | tail -n 1`, { encoding: 'utf8' }).trim();
      const match = logContent.match(/label=\"([^\"]+)\"/);
      if (match && match[1]) {
        modelCandidates.push({ source: 'log', val: match[1].trim() });
      }
    }
  } catch (e) {}

  // Fallback if none found
  let rawChoice = 'Gemini 3.8 Flash (High)';
  if (modelCandidates.length > 0) {
    const tmuxCand = modelCandidates.find(c => c.source === 'tmux');
    const settingsCand = modelCandidates.find(c => c.source === 'settings');
    const logCand = modelCandidates.find(c => c.source === 'log');
    rawChoice = (tmuxCand || settingsCand || logCand).val;
  }

  // Parse model and mode
  let modelName = 'Gemini 3.8 Flash';
  let modeName = 'HIGH';

  // FIX 2026-10-03: check the tmux "·" format FIRST (status bar may contain "1 task(s)")
  if (rawChoice.includes('·')) {
    const parts = rawChoice.split('·');
    modelName = parts[0].trim();
    modeName = (parts[1] || 'HIGH').trim().toUpperCase();
  } else if (/^(.*?)\s*\((.*?)\)$/.test(rawChoice.trim())) {
    const m = rawChoice.trim().match(/^(.*?)\s*\((.*?)\)$/);
    modelName = m[1].trim();
    modeName = m[2].trim().toUpperCase();
  } else {
    modelName = rawChoice.trim();
  }

  console.log(`[WA Bridge] 🎯 3-Way Model Verification (${targetWindow}):`, JSON.stringify(modelCandidates), `=> ${modelName} [${modeName}]`);
  return { modelName, modeName, raw: rawChoice, candidates: modelCandidates };
}

function buildHeaderBox(modelLabel) {
  const modelUpper = (modelLabel || 'AGY ASSISTANT').toUpperCase();
  const width = 34; // internal content width
  
  function center(text, w) {
    const pad = Math.max(0, w - text.length);
    const left = Math.floor(pad / 2);
    const right = pad - left;
    return ' '.repeat(left) + text + ' '.repeat(right);
  }

  const borderTop = '╔' + '═'.repeat(width) + '╗';
  const borderBottom = '╚' + '═'.repeat(width) + '╝';
  const emptyLine = '║' + ' '.repeat(width) + '║';
  
  const line1 = '║' + center('🤖 A G Y', width) + '║';
  const line2 = '║' + center('ANTIGRAVITY INTELLIGENCE', width) + '║';
  const line3 = '║' + center(modelUpper, width) + '║';
  const line4 = '║' + center('● CORE ONLINE  ● VERIFIED', width) + '║';
  
  return '```\n' + [
    borderTop,
    emptyLine,
    line1,
    line2,
    emptyLine,
    line3,
    line4,
    emptyLine,
    borderBottom
  ].join('\n') + '\n```\n\n';
}

function buildSignatureBox() {
  const width = 30;
  function center(text, w) {
    const pad = Math.max(0, w - text.length);
    const left = Math.floor(pad / 2);
    const right = pad - left;
    return ' '.repeat(left) + text + ' '.repeat(right);
  }

  const borderTop = '╔' + '═'.repeat(width) + '╗';
  const borderBottom = '╚' + '═'.repeat(width) + '╝';
  const emptyLine = '║' + ' '.repeat(width) + '║';
  const line1 = '║' + center('A N T I G R A V I T Y', width) + '║';
  const line2 = '║' + center('◉ AGY ENGINE ◉', width) + '║';

  const sealBorder = '«' + '━'.repeat(24);
  const sealClose  = '━'.repeat(24) + '»';

  return [
    borderTop,
    emptyLine,
    line1,
    emptyLine,
    line2,
    emptyLine,
    borderBottom,
    sealBorder,
    '✓ VERIFIED',
    '✓ PROCESSED',
    '✓ RESPONSE SEALED',
    sealClose
  ].join('\n');
}

function buildDynamicExecutionMatrix(turnTools, hasThinking, thinkingLength) {
  const stages = ['INPUT'];

  // Thinking / Analysis stages
  if (hasThinking) {
    stages.push('ANALYZE');
    if (thinkingLength && thinkingLength > 800) {
      stages.push('DEEP THINK');
      stages.push('PLAN');
    }
  }

  function getStageForTool(toolItem) {
    const name = typeof toolItem === 'string' ? toolItem : toolItem.name;
    const args = (typeof toolItem === 'object' && toolItem.args) ? toolItem.args : {};
    const cmd = (args.CommandLine || '').toLowerCase();
    const summary = (args.toolSummary || '').toLowerCase();
    const action = (args.toolAction || '').toLowerCase();

    if (name === 'run_command') {
      if (cmd.includes('calc') || cmd.includes('expr ') || cmd.includes('bc ') || cmd.includes('math.')) return 'CALCULATE';
      if (cmd.includes('diff ') || cmd.includes('compare') || summary.includes('compare') || action.includes('compare')) return 'COMPARE';
      if (cmd.includes('pytest') || cmd.includes('jest') || cmd.includes('test') || summary.includes('test') || action.includes('test')) return 'TEST';
      if (cmd.includes('node -c') || cmd.includes('syntax') || cmd.includes('tsc') || cmd.includes('eslint') || summary.includes('validate') || action.includes('validate')) return 'VALIDATE';
      if (cmd.includes('status') || cmd.includes('verify') || cmd.includes('curl ') || cmd.includes('check') || summary.includes('status') || summary.includes('verify') || summary.includes('check')) return 'VERIFY';
      if (cmd.includes('systemctl restart') || cmd.includes('systemctl reload') || cmd.includes('deploy')) return 'DEPLOY';
      if (cmd.includes('git ')) return 'VCS';
      if (cmd.includes('wget ') || cmd.includes('http')) return 'NETWORK';
      return 'PROCESS';
    }
    if (name === 'replace_file_content') return 'MODIFY';
    if (name === 'write_to_file') return 'CREATE';
    if (name === 'view_file' || name === 'list_dir') return 'INSPECT';
    if (name === 'grep_search' || name === 'find_by_name') return 'SEARCH';
    if (name === 'search_web') return 'RESEARCH';
    if (name === 'read_url_content') return 'FETCH';
    if (name === 'manage_task') return 'TASK';
    if (name === 'ask_question') return 'CLARIFY';
    if (name === 'invoke_subagent') return 'DELEGATE';
    return 'PROCESS';
  }

  let searchInspectCount = 0;
  for (const item of turnTools) {
    const stage = getStageForTool(item);
    if (stage === 'SEARCH' || stage === 'INSPECT' || stage === 'RESEARCH' || stage === 'FETCH') {
      searchInspectCount++;
    }
    if (!stages.includes(stage)) {
      stages.push(stage);
    }
  }

  if (searchInspectCount >= 2 && !stages.includes('CROSS-CHECK')) {
    stages.push('CROSS-CHECK');
  }

  stages.push('RESPOND');
  stages.push('SEAL');

  let out = '╔═ EXECUTION MATRIX ═╗\n';
  stages.forEach((s, idx) => {
    const num = String(idx + 1).padStart(2, '0');
    out += `${num} ◉ ${s}\n`;
  });
  out += '╚════════════════════╝';
  return out;
}

function formatMarkdownForWhatsApp(text) {
  if (!text) return text;
  let out = text;

  // Protect code blocks (``` ... ```) and inline code (` ... `)
  const codeBlocks = [];
  out = out.replace(/```[\s\S]*?```/g, (m) => {
    codeBlocks.push(m);
    return `___CODE_BLOCK_${codeBlocks.length - 1}___`;
  });

  const inlineCodes = [];
  out = out.replace(/`[^`\n]+`/g, (m) => {
    inlineCodes.push(m);
    return `___INLINE_CODE_${inlineCodes.length - 1}___`;
  });

  // 1. Triple bold/italic: ***text*** -> _*text*_
  out = out.replace(/\*\*\*([^\*\n]+?)\*\*\*/g, '_*$1*_');

  // 2. Double bold: **text** -> *text*
  out = out.replace(/\*\*([^\*\n]+?)\*\*/g, '*$1*');

  // 3. Parentheses around bold: (*text*) or (**text**) -> *(text)*
  out = out.replace(/\(\*([^\*\n]+?)\*\)/g, '*($1)*');

  // 4. Clean up bullet list markers with bold:
  // e.g. '* *bold*' or '- *bold*' -> '• *bold*'
  out = out.replace(/^[ \t]*[\*\-][ \t]+\*([^\*\n]+?)\*/gm, '• *$1*');

  // 5. Headings: ### Heading -> *Heading*
  out = out.replace(/^#{1,6}\s+(.+)$/gm, '*$1*');

  // 6. Clean any lingering double asterisks outside code
  while (out.includes('**')) {
    out = out.replace(/\*\*/g, '*');
  }

  // 7. Clamp decorative borders (e.g. ━━━━━━━━, ════════, ────────, --------)
  out = out.replace(/^([«\s]*)([━═─\-_*=~]{4,})([»\s]*)$/gm, (m, left, border, right) => {
    const char = border[0];
    const borderLen = Math.min(border.length, Math.max(16, 30 - left.length - right.length));
    return left + char.repeat(borderLen) + right;
  });

  // Restore inline codes
  out = out.replace(/___INLINE_CODE_(\d+)___/g, (_, i) => inlineCodes[Number(i)]);

  // Restore code blocks
  out = out.replace(/___CODE_BLOCK_(\d+)___/g, (_, i) => codeBlocks[Number(i)]);

  return out;
}

/**
 * Mobile-optimized text wrapper.
 * Wraps text so that lines comfortably fit mobile viewports (~48-50 chars).
 * Clamps decorative borders/dividers to max 30 characters.
 * Intelligently wraps paragraphs, bullet lists, code blocks, and long file paths.
 */
function wrapForMobile(text, maxWidth = 48) {
  if (!text) return '';
  const lines = text.split('\n');
  const result = [];
  let inCodeBlock = false;

  for (let line of lines) {
    if (line.trim().startsWith('```') || line.trim().startsWith("'''")) {
      inCodeBlock = !inCodeBlock;
      result.push(line);
      continue;
    }

    if (inCodeBlock) {
      if (line.length <= maxWidth) {
        result.push(line);
      } else {
        const wrappedCode = wrapLinePreservingIndent(line, maxWidth);
        result.push(...wrappedCode);
      }
      continue;
    }

    // 1. Clamp decorative borders / dividers
    const dividerMatch = line.match(/^([«\s]*)([━═─\-_*=~]{4,})([»\s]*)$/);
    if (dividerMatch) {
      const left = dividerMatch[1] || '';
      const char = dividerMatch[2][0];
      const right = dividerMatch[3] || '';
      const borderLen = Math.min(dividerMatch[2].length, Math.max(16, 30 - left.length - right.length));
      result.push(left + char.repeat(borderLen) + right);
      continue;
    }

    // 2. Short lines that don't exceed maxWidth
    if (line.length <= maxWidth) {
      result.push(line);
      continue;
    }

    // 3. Bullet points and numbered lists
    const listMatch = line.match(/^(\s*(?:[•\-*]|\d+\.|\>\s*[•\-*]?)\s*)(.*)$/);
    if (listMatch) {
      const prefix = listMatch[1];
      const body = listMatch[2];
      const indent = ' '.repeat(Math.min(prefix.length, 3));
      const firstLimit = Math.max(20, maxWidth - prefix.length);
      const nextLimit = Math.max(20, maxWidth - indent.length);
      const wrapped = wrapParagraph(body, firstLimit, nextLimit);
      if (wrapped.length > 0) {
        result.push(prefix + wrapped[0]);
        for (let j = 1; j < wrapped.length; j++) {
          result.push(indent + wrapped[j]);
        }
      }
      continue;
    }

    // 4. Standard paragraph or heading
    const wrapped = wrapParagraph(line, maxWidth, maxWidth);
    result.push(...wrapped);
  }

  return result.join('\n');
}

function wrapParagraph(text, firstLineWidth, nextLineWidth) {
  if (!text) return [];
  const words = text.split(/\s+/).filter(w => w.length > 0);
  if (words.length === 0) return [''];

  const lines = [];
  let currentLine = '';
  let curLimit = firstLineWidth;

  for (const word of words) {
    if (word.length > curLimit) {
      if (currentLine) {
        lines.push(currentLine);
        currentLine = '';
        curLimit = nextLineWidth;
      }
      const chunks = breakLongToken(word, curLimit);
      for (let i = 0; i < chunks.length - 1; i++) {
        lines.push(chunks[i]);
      }
      currentLine = chunks[chunks.length - 1];
      curLimit = nextLineWidth;
      continue;
    }

    if (!currentLine) {
      currentLine = word;
    } else if ((currentLine.length + 1 + word.length) <= curLimit) {
      currentLine += ' ' + word;
    } else {
      lines.push(currentLine);
      currentLine = word;
      curLimit = nextLineWidth;
    }
  }

  if (currentLine) {
    lines.push(currentLine);
  }

  return lines;
}

function breakLongToken(token, maxLen) {
  const chunks = [];
  let remaining = token;

  while (remaining.length > maxLen) {
    let splitIdx = -1;
    for (let i = maxLen; i >= Math.floor(maxLen * 0.4); i--) {
      if (remaining[i] === '/' || remaining[i] === '_' || remaining[i] === '-' || remaining[i] === ':' || remaining[i] === ',') {
        splitIdx = i + 1;
        break;
      }
    }
    if (splitIdx === -1) {
      splitIdx = maxLen;
    }
    chunks.push(remaining.substring(0, splitIdx));
    remaining = remaining.substring(splitIdx);
  }

  if (remaining) {
    chunks.push(remaining);
  }
  return chunks;
}

function wrapLinePreservingIndent(line, maxWidth) {
  const indentMatch = line.match(/^(\s*)/);
  const indent = indentMatch ? indentMatch[1] : '';
  const content = line.substring(indent.length);
  const available = Math.max(20, maxWidth - indent.length);

  const words = content.split(' ');
  const chunks = [];
  let cur = '';

  for (let w of words) {
    if (w.length > available) {
      if (cur) {
        chunks.push(indent + cur);
        cur = '';
      }
      const tokenChunks = breakLongToken(w, available);
      for (let i = 0; i < tokenChunks.length - 1; i++) {
        chunks.push(indent + '  ' + tokenChunks[i]);
      }
      cur = '  ' + tokenChunks[tokenChunks.length - 1];
      continue;
    }

    if (!cur) {
      cur = w;
    } else if (cur.length + 1 + w.length <= available) {
      cur += ' ' + w;
    } else {
      chunks.push(indent + cur);
      cur = '  ' + w;
    }
  }
  if (cur) chunks.push(indent + cur);
  return chunks.length > 0 ? chunks : [line];
}

function cleanModelOutput(text) {
  if (!text) return '';
  let out = text;
  // 0. Strip leading repeated completion emojis (e.g. ✅ or 🟢) so they are not duplicated inside body
  out = out.replace(/^(?:(?:\s*[✅🟢]\s*){4,25}\n*)+/g, '');
  // 1. Strip top banner box (handling ╔══╗, pipes |, or text boxes)
  out = out.replace(/(?:(?:```|''')[a-z]*\s*\n)?(?:╔[═]+╗|[|─_]{4,})[^╚]*?(?:ANTIGRAVITY INTELLIGENCE|🤖\s*A\s*G\s*Y)[^╚]*?(?:╚[═]+╝|[|─_]{4,})(?:\s*\n(?:```|'''))?\n*/gi, '');
  // 2. Strip bottom signature box
  out = out.replace(/(?:(?:```|''')[a-z]*\s*\n)?(?:╔[═]+╗|[|─_]{4,})[^╚]*?AGY ENGINE[^╚]*?(?:╚[═]+╝|[|─_]{4,})(?:\s*\n(?:```|'''))?\n*/gi, '');
  // 3. Strip seal
  out = out.replace(/(?:```[a-z]*\s*\n)?«[━]+[^»]*?(?:VERIFIED|SEALED)[^»]*?[━]+»(?:\s*\n```)?\n*/gi, '');
  // 4. Strip execution matrix
  out = out.replace(/(?:```[a-z]*\s*\n)?╔═\s*EXECUTION MATRIX[^╚]*?╚═+╝(?:\s*\n```)?\n*/gi, '');
  // 5. Strip session data (duplicate)
  out = out.replace(/(?:```[a-z]*\s*\n)?(?:╭─|┌─|[|])\s*SESSION DATA[^╰┘|]*?(?:╰─+╯|└─+┘|[|─_]{4,})(?:\s*\n```)?\n*/gi, '');
  // 6. Strip neural response wrapper header & footer delimiters
  out = out.replace(/╭─\s*NEURAL RESPONSE\s*─╮\s*\n?/gi, '');
  out = out.replace(/\n*╰─+\s*(?:NEURAL RESPONSE)?\s*─+╯\s*/gi, '');
  out = out.replace(/\n*╰─{4,}╯\s*$/g, '');
  // 7. Clean up double-wrapped long file path links: ['file:///path'](file:///path) -> `file:///path`
  out = out.replace(/\[\s*'(file:\/\/\/[^']+)'\s*\]\s*\(\s*file:\/\/\/[^\)]+\s*\)/g, '`$1`');
  out = out.replace(/\[\s*(file:\/\/\/[^\s\]]+)\s*\]\s*\(\s*file:\/\/\/[^\)]+\s*\)/g, '`$1`');
  // 8. Clean trailing/leading codeblock artifacts
  out = out.replace(/^\s*(?:```|''')[a-z]*\s*\n/i, '');
  out = out.replace(/\n\s*(?:```|''')\s*$/i, '');
  return out.trim();
}


// Dynamic transcript tracking
let currentTranscriptFile = null;
let lastSeenStepIndex = 0;
let lastSentReplyIndex = 0;

const convWindowMap = {};
const convJidMap = {};

function getTargetInfoForTranscript(transcriptPath) {
  const match = transcriptPath.match(/\/brain\/([a-f0-9-]+)\//);
  const convId = match ? match[1] : transcriptPath;
  if (convWindowMap[convId] && convJidMap[convId]) {
    return { window: convWindowMap[convId], jid: convJidMap[convId] };
  }

  // 1. Direct step 0 prompt inspection from transcript.jsonl
  try {
    const firstLine = fs.readFileSync(transcriptPath, 'utf8').split('\n')[0];
    if (firstLine) {
      const step0 = JSON.parse(firstLine);
      const content = step0.content || '';
      if (content.includes('AGY · YouTube Pipeline') || content.includes('(yt)')) {
        convWindowMap[convId] = 'agy:yt';
        convJidMap[convId] = '120363430650656655@g.us';
        return { window: 'agy:yt', jid: '120363430650656655@g.us' };
      }
      if (content.includes('AGY · Frappe') || content.includes('(frappe)')) {
        convWindowMap[convId] = 'agy:frappe';
        convJidMap[convId] = '120363430126311832@g.us';
        return { window: 'agy:frappe', jid: '120363430126311832@g.us' };
      }
      if (content.includes('AGY · Telegram') || content.includes('(tg)')) {
        convWindowMap[convId] = 'agy:tg';
        convJidMap[convId] = '120363411604185129@g.us';
        return { window: 'agy:tg', jid: '120363411604185129@g.us' };
      }
      if (content.includes('AGY · Digital History') || content.includes('(history)')) {
        convWindowMap[convId] = 'agy:history';
        convJidMap[convId] = '120363429326945679@g.us';
        return { window: 'agy:history', jid: '120363429326945679@g.us' };
      }
      if (content.includes('AGY · Kids Tube') || content.includes('KidsTube') || content.includes('(kids)')) {
        convWindowMap[convId] = 'agy:kids';
        convJidMap[convId] = '120363428733621560@g.us';
        return { window: 'agy:kids', jid: '120363428733621560@g.us' };
      }
      if (content.includes('AGY · Rust Task') || content.includes('Rust_Task') || content.includes('(rust)')) {
        convWindowMap[convId] = 'agy:rust';
        convJidMap[convId] = '120363430134546653@g.us';
        return { window: 'agy:rust', jid: '120363430134546653@g.us' };
      }
      if (content.includes('AGY · Article') || content.includes('Article-Publishing') || content.includes('(article)')) {
        convWindowMap[convId] = 'agy:article';
        convJidMap[convId] = '120363412465134469@g.us';
        return { window: 'agy:article', jid: '120363412465134469@g.us' };
      }
      if (content.includes('AGY · 3D') || content.includes('3D-Game-Design') || content.includes('(game)')) {
        convWindowMap[convId] = 'agy:game';
        convJidMap[convId] = '120363412755041087@g.us';
        return { window: 'agy:game', jid: '120363412755041087@g.us' };
      }
      if (content.includes('Ask & Research') || content.includes('Ask-And-Research') || content.includes('(research)')) {
        convWindowMap[convId] = 'agy:research';
        const pGroups = getProjectGroupMap();
        convJidMap[convId] = (pGroups.research && pGroups.research.id) ? pGroups.research.id : TARGET_JID;
        return { window: 'agy:research', jid: convJidMap[convId] };
      }
    }
  } catch (e) {}

  // 2. Database workspace check
  try {
    const out = execSync(`python3 -c "import sqlite3; conn=sqlite3.connect('/home/azureuser/.gemini/antigravity-cli/conversation_summaries.db'); row=conn.execute('SELECT workspace_uris FROM conversation_summaries WHERE conversation_id=?', ('${convId}',)).fetchone(); print(row[0] if row else '')"`, { encoding: 'utf8', timeout: 1500 }).trim();
    if (out) {
      if (out.includes('social-media/youtube') || out.includes('Social Media/youtube') || out.includes('/youtube')) {
        convWindowMap[convId] = 'agy:yt';
        convJidMap[convId] = '120363430650656655@g.us';
      } else if (out.includes('Frappe-erp-Alco')) {
        convWindowMap[convId] = 'agy:frappe';
        convJidMap[convId] = '120363430126311832@g.us';
      } else if (out.includes('telegram-bot')) {
        convWindowMap[convId] = 'agy:tg';
        convJidMap[convId] = '120363411604185129@g.us';
      } else if (out.includes('PERSONAL AI AGENT')) {
        convWindowMap[convId] = 'agy:history';
        convJidMap[convId] = '120363429326945679@g.us';
      } else if (out.includes('kids_tube_with_folder_seection')) {
        convWindowMap[convId] = 'agy:kids';
        convJidMap[convId] = '120363428733621560@g.us';
      } else if (out.includes('Rust_Task_With_Time_Keeping_And_Live_Note')) {
        convWindowMap[convId] = 'agy:rust';
        convJidMap[convId] = '120363430134546653@g.us';
      } else if (out.includes('Article-Publishing-Platform')) {
        convWindowMap[convId] = 'agy:article';
        convJidMap[convId] = '120363412465134469@g.us';
      } else if (out.includes('3D-Game-Design-Studio')) {
        convWindowMap[convId] = 'agy:game';
        convJidMap[convId] = '120363412755041087@g.us';
      } else if (out.includes('Ask-And-Research-Agent') || out.includes('Ask-and-research-agent')) {
        convWindowMap[convId] = 'agy:research';
        const pGroups = getProjectGroupMap();
        convJidMap[convId] = (pGroups.research && pGroups.research.id && pGroups.research.id.endsWith('@g.us') && !pGroups.research.id.includes('pending')) ? pGroups.research.id : (lastPersonalLid || TARGET_JID);
      } else {
        convWindowMap[convId] = 'agy:0';
        convJidMap[convId] = lastPersonalLid || TARGET_JID;
      }
      return { window: convWindowMap[convId], jid: convJidMap[convId] };
    }
  } catch (e) {}

  return { window: 'agy:0', jid: lastPersonalLid || TARGET_JID };
}

let cachedConvDirs = [];
let lastConvDirsCheck = 0;

function findRecentTranscripts() {
  const brainDir = '/home/azureuser/.gemini/antigravity-cli/brain';
  if (!fs.existsSync(brainDir)) return [];

  const recent = [];
  const now = Date.now();
  const threshold = now - 30 * 60 * 1000; // 30 minutes

  try {
    if (now - lastConvDirsCheck > 4000 || cachedConvDirs.length === 0) {
      cachedConvDirs = fs.readdirSync(brainDir);
      lastConvDirsCheck = now;
    }
    for (const d of cachedConvDirs) {
      const p = path.join(brainDir, d, '.system_generated/logs/transcript.jsonl');
      try {
        const stat = fs.statSync(p);
        if (stat.mtimeMs > threshold) {
          recent.push({ path: p, mtime: stat.mtimeMs });
        }
      } catch (e) {}
    }
  } catch (e) {}

  recent.sort((a, b) => b.mtime - a.mtime);
  return recent.map(r => r.path);
}

function findNewestTranscript() {
  const recent = findRecentTranscripts();
  return recent.length > 0 ? recent[0] : null;
}

function uploadToPasteRs(text) {
  return new Promise((resolve) => {
    if (!text || !String(text).trim()) return resolve(null);
    try {
      const req = https.request('https://paste.rs', {
        method: 'POST',
        headers: {
          'Content-Type': 'text/plain; charset=utf-8',
          'Content-Length': Buffer.byteLength(text)
        },
        timeout: 5000
      }, (res) => {
        let body = '';
        res.setEncoding('utf8');
        res.on('data', chunk => body += chunk);
        res.on('end', () => {
          const out = body.trim();
          // FIX 2026-10-03: never use an HTML error page (e.g. 400) as the link
          if (res.statusCode >= 200 && res.statusCode < 300 && /^https:\/\/paste\.rs\/\S+$/.test(out)) {
            resolve(out);
          } else {
            console.log('[WA Bridge] paste.rs rejected upload: HTTP', res.statusCode, 'bytes', Buffer.byteLength(text));
            resolve(null);
          }
        });
      });

      req.on('error', () => resolve(null));
      req.on('timeout', () => { req.destroy(); resolve(null); });
      req.write(text);
      req.end();
    } catch (e) {
      resolve(null);
    }
  });
}

const PROJECT_GROUPS_FILE = '/home/azureuser/.webterminal/project_groups.json';

function getProjectGroupMap() {
  if (fs.existsSync(PROJECT_GROUPS_FILE)) {
    try {
      return JSON.parse(fs.readFileSync(PROJECT_GROUPS_FILE, 'utf8'));
    } catch (e) {}
  }
  return {};
}

function isAllowedSender(sender, participant = '') {
  if (!sender) return false;
  if (sender.endsWith('@g.us')) {
    const groups = getProjectGroupMap();
    const isOurGroup = Object.values(groups).some(g => g && g.id === sender);
    if (!isOurGroup) return false;
    const p = participant || '';
    if (ALLOWED_NUMBERS.some(num => p.includes(num))) return true;
    if (p.includes('82935919157317') || p.includes('8801955333555') || p.includes('8801966608406') || p.includes('206343935946909')) return true;
    const meLid = sock?.authState?.creds?.me?.lid || '';
    if (meLid) {
      const cleanLid = meLid.split(':')[0].split('@')[0];
      if (cleanLid && p.includes(cleanLid)) return true;
    }
    return false;
  }
  if (ALLOWED_NUMBERS.some(num => sender.includes(num))) return true;
  const meLid = sock?.authState?.creds?.me?.lid || '';
  if (meLid) {
    const cleanLid = meLid.split(':')[0].split('@')[0];
    if (cleanLid && sender.includes(cleanLid)) return true;
  }
  if (sender.includes('82935919157317') || sender.includes('8801955333555') || sender.includes('8801966608406') || sender.includes('206343935946909')) return true;
  return false;
}

async function sendWhatsAppMessage(text, options = {}) {
  if (!sock || !isWsConnected || !text) return;
  const target = options.to || lastActiveJid || TARGET_JID;
  const isGroup = target.endsWith('@g.us');

  // CRITICAL: NEVER pass 'quoted' to group messages!
  // In WhatsApp groups, quoting own messages across linked devices creates an invalid contextInfo participant that WhatsApp servers silently discard.
  const cleanOptions = {};
  if (!isGroup && options.quoted) {
    cleanOptions.quoted = options.quoted;
  }

  try {
    const res = await sock.sendMessage(target, { text: text.trim() }, cleanOptions);
    if (res && res.key && res.key.id) {
      sentMessageIds.add(res.key.id);
      console.log(`[WA Bridge] 📨 Sent to ${target} (isGroup=${isGroup}, msgId=${res.key.id})`);
    }
    return res;
  } catch (err) {
    try {
      console.warn(`[WA Bridge] ⚠️ Retrying fallback send to ${target} without options: ${err.message}`);
      const fallbackRes = await sock.sendMessage(target, { text: text.trim() });
      if (fallbackRes && fallbackRes.key && fallbackRes.key.id) {
        sentMessageIds.add(fallbackRes.key.id);
        console.log(`[WA Bridge] 📨 Fallback sent to ${target}, msgId=${fallbackRes.key.id}`);
      }
      return fallbackRes;
    } catch (e) {
      console.error(`[WA Bridge] ❌ Error sending message to ${target}:`, e.message);
    }
  }
}

async function sendWhatsAppDocument(filePath, fileName, caption = '', options = {}) {
  if (!sock || !isWsConnected || !filePath || !fs.existsSync(filePath)) return null;
  const target = options.to || lastActiveJid || TARGET_JID;
  const buffer = fs.readFileSync(filePath);
  const ext = path.extname(filePath).toLowerCase();
  let mimetype = 'application/octet-stream';
  if (ext === '.xlsx') mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
  else if (ext === '.xls') mimetype = 'application/vnd.ms-excel';
  else if (ext === '.pdf') mimetype = 'application/pdf';
  else if (ext === '.csv') mimetype = 'text/csv';
  else if (ext === '.json') mimetype = 'application/json';

  try {
    const res = await sock.sendMessage(target, {
      document: buffer,
      mimetype: mimetype,
      fileName: fileName || path.basename(filePath),
      caption: caption || undefined
    });
    if (res && res.key && res.key.id) {
      sentMessageIds.add(res.key.id);
      console.log(`[WA Bridge] 📄 Sent document ${fileName || path.basename(filePath)} to ${target} (${buffer.length} bytes, msgId=${res.key.id})`);
    }
    return res;
  } catch (err) {
    console.error(`[WA Bridge] ❌ Error sending document to ${target}:`, err.message);
    return null;
  }
}

let isProcessingOutbox = false;
async function processWaOutbox() {
  if (isProcessingOutbox || !sock || !isWsConnected) return;
  if (!fs.existsSync(WA_OUTBOX_DIR)) return;

  isProcessingOutbox = true;
  try {
    const files = fs.readdirSync(WA_OUTBOX_DIR).filter(f => f.endsWith('.json'));
    for (const f of files) {
      const jobPath = path.join(WA_OUTBOX_DIR, f);
      try {
        const raw = fs.readFileSync(jobPath, 'utf8');
        const job = JSON.parse(raw);
        const target = job.target || lastActiveJid || TARGET_JID;

        if (job.summary) {
          await sendWhatsAppMessage(job.summary, { to: target });
          await new Promise(r => setTimeout(r, 600));
        }

        if (job.excel_path && fs.existsSync(job.excel_path)) {
          await sendWhatsAppDocument(job.excel_path, job.excel_name, `📊 ${job.topic || 'Research Dossier'}`, { to: target });
        }

        const archiveDir = path.join(WA_OUTBOX_DIR, 'archive');
        if (!fs.existsSync(archiveDir)) fs.mkdirSync(archiveDir, { recursive: true });
        fs.renameSync(jobPath, path.join(archiveDir, `${Date.now()}_${f}`));
        console.log(`[WA Bridge] ✅ Processed outbox job: ${f}`);
      } catch (jobErr) {
        console.error(`[WA Bridge] ❌ Error processing job ${f}:`, jobErr.message);
        try {
          const errDir = path.join(WA_OUTBOX_DIR, 'errors');
          if (!fs.existsSync(errDir)) fs.mkdirSync(errDir, { recursive: true });
          fs.renameSync(jobPath, path.join(errDir, f));
        } catch (e) {}
      }
    }
  } catch (e) {
    console.error('[WA Bridge] Outbox scan error:', e.message);
  } finally {
    isProcessingOutbox = false;
  }
}

function autoSanitizeAuth() {
  try {
    if (!fs.existsSync(AUTH_DIR)) return;
    const backupDir = '/home/azureuser/.webterminal/wa_auth_senderkeys_backup';
    if (!fs.existsSync(backupDir)) fs.mkdirSync(backupDir, { recursive: true });

    const files = fs.readdirSync(AUTH_DIR);
    for (const f of files) {
      if (f.startsWith('sender-key-')) {
        const fullPath = path.join(AUTH_DIR, f);
        try {
          const sz = fs.statSync(fullPath).size / 1024;
          if (sz > 25) { // If bloated above 25KB, rotate it
            const dest = path.join(backupDir, `${f}.${Date.now()}.bak`);
            fs.renameSync(fullPath, dest);
            console.log(`[WA Bridge] 🛡️ Auto-sanitized bloated sender key: ${f} (${sz.toFixed(1)} KB) -> backed up`);
          }
        } catch (e) {}
      }
    }
  } catch (e) {
    console.error('[WA Bridge] Auto-sanitize error:', e.message);
  }
}

async function ensureResearchGroup() {
  try {
    const pGroups = getProjectGroupMap();
    const currentId = pGroups.research?.id;
    const isPending = !currentId || currentId.includes('pending') || !currentId.endsWith('@g.us');

    const groups = await sock.groupFetchAllParticipating();
    const list = Object.values(groups).map(g => ({ id: g.id, subject: g.subject, participants: g.participants || [] }));
    console.log('[WA Bridge] 📋 ALL_PARTICIPATING_GROUPS count:', list.length);

    let matched = null;
    for (const g of list) {
      const s = (g.subject || '').toLowerCase();
      const isMatch = /(?:ask\s*&?\s*research|research\s*agent|agy\s*·\s*ask)/i.test(s);
      const hasTargetParticipant = g.participants.some(p => (p.id || '').includes('8801966608406'));
      if (isMatch || hasTargetParticipant) {
        matched = g;
        break;
      }
    }

    if (matched) {
      console.log(`[WA Bridge] 🎯 Auto-linked Ask & Research Group: ${matched.subject} (${matched.id})`);
      pGroups.research = {
        id: matched.id,
        name: matched.subject || 'AGY · Ask & Research',
        key: 'research',
        window: 'agy:research',
        cwd: '/home/azureuser/IrakIroan/IroScript_Projects/Ask-And-Research-Agent'
      };
      fs.writeFileSync(PROJECT_GROUPS_FILE, JSON.stringify(pGroups, null, 2), 'utf8');
      return;
    }

    if (isPending) {
      console.log('[WA Bridge] 🚀 Creating dedicated group with 01966608406: "AGY · Ask & Research"...');
      const participants = ['8801966608406@s.whatsapp.net'];
      if (TARGET_PHONE && TARGET_PHONE !== '8801966608406') {
        participants.push(`${TARGET_PHONE}@s.whatsapp.net`);
      }
      try {
        const newGroup = await sock.groupCreate('AGY · Ask & Research', participants);
        console.log('[WA Bridge] ✅ Group created successfully:', newGroup);
        if (newGroup && newGroup.id) {
          pGroups.research = {
            id: newGroup.id,
            name: 'AGY · Ask & Research',
            key: 'research',
            window: 'agy:research',
            cwd: '/home/azureuser/IrakIroan/IroScript_Projects/Ask-And-Research-Agent'
          };
          fs.writeFileSync(PROJECT_GROUPS_FILE, JSON.stringify(pGroups, null, 2), 'utf8');

          let inviteUrl = '';
          try {
            const code = await sock.groupInviteCode(newGroup.id);
            inviteUrl = `https://chat.whatsapp.com/${code}`;
          } catch (e) {}

          await sendWhatsAppMessage(`🔬 ══════════════════════ 🔬\n👑 *[AGY · ASK & RESEARCH AGENT]*\n━━━━━━━━━━━━━━━━━━━━━\n> 🎯 *উদ্দেশ্য:* অজানা, নতুন ও অপ্রচলিত বিষয়ে গভীর গবেষণা এবং স্বয়ংক্রিয় এক্সেল ডসিয়ার তৈরি।\n> 📱 *যুক্ত নম্বর:* +8801966608406\n> 📁 *রিসার্চ ডিরেক্টরি:* \`IroScript_Projects/Ask-And-Research-Agent\`\n> 🖥️ *টার্মিনাল সেশন:* \`tmux agy:research\`\n\n⚡ _এই গ্রুপে যেকোনো নতুন বিষয়ের নাম পাঠালে এআই তাৎক্ষণিকভাবে সাব-ফোল্ডার খুলে গবেষণা শুরু করবে এবং এক্সেল রিপোর্ট পাঠাবে।_\n══════════════════════`, { to: newGroup.id });

          const personalTarget = lastPersonalLid || TARGET_JID;
          await sendWhatsAppMessage(`🔬 ══════════════════════ 🔬\n✅ *[Ask & Research Agent গ্রুপ তৈরি সম্পন্ন]*\n━━━━━━━━━━━━━━━━━━━━━\n> 👥 *গ্রুপের নাম:* AGY · Ask & Research\n> 📱 *যুক্ত নম্বর:* +8801966608406\n> 🔗 *গ্রুপ লিঙ্ক:* ${inviteUrl || 'অটো-অ্যাড সম্পন্ন'}\n\n⚡ _Ask & Research Agent এখন এই গ্রুপে লাইভ সংযুক্ত।_\n══════════════════════`, { to: personalTarget });
        }
      } catch (cgErr) {
        console.error('[WA Bridge] ❌ Failed to create group via sock.groupCreate:', cgErr.message);
      }
    }
  } catch (err) {
    console.error('[WA Bridge] Failed in ensureResearchGroup:', err.message);
  }
}

async function ensureCodexGroup() {
  try {
    const pGroups = getProjectGroupMap();
    const currentId = pGroups.codex?.id;
    const isPending = !currentId || currentId.includes('pending') || !currentId.endsWith('@g.us');

    const groups = await sock.groupFetchAllParticipating();
    const list = Object.values(groups).map(g => ({ id: g.id, subject: g.subject, participants: g.participants || [] }));

    let matched = null;
    for (const g of list) {
      const s = (g.subject || '').toLowerCase();
      const isMatch = /(?:openai\s*codex|codex|agy\s*·\s*codex)/i.test(s);
      if (isMatch) {
        matched = g;
        break;
      }
    }

    if (matched) {
      console.log(`[WA Bridge] 🎯 Auto-linked OpenAI Codex Group: ${matched.subject} (${matched.id})`);
      pGroups.codex = {
        id: matched.id,
        name: matched.subject || 'AGY · OpenAI Codex',
        key: 'codex',
        window: 'agy:codex',
        cwd: '/home/azureuser/IroScript_Projects/OpenAI_Codex',
        git_remote: '',
        whatsapp_status: 'CONNECTED'
      };
      fs.writeFileSync(PROJECT_GROUPS_FILE, JSON.stringify(pGroups, null, 2), 'utf8');
      return;
    }

    if (isPending) {
      console.log('[WA Bridge] 🚀 Creating dedicated group with 01966608406: "AGY · OpenAI Codex"...');
      const participants = ['8801966608406@s.whatsapp.net'];
      if (TARGET_PHONE && TARGET_PHONE !== '8801966608406') {
        participants.push(`${TARGET_PHONE}@s.whatsapp.net`);
      }
      try {
        const newGroup = await sock.groupCreate('AGY · OpenAI Codex', participants);
        console.log('[WA Bridge] ✅ Codex Group created successfully:', newGroup);
        if (newGroup && newGroup.id) {
          pGroups.codex = {
            id: newGroup.id,
            name: 'AGY · OpenAI Codex',
            key: 'codex',
            window: 'agy:codex',
            cwd: '/home/azureuser/IroScript_Projects/OpenAI_Codex',
            git_remote: '',
            whatsapp_status: 'CONNECTED'
          };
          fs.writeFileSync(PROJECT_GROUPS_FILE, JSON.stringify(pGroups, null, 2), 'utf8');

          let inviteUrl = '';
          try {
            const code = await sock.groupInviteCode(newGroup.id);
            inviteUrl = `https://chat.whatsapp.com/${code}`;
          } catch (e) {}

          await sendWhatsAppMessage(`🤖 ══════════════════════ 🤖\n👑 *[AGY · OPENAI CODEX TERMINAL]*\n━━━━━━━━━━━━━━━━━━━━━\n> 🎯 *উদ্দেশ্য:* OpenAI Codex (GPT-6.1-sol) ডেডিকেটেড কোডিং ও অটোমেশন টার্মিনাল।\n> 📱 *যুক্ত নম্বর:* +8801966608406\n> 📁 *ওয়ার্কস্পেস ডিরেক্টরি:* \`IroScript_Projects/OpenAI_Codex\`\n> 🖥️ *টার্মিনাল সেশন:* \`tmux agy:codex\`\n\n⚡ _এই গ্রুপে পাঠানো যেকোনো প্রম্পট সরাসরি OpenAI Codex এক্সিকিউট করবে।_\n══════════════════════`, { to: newGroup.id });

          const personalTarget = lastPersonalLid || TARGET_JID;
          await sendWhatsAppMessage(`🤖 ══════════════════════ 🤖\n✅ *[OpenAI Codex টার্মিনাল গ্রুপ তৈরি সম্পন্ন]*\n━━━━━━━━━━━━━━━━━━━━━\n> 👥 *গ্রুপের নাম:* AGY · OpenAI Codex\n> 📱 *যুক্ত নম্বর:* +8801966608406\n> 🔗 *গ্রুপ লিঙ্ক:* ${inviteUrl || 'অটো-অ্যাড সম্পন্ন'}\n\n⚡ _OpenAI Codex টার্মিনাল এখন এই গ্রুপে লাইভ সংযুক্ত।_\n══════════════════════`, { to: personalTarget });
        }
      } catch (cgErr) {
        console.error('[WA Bridge] ❌ Failed to create group via sock.groupCreate:', cgErr.message);
      }
    }
  } catch (err) {
    console.error('[WA Bridge] Failed in ensureCodexGroup:', err.message);
  }
}

let sanitizeIntervalStarted = false;

async function startBridge() {
  autoSanitizeAuth();
  if (!sanitizeIntervalStarted) {
    setInterval(autoSanitizeAuth, 15 * 60 * 1000);
    sanitizeIntervalStarted = true;
  }
  const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);

  sock = makeWASocket({
    auth: state,
    logger: pino({ level: 'silent' }),
    printQRInTerminal: false,
    browser: ['Ubuntu', 'Chrome', '122.0.0'],
    connectTimeoutMs: 60000,
    keepAliveIntervalMs: 25000,
    defaultQueryTimeoutMs: 60000,
    retryRequestDelayMs: 250
  });

  sock.ev.on('creds.update', saveCreds);

  sock.ev.on('connection.update', async (update) => {
    const { connection, lastDisconnect } = update;
    console.log('[WA Bridge] Connection update:', connection || update);

    if (connection === 'close') {
      isWsConnected = false;
      const statusCode = lastDisconnect?.error?.output?.statusCode;
      const shouldReconnect = statusCode !== DisconnectReason.loggedOut;
      console.log('[WA Bridge] Connection closed, reason:', statusCode, 'reconnecting:', shouldReconnect);
      if (shouldReconnect) {
        setTimeout(startBridge, 3000);
      } else {
        console.log('[WA Bridge] ⚠️ Session logged out (401). Clearing auth for re-pairing...');
        try {
          const backupDir = `/home/azureuser/.webterminal/wa_auth_backup_${Date.now()}`;
          if (fs.existsSync(AUTH_DIR)) {
            fs.renameSync(AUTH_DIR, backupDir);
            console.log('[WA Bridge] Backed up old auth to:', backupDir);
          }
        } catch (e) {
          console.error('[WA Bridge] Backup auth error:', e.message);
        }
        setTimeout(startBridge, 2000);
      }
    } else if (connection === 'open') {
      isWsConnected = true;
      console.log('[WA Bridge] 🟢 WhatsApp connection is OPEN!');
      try {
        if (fs.existsSync(PAIRING_FILE)) fs.unlinkSync(PAIRING_FILE);
      } catch (e) {}

      const meLid = sock?.authState?.creds?.me?.lid;
      if (meLid) {
        lastActiveJid = meLid.replace(/:.*@/, '@');
        console.log('[WA Bridge] Set lastActiveJid to LID:', lastActiveJid);
      }

      ensureResearchGroup().catch(err => {
        console.error('[WA Bridge] ensureResearchGroup error:', err.message);
      });
      ensureCodexGroup().catch(err => {
        console.error('[WA Bridge] ensureCodexGroup error:', err.message);
      });

      // Reconcile and recover waiting messages after Baileys reconnect (Section 10 & Milestone 2)
      try {
        const queue = loadDurableQueue();
        const pendingItems = queue.filter(q => q.status === 'RECEIVED' || q.status === 'RETRYING' || q.status === 'HELD_FOR_ZIP');
        if (pendingItems.length > 0) {
          console.log(`[WA Bridge] 🔄 Baileys reconnected! Found ${pendingItems.length} waiting message(s) in durable queue.`);
          const recoveryText = BANGLA_RECONNECT_TEMPLATE.replace('{count}', pendingItems.length);
          const targetNoticeRecipient = lastActiveJid || (pendingItems[0].reply_context && pendingItems[0].reply_context.sender);
          if (targetNoticeRecipient) {
            sendWhatsAppMessage(recoveryText, { to: targetNoticeRecipient }).catch(err => {
              console.error('[WA Bridge] Error sending reconnect recovery notice:', err.message);
            });
          }

          // Resume pending delivery in FIFO order
          const pendingWindows = new Set(pendingItems.map(p => p.target_window));
          for (const win of pendingWindows) {
            drainNextPromptForWindow(win);
          }
        }
      } catch (recErr) {
        console.error('[WA Bridge] Error in reconnect message reconciliation:', recErr.message);
      }

      try {
        let activeConsoleUrl = 'https://textiles-absolute-destinations-omaha.trycloudflare.com';
        const urlFile = '/home/azureuser/.webterminal/terminal_url.txt';
        if (fs.existsSync(urlFile)) {
          const readUrl = fs.readFileSync(urlFile, 'utf8').trim();
          if (readUrl) activeConsoleUrl = readUrl;
        }
        const welcomeText = `╔══════════════════════════╗\n   👑 *ইরাক ভাইয়ার পার্সোনাল ক্লাউড এআই* 👑\n╚══════════════════════════╝\n\n> 🟢 *সার্ভার স্ট্যাটাস:* সক্রিয় (24/7 Cloud Online)\n> 🚀 *ইঞ্জিন:* Antigravity CLI\n> 🛡️ *সুরক্ষা:* এন্ড-টু-এন্ড এনক্রিপ্টেড মাল্টি-ডিভাইস\n\n💎 *শর্টকাট ফিচার:*\n• ⚡ \`$ <কমান্ড>\` ➔ সরাসরি লিনাক্স কমান্ড রান (যেমন: \`$ uptime\`)\n• 📸 \`/screen\` ➔ লাইভ টার্মিনাল স্ক্রিনশট\n• 🌐 *ওয়েব কনসোল:* ${activeConsoleUrl}\n══════════════════════════`;
        await sendWhatsAppMessage(welcomeText);
        console.log('[WA Bridge] Sent ready notice to:', lastActiveJid);
      } catch (err) {
        console.error('[WA Bridge] Ready message error:', err.message);
      }
    }
  });

  function unwrapMessage(rawMsg) {
    if (!rawMsg) return {};
    let m = rawMsg;
    while (m) {
      if (m.ephemeralMessage?.message) {
        m = m.ephemeralMessage.message;
      } else if (m.viewOnceMessage?.message) {
        m = m.viewOnceMessage.message;
      } else if (m.viewOnceMessageV2?.message) {
        m = m.viewOnceMessageV2.message;
      } else if (m.documentWithCaptionMessage?.message) {
        m = m.documentWithCaptionMessage.message;
      } else {
        break;
      }
    }
    return m || {};
  }

  function formatBytes(bytes) {
    if (!bytes) return '0 B';
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }

  async function flushMediaBatch() {
    if (mediaBatch.length === 0) return;
    const currentBatch = [...mediaBatch];
    mediaBatch = [];
    if (mediaBatchTimer) {
      clearTimeout(mediaBatchTimer);
      mediaBatchTimer = null;
    }

    const lastItem = currentBatch[currentBatch.length - 1];

    if (currentBatch.length === 1) {
      const item = currentBatch[0];
      const itemSender = item.msg?.key?.remoteJid || lastActiveJid;
      const targetWindow = getWindowForSender(itemSender);
      lastUserMsgByWindow[targetWindow] = item.msg;
      lastUserMsgKeyByWindow[targetWindow] = item.msg.key;
      const cleanCaption = item.caption ? ` ইউজারের ক্যাপশন/প্রশ্ন: "${item.caption.trim()}".` : '';
      if (item.isImage) {
        await sendWhatsAppMessage(`📷 ══════════════════════ 📷\n🤖 *[ছবি ইনপুট গ্রহণ করা হয়েছে]*\n━━━━━━━━━━━━━━━━━━━━━\n> 🖼️ *ফাইল:* \`${item.originalName}\`\n> 💬 *ক্যাপশন:* "${item.caption || '(কোনো ক্যাপশন নেই)'}"\n\n⚡ _এআই ছবিটি বিশ্লেষণ করে উত্তর প্রস্তুত করছে..._\n══════════════════════`, { to: itemSender, quoted: item.msg });
        const prompt = `[ছবি ইনপুট: ${item.filePath}].${cleanCaption} অনুগ্রহ করে view_file("${item.filePath}") ব্যবহার করে ছবিটি দেখুন এবং বিস্তারিত সঠিক উত্তর দিন।`;
        dispatchToTmux(prompt, targetWindow);
      } else {
        await sendWhatsAppMessage(`📁 ══════════════════════ 📁\n🤖 *[ফাইল ইনপুট গ্রহণ করা হয়েছে]*\n━━━━━━━━━━━━━━━━━━━━━\n> 📄 *ফাইল:* \`${item.originalName}\` (\`${formatBytes(item.size)}\`)\n> 💬 *ক্যাপশন:* "${item.caption || '(কোনো ক্যাপশন নেই)'}"\n\n⚡ _এআই ফাইলটি পর্যবেক্ষণ করছে..._\n══════════════════════`, { to: itemSender, quoted: item.msg });
        const prompt = `[ফাইল ইনপুট: ${item.filePath}]. মূল ফাইলের নাম: "${item.originalName}".${cleanCaption} অনুগ্রহ করে view_file("${item.filePath}") ব্যবহার করে ফাইলটি পর্যবেক্ষণ করুন এবং বিস্তারিত সঠিক উত্তর দিন।`;
        dispatchToTmux(prompt, targetWindow);
      }
      return;
    }

    // MULTI-FILE BATCH (Unlimited Files Upload Support)
    const batchSender = lastItem.msg?.key?.remoteJid || lastActiveJid;
    const batchTargetWindow = getWindowForSender(batchSender);
    lastUserMsgByWindow[batchTargetWindow] = lastItem.msg;
    lastUserMsgKeyByWindow[batchTargetWindow] = lastItem.msg.key;

    let cardText = `📁 ══════════════════════ 📁\n🤖 *[মাল্টি-ফাইল আপলোড গ্রহণ করা হয়েছে (${currentBatch.length}টি ফাইল)]*\n━━━━━━━━━━━━━━━━━━━━━\n`;
    currentBatch.forEach((item, idx) => {
      cardText += `${idx + 1}. 📄 *${item.originalName}* (\`${formatBytes(item.size)}\`)\n`;
    });
    cardText += `\n⚡ _এআই সবকটি (${currentBatch.length}টি) ফাইল একসাথে প্রসেস করছে..._\n══════════════════════`;
    await sendWhatsAppMessage(cardText, { to: batchSender, quoted: lastItem.msg });

    let multiPrompt = `[মাল্টি-ফাইল ইনপুট (${currentBatch.length}টি ফাইল গৃহীত)]:\n`;
    currentBatch.forEach((item, idx) => {
      multiPrompt += `${idx + 1}. ${item.filePath} (মূল ফাইলের নাম: "${item.originalName}", আকার: ${formatBytes(item.size)})\n`;
    });
    const captions = currentBatch.map(b => b.caption).filter(Boolean).join(' | ');
    if (captions) {
      multiPrompt += `ইউজারের ক্যাপশন/প্রশ্ন: "${captions.trim()}".\n`;
    }
    multiPrompt += `অনুগ্রহ করে view_file ব্যবহার করে সবগুলো ফাইল পর্যবেক্ষণ করে বিস্তারিত উত্তর দিন।`;
    dispatchToTmux(multiPrompt, batchTargetWindow);
  }

  // Handle incoming messages from Iraq bhai
  sock.ev.on('messages.upsert', async ({ messages, type }) => {
    if (type !== 'notify') return;

    for (const msg of messages) {
      if (!msg.message) continue;
      const msgId = msg.key.id;
      if (!msgId || sentMessageIds.has(msgId) || processedIncomingMessageIds.has(msgId)) continue;

      const sender = msg.key.remoteJid || '';
      const participant = msg.key.participant || msg.participant || '';
      if (!isAllowedSender(sender, participant)) {
        console.log('[WA Bridge] Ignored message from other sender:', sender, participant);
        continue;
      }

      // Deduplicate strictly by message ID (Section 4 & Milestone 2: never drop messages by age)
      if (processedIncomingMessageIds.has(msgId)) {
        continue;
      }

      // 2. Meta AI & Bot Interception Filter:
      // Exclude messages targeting Meta AI or third-party bots
      const isMetaAiJid = sender.includes('13135550002') || sender.toLowerCase().includes('meta') || sender.includes('@bot') || sender.startsWith('0@s.whatsapp.net');
      if (isMetaAiJid) {
        console.log(`[WA Bridge] 🤖 [REJECTED META AI JID]: Message target is Meta AI (${sender}). Dropped.`);
        processedIncomingMessageIds.add(msgId);
        continue;
      }

      // Unwrap all message wrappers (documentWithCaptionMessage, ephemeralMessage, viewOnce)
      const unwrapped = unwrapMessage(msg.message);

      // Check contextInfo mentions for Meta AI
      const contextInfo = unwrapped.extendedTextMessage?.contextInfo ||
                          unwrapped.imageMessage?.contextInfo ||
                          unwrapped.documentMessage?.contextInfo ||
                          msg.message?.extendedTextMessage?.contextInfo || {};
      const mentionedJids = contextInfo.mentionedJid || [];
      const hasMetaAiMention = mentionedJids.some(jid => jid.includes('13135550002') || jid.toLowerCase().includes('meta'));
      if (hasMetaAiMention) {
        console.log(`[WA Bridge] 🤖 [REJECTED META AI MENTION]: Message mentions Meta AI (${mentionedJids.join(', ')}). Dropped.`);
        processedIncomingMessageIds.add(msgId);
        continue;
      }

      const isImage = !!(unwrapped.imageMessage);
      const isDocument = !!(unwrapped.documentMessage);
      const isAudio = !!(unwrapped.audioMessage);
      const isVideo = !!(unwrapped.videoMessage);
      const isMedia = isImage || isDocument || isAudio || isVideo;

      const text = (unwrapped.conversation ||
                    unwrapped.extendedTextMessage?.text ||
                    unwrapped.imageMessage?.caption ||
                    unwrapped.videoMessage?.caption ||
                    unwrapped.documentMessage?.caption || '').trim();

      if (!text && !isMedia) continue;

      if (text.toLowerCase().startsWith('@meta') || text.toLowerCase().startsWith('@meta ai')) {
        console.log(`[WA Bridge] 🤖 [REJECTED META AI PROMPT]: Message addresses Meta AI explicitly. Dropped.`);
        processedIncomingMessageIds.add(msgId);
        continue;
      }

      // Mark message as processed to prevent any duplicate/re-synced execution
      processedIncomingMessageIds.add(msgId);
      saveProcessedMessageIds();

      console.log(`[WA Bridge] 📩 Message from Iraq bhai (${sender}):`, text || `[Media: ${isImage ? 'Image' : 'File'}]`);
      lastUserMsgKey = msg.key;
      lastUserMsg = msg;
      lastActiveJid = sender;
      if (!sender.endsWith('@g.us')) {
        lastPersonalLid = sender;
      }

      // 1. Direct Terminal Screen Snapshot (/screen or /term)
      if (text === '/screen' || text === '/term' || text === '/tmux') {
        const targetWindow = getWindowForSender(sender);
        try {
          const screen = execSync(`tmux capture-pane -p -t ${targetWindow}`, { encoding: 'utf8' });
          const cleanScreen = screen.split('\n').filter(l => l.trim()).slice(-20).join('\n');
          await sendWhatsAppMessage(`🖥️ ══════════════════════ 🖥️\n📸 *[টার্মিনাল লাইভ স্ক্রিন ক্যাপচার]*\n━━━━━━━━━━━━━━━━━━━━━\n> 📟 *টার্মিনাল সেশন:* \`tmux ${targetWindow}\`\n\n\`\`\`\n${cleanScreen}\n\`\`\`\n══════════════════════`, { quoted: msg });
        } catch (e) {
          await sendWhatsAppMessage(`⚠️ টার্মিনাল ক্যাপচার এরর: ${e.message}`, { quoted: msg });
        }
        continue;
      }

      // 2. Direct Bash Shell Command execution (starting with $, !, or /sh)
      if (text.startsWith('$') || text.startsWith('!') || text.startsWith('/sh ')) {
        const targetWindow = getWindowForSender(sender);
        let projectCwd = '/home/azureuser';
        if (targetWindow === 'agy:yt') {
          projectCwd = '/home/azureuser/IrakIroan/IroScript_Projects/Social Media/youtube';
        } else if (targetWindow === 'agy:frappe') {
          projectCwd = '/home/azureuser/Frappe-erp-Alco';
        } else if (targetWindow === 'agy:tg') {
          projectCwd = '/home/azureuser/telegram-bot';
        } else if (targetWindow === 'agy:history') {
          projectCwd = '/home/azureuser/.openclaw/workspace/IROSCRIPT-CEO/PERSONAL AI AGENT';
        } else if (targetWindow === 'agy:kids') {
          projectCwd = '/home/azureuser/kids_tube_with_folder_seection';
        } else if (targetWindow === 'agy:rust') {
          projectCwd = '/home/azureuser/Rust_Task_With_Time_Keeping_And_Live_Note';
        } else if (targetWindow === 'agy:article') {
          projectCwd = '/home/azureuser/Article-Publishing-Platform';
        } else if (targetWindow === 'agy:game') {
          projectCwd = '/home/azureuser/3D-Game-Design-Studio';
        } else if (targetWindow === 'agy:research') {
          projectCwd = '/home/azureuser/IrakIroan/IroScript_Projects/Ask-And-Research-Agent';
        }

        const shellCmd = text.replace(/^(\$|!|\/sh\s*)/, '').trim();
        try {
          await sock.sendMessage(sender, { react: { text: '⚡', key: msg.key } });
        } catch (e) {}

        exec(shellCmd, { cwd: projectCwd, timeout: 30000 }, async (error, stdout, stderr) => {
          let output = (stdout || '') + (stderr || '');
          if (error && !output) output = error.message;
          if (!output.trim()) output = '(কমান্ড সফল হয়েছে কিন্তু কোনো টেক্সট আউটপুট নেই)';

          const displayOut = output.length > 2000 ? output.substring(0, 1900) + '\n... [আউটপুট বড় হওয়ায় সংক্ষেপিত]' : output.trim();
          await sendWhatsAppMessage(`💻 ══════════════════════ 💻\n⚡ *[সরাসরি শেল এক্সিকিউশন · ${targetWindow}]*\n━━━━━━━━━━━━━━━━━━━━━\n> 📁 *ডিরেক্টরি:* \`${projectCwd}\`\n> ⚙️ *কমান্ড:* \`$ ${shellCmd}\`\n\n📦 *টার্মিনাল আউটপুট:*\n\`\`\`\n${displayOut}\n\`\`\`\n══════════════════════`, { quoted: msg });
        });
        continue;
      }

      // 2.25. Interactive Terminal Keystroke Navigation (esc, enter, up, down, tab, left, right, c-c, or 1-9 for pickers)
      const trimmedLower = text.trim().toLowerCase();
      const navKeyMap = {
        '/esc': 'Escape', 'esc': 'Escape', '/escape': 'Escape', 'cancel': 'Escape',
        '/enter': 'Enter', 'enter': 'Enter',
        '/up': 'Up', 'up': 'Up',
        '/down': 'Down', 'down': 'Down',
        '/left': 'Left', 'left': 'Left',
        '/right': 'Right', 'right': 'Right',
        '/tab': 'Tab', 'tab': 'Tab',
        '/c-c': 'C-c', 'c-c': 'C-c', '/ctrl-c': 'C-c'
      };
      let navKey = navKeyMap[trimmedLower] || null;
      if (!navKey && /^[1-9]$/.test(trimmedLower)) {
        const checkWin = getWindowForSender(sender);
        try {
          const paneSnapshot = execSync(`tmux capture-pane -p -t ${checkWin} | tail -n 12`, { encoding: 'utf8', timeout: 1500 });
          if (paneSnapshot.includes('Navigate') || paneSnapshot.includes('Question') || paneSnapshot.includes('Run this command?') || paneSnapshot.includes('> 1.') || paneSnapshot.includes('Select')) {
            navKey = `NUMBER_${trimmedLower}`;
          }
        } catch (e) {}
      }
      if (navKey) {
        const targetWin = getWindowForSender(sender);
        try {
          const { execFileSync } = require('child_process');
          if (navKey.startsWith('NUMBER_')) {
            const digit = navKey.split('_')[1];
            execFileSync('tmux', ['send-keys', '-t', targetWin, digit]);
            execFileSync('tmux', ['send-keys', '-t', targetWin, 'Enter']);
          } else {
            execFileSync('tmux', ['send-keys', '-t', targetWin, navKey]);
          }
          await sock.sendMessage(sender, { react: { text: '🎯', key: msg.key } }).catch(() => {});
          setTimeout(async () => {
            try {
              const screen = execSync(`tmux capture-pane -p -t ${targetWin}`, { encoding: 'utf8', timeout: 2000 });
              const cleanScreen = screen.split('\n').filter(l => l.trim()).slice(-20).join('\n');
              await sendWhatsAppMessage(`🕹️ ══════════════════════ 🕹️\n⌨️ *[কীস্ট্রোক প্রেরিত: \`${navKey}\` · ${targetWin}]*\n━━━━━━━━━━━━━━━━━━━━━\n\`\`\`\n${cleanScreen}\n\`\`\`\n══════════════════════`, { quoted: msg });
            } catch (err) {}
          }, 400);
        } catch (e) {
          console.error(`[WA Bridge] Navigation key error:`, e.message);
        }
        continue;
      }

      // 2.3. Model switch (/model [window] <model> [low|medium|high])  — handled by bridge, not the AI
      if (/^\/models?(\s|$)/i.test(text)) {
        const { execFile } = require('child_process');
        const MODEL_SCRIPT = '/home/azureuser/.webterminal/set_agy_model.sh';
        const knownWins = ['0', 'main', 'master', 'yt', 'frappe', 'tg', 'history', 'kids', 'rust', 'article', 'game', 'research', 'report', 'reporting', 'codex'];
        const tokens = text.replace(/^\/models?\s*/i, '').trim().split(/\s+/).filter(Boolean);
        let targetWindow = getWindowForSender(sender);
        if (tokens.length && (knownWins.includes(tokens[0].toLowerCase()) || /^agy:/i.test(tokens[0]))) {
          const w = tokens.shift().toLowerCase();
          targetWindow = w.startsWith('agy:') ? w : ({ '0': 'agy:0', main: 'agy:0', master: 'agy:0', reporting: 'agy:report' }[w] || `agy:${w}`);
        }
        let effort = 'high';
        if (tokens.length && /^(low|med|medium|high|max)$/i.test(tokens[tokens.length - 1])) effort = tokens.pop().toLowerCase();
        const query = tokens.join(' ');
        if (!query || query === 'status' || query === 'info' || query === 'current') {
          execFile(MODEL_SCRIPT, ['--status', targetWindow], { timeout: 10000 }, async (err, stdout) => {
            const cur = ((stdout || '') || (err ? err.message : '')).trim();
            const help = targetWindow === 'agy:codex'
              ? `\nCodex model বদলাতে:\n/model codex gpt-6.1-sol high\n/model codex gpt-6-astra high\n/model codex gpt-6-sol medium\n/model codex gpt-6-luna low\n/model codex gpt-5.6-sol high\n/model codex gpt-5.6-terra high\n/model codex gpt-5.6-luna low\n/model codex gpt-5.5 high\nEffort: low / medium / high`
              : `\nপরিবর্তন করতে:\n/model opus high\n/model sonnet medium\n/model flash low\n/model 3.1 pro\n/model frappe opus high (অন্য agent)`;
            await sendWhatsAppMessage(`🧠 *[মডেল স্ট্যাটাস]*\n> ${cur}${help}`, { to: sender, quoted: msg });
          });
          continue;
        }
        try { await sock.sendMessage(sender, { react: { text: '🧠', key: msg.key } }); } catch (e) {}
        await sendWhatsAppMessage(`🧠 *[মডেল পরিবর্তন হচ্ছে]*\n> \`${targetWindow}\` → *${query}* · ${effort}\n_এজেন্ট ব্যস্ত থাকলে কাজ শেষ হলে পরিবর্তন হবে..._`, { to: sender, quoted: msg });
        execFile(MODEL_SCRIPT, [targetWindow, query, effort, '900'], { timeout: 960000 }, async (err, stdout) => {
          const out = ((stdout || '').trim() || (err ? err.message : '')).trim();
          const ok = !err && out.startsWith('OK');
          await sendWhatsAppMessage(`${ok ? '✅' : '❌'} *[মডেল ${ok ? 'পরিবর্তন সম্পন্ন' : 'পরিবর্তন ব্যর্থ'}]*\n> ${out}`, { to: sender });
        });
        continue;
      }

      // 2.35. Direct Master Orchestrator routing (/master, /agy0, /admin)
      if (text.startsWith('/master ') || text.startsWith('/agy0 ') || text.startsWith('/admin ')) {
        const masterPrompt = text.replace(/^(\/master|\/agy0|\/admin)\s*/i, '').trim();
        lastUserMsgByWindow['agy:0'] = msg;
        lastUserMsgKeyByWindow['agy:0'] = msg.key;
        dispatchToTmux(masterPrompt, 'agy:0');
        await sendWhatsAppMessage(`🤖 ══════════════════════ 🤖\n👑 *[AGY MASTER ORCHESTRATOR · প্রসেসিং শুরু]*\n━━━━━━━━━━━━━━━━━━━━━\n> 💬 *নির্দেশনা:* "${masterPrompt.substring(0, 80)}"\n\n⚡ _টার্মিনাল সেশন (tmux agy:0) কাজ শুরু করেছে..._\n══════════════════════`, { to: sender });
        continue;
      }

      // 2.4. Direct Frappe routing (/frappe, frappe:)
      if (text.startsWith('/frappe ') || text.toLowerCase().startsWith('frappe: ')) {
        const frappePrompt = text.replace(/^(\/frappe|frappe:)\s*/i, '').trim();
        lastUserMsgByWindow['agy:frappe'] = msg;
        lastUserMsgKeyByWindow['agy:frappe'] = msg.key;
        dispatchToTmux(frappePrompt, 'agy:frappe');
        await sendWhatsAppMessage(`🤖 ══════════════════════ 🤖\n🏢 *[AGY · Frappe ERP Alco · প্রসেসিং শুরু]*\n━━━━━━━━━━━━━━━━━━━━━\n> 💬 *নির্দেশনা:* "${frappePrompt.substring(0, 80)}"\n\n⚡ _টার্মিনাল সেশন (tmux agy:frappe) কাজ শুরু করেছে..._\n══════════════════════`, { to: sender });
        continue;
      }

      // 2.5. Direct Ask & Research Command (/ask, /research, ask:, research:)
      if (text.startsWith('/ask ') || text.startsWith('/research ') || text.toLowerCase().startsWith('ask: ') || text.toLowerCase().startsWith('research: ')) {
        const isResearchCmd = /^\/research\b|^research:\s*/i.test(text);
        const topic = text.replace(/^(\/ask|\/research|ask:|research:)\s*/i, '').trim();
        if (topic) {
          lastUserMsgByWindow['agy:research'] = msg;
          lastUserMsgKeyByWindow['agy:research'] = msg.key;
          const promptToSend = isResearchCmd ? `/research ${topic}` : topic;
          dispatchToTmux(promptToSend, 'agy:research');
          if (isResearchCmd) {
            await sendWhatsAppMessage(`🔬 ══════════════════════ 🔬\n🤖 *[ASK & RESEARCH AGENT · গবেষণা শুরু]*\n━━━━━━━━━━━━━━━━━━━━━\n> 📌 *বিষয়:* "${topic.substring(0, 80)}"\n> 📁 *লোকেশন:* \`IroScript_Projects/Ask-And-Research-Agent\`\n\n⚡ _টার্মিনাল সেশন (tmux agy:research) গবেষণা ও ডসিয়ার প্রস্তুত করছে..._\n══════════════════════`, { to: sender });
          } else {
            await sendWhatsAppMessage(`💬 ══════════════════════ 💬\n🤖 *[ASK & RESEARCH AGENT · আস্ক মোড]*\n━━━━━━━━━━━━━━━━━━━━━\n> ❓ *প্রশ্ন:* "${topic.substring(0, 80)}"\n\n⚡ _টার্মিনাল সেশন (tmux agy:research) উত্তর প্রস্তুত করছে..._\n══════════════════════`, { to: sender });
          }
          continue;
        }
      }

      // 2.6. Direct OpenAI Codex Command (/codex, codex:)
      if (text.startsWith('/codex ') || text.toLowerCase().startsWith('codex: ')) {
        const codexPrompt = text.replace(/^(\/codex|codex:)\s*/i, '').trim();
        if (codexPrompt) {
          lastUserMsgByWindow['agy:codex'] = msg;
          lastUserMsgKeyByWindow['agy:codex'] = msg.key;
          dispatchToTmux(codexPrompt, 'agy:codex');
          await sendWhatsAppMessage(`🤖 ══════════════════════ 🤖\n👑 *[OPENAI CODEX · প্রসেসিং শুরু]*\n━━━━━━━━━━━━━━━━━━━━━\n> 💬 *নির্দেশনা:* "${codexPrompt.substring(0, 80)}"\n> 📁 *লোকেশন:* \`IroScript_Projects/OpenAI_Codex\`\n\n⚡ _টার্মিনাল সেশন (tmux agy:codex) কোড ও টাস্ক প্রসেস করছে..._\n══════════════════════`, { to: sender });
          continue;
        }
      }

      // 3. Media Download (Image, Document, etc.)
      if (isMedia) {
        try {
          await sock.sendMessage(sender, { react: { text: isImage ? '📸' : '📁', key: msg.key } });
        } catch (e) {}

        try {
          const mediaDir = '/home/azureuser/.webterminal/media';
          if (!fs.existsSync(mediaDir)) fs.mkdirSync(mediaDir, { recursive: true });

          const buffer = await baileys.downloadMediaMessage(
            { key: msg.key, message: unwrapped },
            'buffer',
            {},
            { reuploadRequest: sock.updateMediaMessage }
          );

          const docMsg = unwrapped.documentMessage;
          let originalFileName = (docMsg && docMsg.fileName) ? docMsg.fileName : '';
          let ext = 'bin';
          if (originalFileName && originalFileName.includes('.')) {
            ext = originalFileName.split('.').pop().toLowerCase();
          } else {
            try {
              ext = baileys.extensionForMediaMessage(unwrapped) || (isImage ? 'jpeg' : 'bin');
            } catch (e) {
              ext = isImage ? 'jpeg' : 'bin';
            }
          }
          if (ext && ext.startsWith('.')) ext = ext.substring(1);
          if (ext === 'jpg') ext = 'jpeg';

          const safeOriginal = originalFileName ? originalFileName.replace(/[^a-zA-Z0-9._-]/g, '_') : '';
          let mediaFileName = safeOriginal ? `media_${Date.now()}_${safeOriginal}` : `media_${Date.now()}_${msgId.substring(0, 8)}.${ext || 'bin'}`;
          let mediaFilePath = path.join(mediaDir, mediaFileName);
          fs.writeFileSync(mediaFilePath, buffer);
          console.log(`[WA Bridge] 📥 Downloaded media to: ${mediaFilePath} (${buffer.length} bytes, original: ${originalFileName || 'N/A'})`);

          mediaBatch.push({
            filePath: mediaFilePath,
            fileName: mediaFileName,
            originalName: originalFileName || mediaFileName,
            size: buffer.length,
            isImage: isImage,
            isDocument: isDocument,
            caption: text,
            sender: sender,
            msg: msg
          });

          // Debounce: wait 1500ms for other files in this batch
          if (mediaBatchTimer) clearTimeout(mediaBatchTimer);
          mediaBatchTimer = setTimeout(async () => {
            await flushMediaBatch();
          }, 1500);

        } catch (err) {
          console.error('[WA Bridge] ❌ Media download error:', err.message);
          await sendWhatsAppMessage(`⚠️ ছবি/মিডিয়া ডাউনলোড করতে সমস্যা হয়েছে: ${err.message}`, { quoted: msg });
        }
        continue;
      }

      // 4. Normal AI prompt / instructions -> Forward to agy CLI
      try {
        await sock.sendMessage(sender, { react: { text: '⏳', key: msg.key } });
      } catch (e) {}

      const groups = getProjectGroupMap();
      let activeGroup = null;
      for (const [k, g] of Object.entries(groups)) {
        if (g && g.id === sender) {
          activeGroup = g;
          break;
        }
      }

      const targetWindow = getWindowForSender(sender);
      lastUserMsgByWindow[targetWindow] = msg;
      lastUserMsgKeyByWindow[targetWindow] = msg.key;

      const isSlashCommand = /^\/[a-zA-Z0-9_-]+(\s+[\s\S]*)?$/.test(text.trim());
      let contextPrompt = text;
      if (activeGroup && !isSlashCommand) {
        contextPrompt = `[প্রজেক্ট গ্রুপ: ${activeGroup.name} (${activeGroup.key})]: ${text}`;
      }

      // 1. Instant dispatch to tmux (zero delay, immediate millisecond execution)
      dispatchToTmux(contextPrompt, targetWindow, msgId, { sender, msg });

      // 2. Send acknowledgment asynchronously without blocking prompt execution
      try {
        const firstLine = text.trim().split('\n')[0] || text;
        const shortPrompt = firstLine.length > 50 ? firstLine.substring(0, 48) + '...' : firstLine;
        const isResearch = targetWindow === 'agy:research';
        const isCodex = targetWindow === 'agy:codex';
        let headerTitle = activeGroup ? `🤖 *[${activeGroup.name} · এআই প্রসেসিং শুরু]*` : (isResearch ? `🔬 *[ASK & RESEARCH AGENT · গবেষণা শুরু]*` : (isCodex ? `🤖 *[OPENAI CODEX · প্রসেসিং শুরু]*` : `🤖 *[মাস্টার কনসোল · এআই প্রসেসিং শুরু]*`));
        let subMsg = isResearch ? `⚡ _আপনার ব্যক্তিগত রিসার্চ অ্যাসিস্ট্যান্ট গবেষণা ও ডসিয়ার প্রস্তুত করছে..._` : (isCodex ? `⚡ _নির্দেশনাটি Codex টার্মিনালে পাঠানো হয়েছে; Codex থেকে প্রকাশিত অগ্রগতি ও আউটপুট এলে এখানে পাঠানো হবে।_` : `⚡ _টার্মিনাল কমান্ড ও আউটপুট লাইভ নিচে দেখতে পাবেন..._`);
        if (isSlashCommand) {
          headerTitle = `⚡ *[AGY NATIVE COMMAND · ${firstLine.split(/\s+/)[0]}]*`;
          subMsg = `⌨️ _টার্মিনাল কীস্ট্রোক পাথ দিয়ে নেটিভভাবে এক্সিকিউট হচ্ছে..._`;
        }
        sendWhatsAppMessage(`⏳ ══════════════════════ ⏳\n${headerTitle}\n━━━━━━━━━━━━━━━━━━━━━\n> 💬 *আপনার নির্দেশনা:* "${shortPrompt}"\n\n${subMsg}\n══════════════════════`, { to: sender }).catch(() => {});
      } catch (e) {}
    }
  });

  // Request pairing code if not registered
  setTimeout(async () => {
    if (!sock.authState.creds.registered) {
      try {
        console.log(`[WA Bridge] Requesting pairing code for ${TARGET_PHONE}...`);
        const code = await sock.requestPairingCode(TARGET_PHONE);
        console.log(`[WA Bridge] 🔑 PAIRING CODE: ${code}`);
        fs.writeFileSync(PAIRING_FILE, code, 'utf8');
      } catch (err) {
        console.error('[WA Bridge] Failed to get pairing code:', err);
      }
    }
  }, 3500);
}


// Watch transcript for real-time live streaming to WhatsApp
// Design: Clean, minimal, WhatsApp-native formatting only
const convTrackers = new Map();
let lastToolNoticeTime = 0;

const activeTranscriptJobs = new Set();

async function processSingleTranscript(transcriptPath) {
  if (!fs.existsSync(transcriptPath)) return;

  let tracker = convTrackers.get(transcriptPath);
  if (!tracker) {
    let maxIndex = 0;
    let maxPlanner = 0;
    try {
      const initialContent = fs.readFileSync(transcriptPath, 'utf8');
      const lines = initialContent.trim().split('\n');
      for (const l of lines) {
        if (!l.trim()) continue;
        try {
          const s = JSON.parse(l);
          if (s.step_index && s.step_index > maxIndex) maxIndex = s.step_index;
          if (s.type === 'PLANNER_RESPONSE' && s.content && s.step_index > maxPlanner) maxPlanner = s.step_index;
        } catch (e) {}
      }
    } catch (e) {}

    tracker = {
      lastSeenStepIndex: maxIndex,
      lastSentReplyIndex: maxPlanner,
      currentTurnTools: [],
      currentTurnHasThinking: false,
      currentTurnThinkingLength: 0,
      isSendingReply: false
    };
    convTrackers.set(transcriptPath, tracker);
    return;
  }

  const targetInfo = getTargetInfoForTranscript(transcriptPath);
  const targetJid = targetInfo.jid;
  const targetWindow = targetInfo.window;

  let content = '';
  try {
    content = fs.readFileSync(transcriptPath, 'utf8');
  } catch (e) {
    return;
  }
  const lines = content.trim().split('\n');

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;
    let step;
    try {
      step = JSON.parse(line);
    } catch (parseErr) {
      continue;
    }
    const stepIdx = step?.step_index;
    if (!stepIdx || stepIdx <= tracker.lastSeenStepIndex) continue;
    tracker.lastSeenStepIndex = stepIdx;
    try {

      // ── 0. CLI User Input Echo ──
      if (step.type === 'USER_INPUT' && step.content) {
        let reqText = step.content;
        const match = reqText.match(/<USER_REQUEST>([\s\S]*?)<\/USER_REQUEST>/);
        if (match) reqText = match[1];
        reqText = reqText.replace(/<ADDITIONAL_METADATA>[\s\S]*?<\/ADDITIONAL_METADATA>/g, '').trim();

        const cleanCompare = reqText.replace(/\s+/g, ' ').trim();
        const cleanDispatched = (lastWaDispatchedPromptByWindow[targetWindow] || '').replace(/\s+/g, ' ').trim();

        const isFromWhatsApp = cleanDispatched && (
          cleanCompare === cleanDispatched ||
          cleanCompare.includes(cleanDispatched) ||
          cleanDispatched.includes(cleanCompare)
        );

        if (isFromWhatsApp) {
          lastWaDispatchedPromptByWindow[targetWindow] = null;
        } else {
          const displayPrompt = reqText.length > 300 ? reqText.substring(0, 290) + '...' : reqText;
          await sendWhatsAppMessage(`💻 ══════════════════════ 💻\n👑 *[সিএলআই টার্মিনাল থেকে ইনপুট · ${targetWindow}]*\n━━━━━━━━━━━━━━━━━━━━━\n> 💬 "${displayPrompt}"\n\n⚡ _এআই প্রসেসিং শুরু করেছে..._\n══════════════════════`, { to: targetJid });
          console.log(`[WA Bridge] 💻 Forwarded CLI user prompt for ${targetWindow} to WhatsApp (step ${stepIdx})`);
        }
      }

      // ── 0. Thinking (Ctrl+o Expanded Detail) ──
      if (step.type === 'PLANNER_RESPONSE' && step.thinking && step.thinking.length > 10) {
        tracker.currentTurnHasThinking = true;
        if (!tracker.currentTurnThinkingLength || step.thinking.length > tracker.currentTurnThinkingLength) {
          tracker.currentTurnThinkingLength = step.thinking.length;
        }
        const thinkLines = step.thinking.trim().split('\n').filter(l => l.trim());
        let summary = thinkLines[0] || '';
        if (summary.startsWith('**')) summary = summary.replace(/\*\*/g, '');
        if (summary.length > 140) summary = summary.substring(0, 135) + '...';
        if (summary) {
          await sendWhatsAppMessage(`> 🧠 *[চিন্তাভাবনা · Ctrl+o]*\n> _${summary}_`, { to: targetJid });
          console.log(`[WA Bridge] 🧠 thinking ${stepIdx} (${targetWindow})`);
        }
      }

      // ── 1. Tool Calls (Ctrl+o Expanded: Diffs, Lines, Commands) ──
      if (step.tool_calls && Array.isArray(step.tool_calls) && step.tool_calls.length > 0) {
        for (const tc of step.tool_calls) {
          const action = tc.args?.toolAction || tc.args?.toolSummary || '';
          tracker.currentTurnTools.push({ name: tc.name, args: tc.args });

          if (tc.name === 'run_command' && tc.args?.CommandLine) {
            const cmd = tc.args.CommandLine.replace(/^"/, '').replace(/"$/, '');
            const shortCmd = cmd.length > 180 ? cmd.substring(0, 175) + '...' : cmd;
            let msg = `> ⚡ *[টার্মিনাল কমান্ড · Ctrl+o]*\n> \`$ ${shortCmd}\``;
            if (action) msg += `\n> 🎯 _${action}_`;
            tracker.pendingCommand = { cmd: shortCmd, stepIdx };
            await sendWhatsAppMessage(msg, { to: targetJid });
            console.log(`[WA Bridge] ⚡ cmd ${stepIdx} (${targetWindow})`);

          } else if (tc.name === 'replace_file_content') {
            const file = (tc.args?.TargetFile || '').replace(/^"/, '').replace(/"$/, '');
            const sLine = tc.args?.StartLine;
            const eLine = tc.args?.EndLine;
            const inst = tc.args?.Instruction || tc.args?.Description || '';
            const targetC = (tc.args?.TargetContent || '').trim();
            const replaceC = (tc.args?.ReplacementContent || '').trim();

            let msg = `> 📝 *[কোড এডিট · Ctrl+o]*\n> 📄 \`${file}\`${(sLine && eLine) ? ` (Lines ${sLine}–${eLine})` : ''}`;
            if (inst) msg += `\n> 🎯 _${inst}_`;
            if (targetC || replaceC) {
              const shortTarget = targetC.length > 320 ? targetC.substring(0, 310) + '\n... [বাকি অংশ]' : targetC;
              const shortReplace = replaceC.length > 320 ? replaceC.substring(0, 310) + '\n... [বাকি অংশ]' : replaceC;
              if (shortTarget) msg += `\n> 🔻 *আগের কোড:*\n\`\`\`\n${shortTarget}\n\`\`\``;
              if (shortReplace) msg += `\n> 🔺 *নতুন কোড:*\n\`\`\`\n${shortReplace}\n\`\`\``;
            }
            await sendWhatsAppMessage(msg, { to: targetJid });
            console.log(`[WA Bridge] 📝 edit ${stepIdx} (${targetWindow})`);

          } else if (tc.name === 'write_to_file') {
            const file = (tc.args?.TargetFile || '').replace(/^"/, '').replace(/"$/, '');
            const desc = tc.args?.Description || tc.args?.Instruction || '';
            const code = (tc.args?.CodeContent || '').trim();
            let msg = `> 📝 *[নতুন ফাইল তৈরি / লিখন · Ctrl+o]*\n> 📄 \`${file}\``;
            if (desc) msg += `\n> 🎯 _${desc}_`;
            if (code) {
              const shortCode = code.length > 320 ? code.substring(0, 310) + '\n... [বাকি অংশ]' : code;
              msg += `\n> 📄 *ফাইলের কোড:*\n\`\`\`\n${shortCode}\n\`\`\``;
            }
            await sendWhatsAppMessage(msg, { to: targetJid });
            console.log(`[WA Bridge] 📝 write ${stepIdx} (${targetWindow})`);

          } else if (tc.name === 'view_file') {
            const file = (tc.args?.AbsolutePath || '').replace(/^"/, '').replace(/"$/, '');
            const sLine = tc.args?.StartLine;
            const eLine = tc.args?.EndLine;
            const action = tc.args?.toolAction || tc.args?.toolSummary || '';
            let lineInfo = '';
            if (sLine && eLine) {
              lineInfo = ` (Lines ${sLine}–${eLine})`;
            } else if (sLine) {
              lineInfo = ` (From Line ${sLine})`;
            }
            let msg = `> 👁️ *[ফাইল পরিদর্শন · Ctrl+o]*\n> 📄 \`${file}\`${lineInfo}`;
            if (action) msg += `\n> 🎯 _${action}_`;
            await sendWhatsAppMessage(msg, { to: targetJid });
            console.log(`[WA Bridge] 👁️ view ${stepIdx} (${targetWindow})`);

          } else if (tc.name === 'grep_search' || tc.name === 'find_by_name') {
            const query = (tc.args?.Query || tc.args?.Pattern || '').replace(/^"/, '').replace(/"$/, '');
            const dir = (tc.args?.SearchPath || tc.args?.DirectoryPath || '').replace(/^"/, '').replace(/"$/, '');
            let msg = `> 🔍 *[কোডবেস সার্চ · Ctrl+o]*\n> 🔎 \`${query}\`${dir ? ` in \`${dir}\`` : ''}`;
            if (action) msg += `\n> 🎯 _${action}_`;
            await sendWhatsAppMessage(msg, { to: targetJid });
            console.log(`[WA Bridge] 🔍 search ${stepIdx} (${targetWindow})`);

          } else if (tc.name === 'search_web') {
            const query = (tc.args?.query || '').replace(/^"/, '').replace(/"$/, '');
            let msg = `> 🌐 *[ওয়েব সার্চ · Ctrl+o]*\n> 🔎 \`${query}\``;
            if (action) msg += `\n> 🎯 _${action}_`;
            await sendWhatsAppMessage(msg, { to: targetJid });
            console.log(`[WA Bridge] 🌐 web ${stepIdx} (${targetWindow})`);

          } else if (tc.name === 'read_url_content') {
            const url = (tc.args?.Url || '').replace(/^"/, '').replace(/"$/, '');
            let msg = `> 🔗 *[URL পড়ছি · Ctrl+o]*\n> 🌐 \`${url.substring(0, 80)}\``;
            if (action) msg += `\n> 🎯 _${action}_`;
            await sendWhatsAppMessage(msg, { to: targetJid });
            console.log(`[WA Bridge] 🔗 url ${stepIdx} (${targetWindow})`);

          } else if (tc.name === 'manage_task') {
            const a = (tc.args?.Action || '').replace(/^"/, '').replace(/"$/, '');
            const tid = (tc.args?.TaskId || '').replace(/^"/, '').replace(/"$/, '');
            let msg = `> ⏱️ *[টাস্ক ম্যানেজমেন্ট · Ctrl+o]*\n> ⚙️ অ্যাকশন: \`${a}\`${tid ? ` (Task: \`${tid}\`)` : ''}`;
            if (action) msg += `\n> 🎯 _${action}_`;
            await sendWhatsAppMessage(msg, { to: targetJid });
            console.log(`[WA Bridge] ⏱️ task ${stepIdx} (${targetWindow})`);

          } else if (tc.name === 'list_dir') {
            const dir = (tc.args?.DirectoryPath || '').replace(/^"/, '').replace(/"$/, '');
            let msg = `> 📂 *[ডিরেক্টরি পরিদর্শন · Ctrl+o]*\n> 📁 \`${dir}\``;
            if (action) msg += `\n> 🎯 _${action}_`;
            await sendWhatsAppMessage(msg, { to: targetJid });
            console.log(`[WA Bridge] 📂 dir ${stepIdx} (${targetWindow})`);

          } else {
            await sendWhatsAppMessage(`> 🔧 *[টুল এক্সিকিউশন · Ctrl+o]*\n> \`${tc.name}\`${action ? `\n> 🎯 _${action}_` : ''}`, { to: targetJid });
            console.log(`[WA Bridge] 🔧 ${tc.name} ${stepIdx} (${targetWindow})`);
          }
        }
      }

      // ── 2. Terminal Output Streaming (GENERIC step / Tool Output · Ctrl+o) ──
      if ((step.type === 'GENERIC' || step.type === 'TOOL_RESPONSE') && step.content && tracker.pendingCommand) {
        let rawOutput = step.content.trim();
        let cleanOutput = '';
        if (rawOutput.includes('Output:\n')) {
          cleanOutput = rawOutput.split('Output:\n').slice(1).join('Output:\n').trim();
        } else if (rawOutput.includes('The command exited with code')) {
          const cLines = rawOutput.split('\n');
          cleanOutput = cLines.slice(2).join('\n').trim();
        } else {
          cleanOutput = rawOutput;
        }

        if (cleanOutput && cleanOutput !== '(no output)' && !cleanOutput.startsWith('Created At:')) {
          if (cleanOutput.length > 450) {
            cleanOutput = cleanOutput.substring(0, 440) + '\n... [আউটপুট সংক্ষেপিত]';
          }
          await sendWhatsAppMessage(`> 💻 *[কমান্ড আউটপুট · Ctrl+o]*\n\`\`\`\n${cleanOutput}\n\`\`\``, { to: targetJid });
          console.log(`[WA Bridge] 💻 cmd output ${stepIdx} (${targetWindow})`);
        }
        tracker.pendingCommand = null;
      }

      if (stepIdx > tracker.lastSeenStepIndex) tracker.lastSeenStepIndex = stepIdx;

      // ── 3. Final Reply ──
      if (step.type === 'PLANNER_RESPONSE' && step.content && stepIdx > tracker.lastSentReplyIndex && !tracker.isSendingReply) {
        tracker.isSendingReply = true;
        tracker.lastSentReplyIndex = stepIdx;
        console.log(`[WA Bridge] 📤 Turn done for ${targetWindow} (step ${stepIdx})`);

        let finalContent = step.content;
        const truncFields = step.truncated_fields || [];
        if (truncFields.includes('content')) {
          const fullPath = transcriptPath.replace('transcript.jsonl', 'transcript_full.jsonl');
          if (fs.existsSync(fullPath)) {
            try {
              const fullLines = fs.readFileSync(fullPath, 'utf8').trim().split('\n');
              for (let j = fullLines.length - 1; j >= 0; j--) {
                const fl = fullLines[j].trim();
                if (!fl) continue;
                const fsObj = JSON.parse(fl);
                if (fsObj.step_index === stepIdx && fsObj.content) {
                  finalContent = fsObj.content;
                  break;
                }
              }
            } catch (e) {}
          }
        }

        const cleanedContent = cleanModelOutput(finalContent);
        const mobileContent = wrapForMobile(cleanedContent, 48);
        const pasteUrl = await uploadToPasteRs(mobileContent);
        console.log('[WA Bridge] paste.rs (mobile-wrapped):', pasteUrl);

        const { modelName, modeName } = getVerifiedModelInfo(targetWindow);
        const now = new Date();
        const timeStr = now.toLocaleTimeString('bn-BD', { timeZone: 'Asia/Dhaka', hour: '2-digit', minute: '2-digit', hour12: true });

        let footer = '\n\n```\n';
        footer += '╭─ SESSION DATA ──────────────╮\n';
        footer += '│ 🕐 TIME  · ' + timeStr.padEnd(17) + '│\n';
        footer += '│ 🤖 MODEL · ' + modelName.padEnd(17) + '│\n';
        footer += '│ ⚡ MODE   · ' + modeName.padEnd(17) + '│\n';
        footer += '╰─────────────────────────────╯\n```';

        const waContent = formatMarkdownForWhatsApp(cleanedContent);
        let body = `╭─ NEURAL RESPONSE ─╮\n${waContent}\n╰──────────────────╯`;
        let completionAccent = '✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅\n\n';
        if (targetWindow === 'agy:yt' || targetWindow.includes('yt') || (targetJid && targetJid.includes('120363430650656655'))) {
          completionAccent = '▶️ ▶️ ▶️ ▶️ ▶️ ▶️ ▶️ ▶️ ▶️ ▶️ ▶️ ▶️ ▶️\n\n';
        } else if (targetWindow === 'agy:report' || targetWindow.includes('report') || (targetJid && targetJid.includes('120363430377910102'))) {
          completionAccent = '📈 📈 📈 📈 📈 📈 📈 📈 📈 📈 📈 📈 📈\n\n';
        }
        const linkHeader = pasteUrl ? `🔗 ${pasteUrl}\n\n` : '';
        const footerAccent = '\n✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅';
        let fullReply = completionAccent + linkHeader + body + footer + footerAccent;

        if (fullReply.length > 60000) {
          body = body.substring(0, 58000) + (pasteUrl ? `\n\n_... সম্পূর্ণ পড়তে উপরের লিঙ্কটি দেখুন_` : '');
          fullReply = completionAccent + linkHeader + body + footer + footerAccent;
        }

        const quoteMsg = lastUserMsgByWindow[targetWindow] || lastUserMsg;
        await sendWhatsAppMessage(fullReply, { to: targetJid, quoted: quoteMsg });

        tracker.currentTurnTools = [];
        tracker.currentTurnHasThinking = false;
        tracker.currentTurnThinkingLength = 0;

        console.log(`[WA Bridge] ✅ Reply delivered to ${targetJid} (${targetWindow})!`);
        autoController.stopTracking(targetWindow);
        tracker.isSendingReply = false;
        windowBusy[targetWindow] = false;

        // triggerCodexPeerReview disabled per user directive: Codex must not audit or dispatch to master agent

        drainNextPromptForWindow(targetWindow);
      }
    } catch (e) {
      console.error(`[WA Bridge] Step error on ${targetWindow}:`, e.message);
    }
  }
}

let lastCodexRolloutPath = null;
let lastCodexLineCount = 0;
let lastCodexKnownLineCount = 0;
let lastCodexFileSize = -1;
let lastCodexHeartbeatTime = 0;
let lastCodexOutputTime = Date.now();
let newestCodexRolloutScanTime = 0;
let newestCodexRolloutCache = null;

function findNewestCodexRollout() {
  if (Date.now() - newestCodexRolloutScanTime < 1000) return newestCodexRolloutCache;
  newestCodexRolloutScanTime = Date.now();
  const baseDir = '/home/azureuser/.codex/sessions';
  if (!fs.existsSync(baseDir)) return null;
  let newest = null;
  let maxMtime = 0;
  function walk(dir) {
    try {
      const entries = fs.readdirSync(dir, { withFileTypes: true });
      for (const e of entries) {
        const full = path.join(dir, e.name);
        if (e.isDirectory()) {
          walk(full);
        } else if (e.isFile() && e.name.startsWith('rollout-') && e.name.endsWith('.jsonl')) {
          try {
            const m = fs.statSync(full).mtimeMs;
            if (m > maxMtime) {
              maxMtime = m;
              newest = full;
            }
          } catch (err) {}
        }
      }
    } catch (err) {}
  }
  walk(baseDir);
  newestCodexRolloutCache = newest;
  return newest;
}

function getCodexModelInfo() {
  try {
    const configPath = '/home/azureuser/.codex/config.toml';
    if (fs.existsSync(configPath)) {
      const content = fs.readFileSync(configPath, 'utf8');
      const mMatch = content.match(/^model\s*=\s*"([^"]+)"/m);
      const eMatch = content.match(/^model_reasoning_effort\s*=\s*"([^"]+)"/m);
      if (mMatch) {
        let slug = mMatch[1];
        let name = slug;
        if (slug === 'gpt-6-luna') name = 'GPT-6-Luna';
        else if (slug === 'gpt-6.1-sol') name = 'GPT-6.1-Sol';
        else if (slug === 'gpt-6-sol') name = 'GPT-6-Sol';
        else if (slug === 'gpt-6-astra') name = 'GPT-6-Astra';
        else if (slug === 'gpt-5.6-luna') name = 'GPT-5.6-Luna';
        else if (slug === 'gpt-5.6-sol') name = 'GPT-5.6-Sol';
        if (eMatch && eMatch[1]) {
          name += ` (${eMatch[1]})`;
        }
        return name;
      }
    }
  } catch (e) {}
  return 'GPT-6-Luna (low)';
}

let activeCodexModelName = null;
const sentCodexMsgIds = new Set();
let isProcessingCodexRollout = false;
let lastCodexPollTime = 0;
const sentCodexChunkIds = new Set();
let activeCodexTurnId = null;
let lastCompletedCodexTurnId = null;
const completedCodexTurnIds = new Set();
const pendingCodexFinalReplies = new Map();

function cleanCodexActivityText(value) {
  return String(value ?? '')
    .replace(/\x1B(?:\[[0-?]*[ -/]*[@-~]|\][^\x07]*(?:\x07|\x1B\\))/g, '')
    .replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '');
}

function splitCodexWhatsAppText(value, maxChars = 12000) {
  const chars = Array.from(cleanCodexActivityText(value));
  if (chars.length <= maxChars) return [chars.join('')];
  const chunks = [];
  for (let start = 0; start < chars.length;) {
    let end = Math.min(start + maxChars, chars.length);
    if (end < chars.length) {
      const newline = chars.lastIndexOf('\n', end - 1);
      if (newline > start + Math.floor(maxChars * 0.7)) end = newline + 1;
    }
    chunks.push(chars.slice(start, end).join(''));
    start = end;
  }
  return chunks.map((chunk, i) => '[' + (i + 1) + '/' + chunks.length + ']\n' + chunk);
}

async function sendCodexChunked(text, targets, eventId) {
  const chunks = splitCodexWhatsAppText(text);
  let delivered = true;
  const stableId = String(eventId || Date.now());
  for (const target of [...new Set((targets || []).filter(Boolean))]) {
    for (let i = 0; i < chunks.length; i++) {
      const deliveryId = stableId + '\u001f' + target + '\u001f' + i;
      if (sentCodexChunkIds.has(deliveryId)) continue;
      const result = await sendWhatsAppMessage(chunks[i], { to: target });
      if (!result || !result.key) {
        delivered = false;
      } else {
        sentCodexChunkIds.add(deliveryId);
        if (sentCodexChunkIds.size > 30000) {
          const oldest = sentCodexChunkIds.values().next().value;
          sentCodexChunkIds.delete(oldest);
        }
      }
    }
  }
  return delivered;
}

async function processCodexRollout() {
  const now = Date.now();
  if (isProcessingCodexRollout || now - lastCodexPollTime < 500) return;
  lastCodexPollTime = now;
  isProcessingCodexRollout = true;
  try {
    if (!sock || !isWsConnected) return;
    const newest = findNewestCodexRollout();
    if (!newest) return;

    const pGroups = getProjectGroupMap();
    const groupJid = (pGroups.codex && pGroups.codex.id && pGroups.codex.id.endsWith('@g.us') && !pGroups.codex.id.includes('pending')) ? pGroups.codex.id : null;
    const codexTargets = groupJid ? [groupJid] : [];

    const isInitialRollout = lastCodexRolloutPath === null;
    if (newest !== lastCodexRolloutPath) {
      lastCodexRolloutPath = newest;
      lastCodexLineCount = 0;
      lastCodexKnownLineCount = 0;
      lastCodexFileSize = -1;
    }

    let content = '';
    let rolloutSize = -1;
    try {
      const stat = fs.statSync(newest);
      rolloutSize = stat.size;
      if (!isInitialRollout && rolloutSize === lastCodexFileSize && lastCodexLineCount === lastCodexKnownLineCount) return;
      content = fs.readFileSync(newest, 'utf8');
    } catch (e) {
      return;
    }

    const rawLines = content.split('\n');
    if (!content.endsWith('\n')) rawLines.pop();
    const allLines = rawLines.filter(Boolean);
    if (isInitialRollout) {
      // The bridge starts while Codex is idle; establish an EOF cursor and never replay old replies.
      lastCodexLineCount = allLines.length;
      lastCodexKnownLineCount = allLines.length;
      lastCodexFileSize = rolloutSize;
      return;
    }
    if (allLines.length <= lastCodexLineCount) {
      lastCodexFileSize = rolloutSize;
      lastCodexKnownLineCount = allLines.length;
      return;
    }

    lastCodexOutputTime = Date.now();
    const newLines = allLines.slice(lastCodexLineCount);
    let retryAtLineIndex = null;

    for (let newLineIndex = 0; newLineIndex < newLines.length; newLineIndex++) {
      const l = newLines[newLineIndex];
      try {
        const obj = JSON.parse(l);
        const p = obj.payload || {};

        // Forward the real persisted task lifecycle event; this is not a generated progress message.
        if (obj.type === 'event_msg' && p.type === 'task_started') {
          const turnId = p.turn_id || p.root_turn_id || l;
          activeCodexTurnId = turnId;
          lastCompletedCodexTurnId = null;
          const started = '▶️ [Codex turn started]' + (p.turn_id ? '\nturn id: ' + p.turn_id : '');
          const delivered = await sendCodexChunked(started, codexTargets, turnId);
          if (delivered) sentCodexMsgIds.add('task-start:' + turnId);
          else retryAtLineIndex = retryAtLineIndex === null ? newLineIndex : Math.min(retryAtLineIndex, newLineIndex);
        }

        // Forward real user-visible lifecycle and tool-start events from Codex.
        if (obj.type === 'event_msg' && p.type === 'task_complete') {
          const turnId = p.turn_id || p.root_turn_id || activeCodexTurnId || l;
          const details = [
            '[Codex turn complete]',
            p.duration_ms !== undefined ? 'duration_ms: ' + p.duration_ms : '',
            p.error ? 'error: ' + JSON.stringify(p.error) : ''
          ].filter(Boolean).join('\n');
          const completionId = 'task-complete:' + turnId;
          let delivered = sentCodexMsgIds.has(completionId);
          if (!delivered) {
            delivered = await sendCodexChunked(details, codexTargets, completionId);
            if (delivered) sentCodexMsgIds.add(completionId);
          }
          if (delivered) {
            completedCodexTurnIds.add(turnId);
            if (completedCodexTurnIds.size > 1000) completedCodexTurnIds.delete(completedCodexTurnIds.values().next().value);
            lastCompletedCodexTurnId = turnId;
            if (activeCodexTurnId === turnId) activeCodexTurnId = null;
            const pendingReply = pendingCodexFinalReplies.get(turnId);
            if (pendingReply) {
              const replyDelivered = await sendCodexChunked(pendingReply.reply, codexTargets, pendingReply.msgId);
              if (replyDelivered) {
                sentCodexMsgIds.add(pendingReply.msgId);
                pendingCodexFinalReplies.delete(turnId);
                console.log('[WA Bridge] Codex final answer delivered after its turn-complete notice');
              } else {
                retryAtLineIndex = retryAtLineIndex === null ? newLineIndex : Math.min(retryAtLineIndex, newLineIndex);
              }
            }
          } else {
            retryAtLineIndex = retryAtLineIndex === null ? newLineIndex : Math.min(retryAtLineIndex, newLineIndex);
          }
        }

        if (obj.type === 'event_msg' && (p.type === 'warning' || p.type === 'error')) {
          const eventId = p.id || p.turn_id || (p.type + ':' + l);
          const details = '[Codex ' + p.type + ']\n' + (p.message || (p.error && p.error.message) || JSON.stringify(p));
          const delivered = await sendCodexChunked(details, codexTargets, eventId);
          if (delivered) sentCodexMsgIds.add(eventId);
          else retryAtLineIndex = retryAtLineIndex === null ? newLineIndex : Math.min(retryAtLineIndex, newLineIndex);
        }

        if (obj.type === 'event_msg' && p.type === 'item_started' && p.item) {
          const item = p.item;
          if (['CommandExecution', 'McpToolCall', 'WebSearch', 'FileChange'].includes(item.type)) {
            const activityId = (item.id || (item.type + ':' + l)) + ':started';
            let details = '[Codex ' + item.type + ' started]\n';
            if (item.type === 'CommandExecution') {
              const cmd = Array.isArray(item.command) ? item.command.join(' ') : (item.command || '');
              details += '$ ' + cmd + (item.cwd ? '\ncwd: ' + item.cwd : '');
            } else {
              details += JSON.stringify(item, null, 2);
            }
            const delivered = await sendCodexChunked(details, codexTargets, activityId);
            if (delivered) sentCodexMsgIds.add(activityId);
            else retryAtLineIndex = retryAtLineIndex === null ? newLineIndex : Math.min(retryAtLineIndex, newLineIndex);
          }
        }

        // 0. Turn Context (Active Model & Reasoning Effort)
        if (obj.type === 'turn_context' && p) {
          if (p.model) {
            let mName = p.model;
            if (mName === 'gpt-6-luna') mName = 'GPT-6-Luna';
            else if (mName === 'gpt-6.1-sol') mName = 'GPT-6.1-Sol';
            else if (mName === 'gpt-6-sol') mName = 'GPT-6-Sol';
            else if (mName === 'gpt-6-astra') mName = 'GPT-6-Astra';
            else if (mName === 'gpt-5.6-luna') mName = 'GPT-5.6-Luna';
            else if (mName === 'gpt-5.6-sol') mName = 'GPT-5.6-Sol';
            const eff = p.effort || (p.collaboration_mode && p.collaboration_mode.settings && p.collaboration_mode.settings.reasoning_effort);
            if (eff) {
              mName += ` (${eff})`;
            }
            activeCodexModelName = mName;
          }
        }

        // Forward public assistant progress; intentionally exclude internal Reasoning items.
        if (obj.type === 'response_item' && p.role === 'assistant' && p.phase === 'commentary' && Array.isArray(p.content)) {
          lastCodexOutputTime = Date.now();
          const progressId = p.id || l;
          if (!sentCodexMsgIds.has(progressId)) {
            const progress = p.content.map(c => c.text || '').filter(Boolean).join('\n').trim();
            if (progress) {
              const delivered = await sendCodexChunked('🧠 [Codex অগ্রগতি]\n' + progress, codexTargets, progressId);
              if (delivered) {
                sentCodexMsgIds.add(progressId);
              } else {
                retryAtLineIndex = retryAtLineIndex === null ? newLineIndex : Math.min(retryAtLineIndex, newLineIndex);
              }
              if (delivered) {
                console.log('[WA Bridge] Codex progress delivered');
              }
            }
          }
        }

        // Codex persists full command output in this structured item when execution completes.
        if (obj.type === 'event_msg' && p.type === 'item_completed' && p.item) {
          const item = p.item;
          if (item.type === 'CommandExecution') {
            const execId = item.id || JSON.stringify(item.command);
            if (!sentCodexMsgIds.has(execId)) {
              const cmdArr = Array.isArray(item.command) ? item.command : [item.command || ''];
              let cmd = cmdArr.join(' ');
              if (cmdArr.length >= 3 && (cmdArr[0] === '/bin/bash' || cmdArr[0] === 'bash') && cmdArr[1] === '-lc') {
                cmd = cmdArr.slice(2).join(' ');
              }
              const stdout = item.stdout || '';
              const stderr = item.stderr || '';
              const combinedOutput = (!stdout && !stderr) ? (item.aggregated_output || item.formatted_output || '') : '';
              const report = [
                '⚡ [Codex কমান্ড সম্পন্ন]',
                '$ ' + cmd,
                item.cwd ? 'cwd: ' + item.cwd : '',
                item.status ? 'status: ' + item.status : '',
                item.exit_code !== undefined ? 'exit code: ' + item.exit_code : '',
                item.duration ? 'duration: ' + JSON.stringify(item.duration) : '',
                stdout ? '--- stdout ---\n' + stdout : '',
                stderr ? '--- stderr ---\n' + stderr : '',
                combinedOutput ? '--- command output (Codex-aggregated; stdout/stderr not separated) ---\n' + combinedOutput : ''
              ].filter(Boolean).join('\n');
              const delivered = await sendCodexChunked(report, codexTargets, execId);
              if (delivered) sentCodexMsgIds.add(execId);
              else retryAtLineIndex = retryAtLineIndex === null ? newLineIndex : Math.min(retryAtLineIndex, newLineIndex);
              console.log('[WA Bridge] Codex command result bytes=' + (Buffer.byteLength(stdout) + Buffer.byteLength(stderr)) + ' delivered=' + delivered);
            }
          } else if (item.type === 'FileChange' || item.type === 'McpToolCall' || item.type === 'WebSearch') {
            const activityId = item.id || (item.type + ':' + l);
            if (!sentCodexMsgIds.has(activityId)) {
              const delivered = await sendCodexChunked('[Codex ' + item.type + ' activity]\n' + JSON.stringify(item, null, 2), codexTargets, activityId);
              if (delivered) sentCodexMsgIds.add(activityId);
              else retryAtLineIndex = retryAtLineIndex === null ? newLineIndex : Math.min(retryAtLineIndex, newLineIndex);
              console.log('[WA Bridge] Codex ' + item.type + ' activity delivered=' + delivered);
            }
          }
        }

        // 3. Final Answer
        if (obj.type === 'response_item' && p.role === 'assistant' && p.phase === 'final_answer' && Array.isArray(p.content)) {
          const msgId = p.id || l;
          if (!sentCodexMsgIds.has(msgId)) {
            let reply = '';
            for (const c of p.content) {
              if (c.type === 'output_text' && c.text) {
                const text = c.text.trim();
                if (text.length > 0) {
                  const now = new Date();
                  const timeStr = now.toLocaleTimeString('bn-BD', { timeZone: 'Asia/Dhaka', hour: '2-digit', minute: '2-digit', hour12: true });
                  const codexModelName = activeCodexModelName || getCodexModelInfo();
                  let footer = '\n\n```\n';
                  footer += '╭─ SESSION DATA ──────────────╮\n';
                  footer += '│ 🕐 TIME  · ' + timeStr.padEnd(17) + '│\n';
                  footer += '│ 🤖 MODEL · ' + codexModelName.padEnd(17) + '│\n';
                  footer += '│ ⚡ ENGINE· OpenAI Codex CLI │\n';
                  footer += '╰─────────────────────────────╯\n```';
                  reply = '🤖 ══════════════════════ 🤖\n👑 *[AGY · OPENAI CODEX · রেসপন্স]*\n━━━━━━━━━━━━━━━━━━━━━\n\n' + text + footer + '\n══════════════════════';
                }
              }
            }
            if (reply) {
              const turnId = activeCodexTurnId || lastCompletedCodexTurnId || p.turn_id || p.root_turn_id || msgId;
              if (completedCodexTurnIds.has(turnId)) {
                const replyDelivered = await sendCodexChunked(reply, codexTargets, msgId);
                if (replyDelivered) {
                  sentCodexMsgIds.add(msgId);
                  console.log('[WA Bridge] Codex final answer delivered to configured WhatsApp targets');
                } else {
                  retryAtLineIndex = retryAtLineIndex === null ? newLineIndex : Math.min(retryAtLineIndex, newLineIndex);
                  console.error('[WA Bridge] Codex final answer delivery incomplete for rollout event ' + msgId);
                }
              } else {
                pendingCodexFinalReplies.set(turnId, { msgId, reply });
                console.log('[WA Bridge] Holding Codex final answer until its turn-complete notice');
              }
            }
          }
        }
      } catch (parseE) {}
    }
    lastCodexKnownLineCount = allLines.length;
    lastCodexFileSize = rolloutSize;
    lastCodexLineCount = retryAtLineIndex === null ? allLines.length : lastCodexLineCount + retryAtLineIndex;
  } catch (err) {
    console.error('[WA Bridge] Codex watcher error:', err.message);
  } finally {
    isProcessingCodexRollout = false;
  }
}

async function triggerCodexPeerReview(targetWindow, targetJid, rawContent) {
  // Disconnected per user directive: do not run codex peer reviews or dispatch codex reports to master agent
  return;
}

function watchReplies() {
  setInterval(() => {
    if (!sock || !sock.authState.creds.registered) return;

    processWaOutbox().catch(err => {
      console.error('[WA Bridge] Outbox processing error:', err.message);
    });

    processCodexRollout().catch(err => {
      console.error('[WA Bridge] Codex rollout watcher error:', err.message);
    });

    try {
      const recentTranscripts = findRecentTranscripts();
      if (!recentTranscripts || recentTranscripts.length === 0) return;

      for (const transcriptPath of recentTranscripts) {
        if (activeTranscriptJobs.has(transcriptPath)) continue;

        activeTranscriptJobs.add(transcriptPath);
        processSingleTranscript(transcriptPath)
          .catch(err => {
            console.error('[WA Bridge] Transcript error:', err.message);
          })
          .finally(() => {
            activeTranscriptJobs.delete(transcriptPath);
          });
      }
    } catch (err) {
      console.error('[WA Bridge] Watcher poll error:', err.message);
    }
  }, 500);
}

function startQueueWatchdog() {
  setInterval(() => {
    try {
      const queue = loadDurableQueue();
      // Reconcile and drain any HELD_FOR_ZIP items whose gate has opened
      const heldWindows = new Set(queue.filter(q => q.status === 'HELD_FOR_ZIP').map(q => q.target_window));
      for (const win of heldWindows) {
        const gateCheck = checkZipGate(win);
        if (gateCheck && (gateCheck.action === 'ALLOW_NOW' || gateCheck.zip_gate === 'ZIP_GATE_OPEN')) {
          drainNextPromptForWindow(win);
        }
      }
      // Reconcile any RECEIVED or RETRYING items for windows that are now idle
      const pendingWindows = new Set(queue.filter(q => q.status === 'RECEIVED' || q.status === 'RETRYING').map(q => q.target_window));
      for (const win of pendingWindows) {
        if (!isWindowBusy(win)) {
          drainNextPromptForWindow(win);
        }
      }
    } catch (e) {}
  }, 3000);
}

if (require.main === module) {
  startBridge();
  watchReplies();
  startQueueWatchdog();
}

module.exports = {
  dispatchToTmux,
  getTargetPhone,
  loadProcessedMessageIds,
  saveProcessedMessageIds,
  checkZipGate,
  loadDurableQueue,
  saveDurableQueue,
  enqueueDurablePrompt,
  updateDurablePromptStatus,
  drainNextPromptForWindow,
  startQueueWatchdog,
  BANGLA_ZIP_HOLD_NOTICE,
  BANGLA_ZIP_COMPLETE_NOTICE,
  BANGLA_RECONNECT_TEMPLATE,
};
