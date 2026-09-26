# CENTRAL PROJECT REGISTRY & BOUNDARY CATALOG

Location: `/home/azureuser/AGY-MASTER/PROJECT_REGISTRY.md`  
Version: `1.0.0`  
Standard: Multi-Agent Workspace Isolation & Domain Directive Registry

---

## 1. GLOBAL & TIER-1 AGENTS

| Agent Identifier | Role | Workspace Path | Mode | Boundary Constraints |
| :--- | :--- | :--- | :--- | :--- |
| `agy:0` | Master / Principal Orchestrator | `/home/azureuser` | Orchestrator | Full workspace routing, task dispatch, final acceptance |
| `agy:ask` | Asking & Technical Research | `/home/azureuser/Ask-And-Research` | Read-Only | Global Read-Only across all projects; zero write |
| `agy:report` | Global Observability & Sentinel | `/home/azureuser/Reporting-Agent` | Audit Sentinel | Global Audit-Only; zero direct write to project code |
| `agy:action` | Incident Containment & Fixer | `/home/azureuser/Action-Agent` | Controlled Fixer | Cross-project write strictly gated by Safety Levels |

---

## 2. DOMAIN-LOCKED WORKER AGENTS (PROJECTS)

| Project Name | Domain Identifier | Canonical Workspace Path | Primary Directives |
| :--- | :--- | :--- | :--- |
| **YouTube Pipeline** | `agy:project:youtube` | `/home/azureuser/.openclaw/workspace/IROSCRIPT-CEO/social-media/youtube` | Veo 3.1 Chrome Extension only; SQLite source-of-truth; No FFmpeg/OpenCV |
| **Frappe ERPNext** | `agy:project:frappe` | `/home/azureuser/Frappe-erp-Alco` | ERPNext v16+; Python 3.12+; PyPika / `frappe.qb`; Modern JS form controller; Mobile-first |
| **Telegram Bot** | `agy:project:telegram` | `/home/azureuser/telegram-bot` | Live MTProto / Telethon search only; No local JSON/CSV search fallback |
| **Digital History** | `agy:project:history` | `/home/azureuser/.openclaw/workspace/IROSCRIPT-CEO/PERSONAL AI AGENT` | OpenRecall daemon protection; Immutable history buffer |
| **Kids Tube** | `agy:project:kids` | `/home/azureuser/kids_tube_with_folder_seection` | Folder selection UI; safe kids content parsing |
| **Rust Task** | `agy:project:rust` | `/home/azureuser/Rust_Task_With_Time_Keeping_And_Live_Note` | Cargo build verification; Axum overlay; Flutter release parity |
| **Article Publishing** | `agy:project:article` | `/home/azureuser/Article-Publishing-Platform` | CockroachDB / DB schema management; API publishing pipeline |
| **3D Game Studio** | `agy:project:game` | `/home/azureuser/3D-Game-Design-Studio` | Jungle Street View; Three.js / WebGL pipeline |

---

## 3. BOUNDARY RULES
1. Project agents are locked inside their canonical workspace.
2. Cross-project file reads, writes, and executions are denied by the gateway.
3. Common system tools (`ls`, `pwd`, `git status`, compiler commands) are allowed only within project boundary.
