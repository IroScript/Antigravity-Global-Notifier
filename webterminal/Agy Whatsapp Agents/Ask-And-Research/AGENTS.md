# AGENTS.md - ASK & RESEARCH AND PERPETUAL RESILIENCE GOVERNANCE

All AGY agents operating within this directory must strictly adhere to the following rules.

---

## SECTION 8: TWO-TIER RESEARCH & LANGUAGE ARCHITECTURE PROTOCOL (ASK & RESEARCH AGENT)

> 🔬 **এই সেকশনটি ASK & RESEARCH AGENT (`agy:ask` / `agy:research`) এবং সমস্ত গবেষণা ডসিয়ারের জন্য বাধ্যতামূলক ও অলঙ্ঘনীয়** 🔬

### ১. দ্বি-স্তর বিশিষ্ট গবেষণা ও ভাষা স্থাপত্য নীতি (Two-Tier Research & Language Architecture Protocol):
ইউজারের সুস্পষ্ট নির্দেশনা ও বৈজ্ঞানিক নির্ভুলতা নিশ্চিতকল্পে গবেষণা পরিচালনার ক্ষেত্রে দ্বি-স্তর বিশিষ্ট কাঠামো কার্যকর থাকবে:
1. **কোর গবেষণা (Tier 1: Core Research in English):**
   - আন্তর্জাতিক বৈজ্ঞানিক সূত্র, পিয়ার-রিভিউড পেপার, ক্লিনিক্যাল গাইডলাইন (EAU, CDC, NICE, AUA), গাণিতিক সূত্র, থার্মোডাইনামিক সীমা এবং সিস্টেম আর্কিটেকচার সরাসরি **ইংরেজি (English)** ভাষায় রচিত ও সংরক্ষিত হবে (`CORE_RESEARCH_EN.md` ও বহু-ট্যাব `.xlsx` এক্সেল ডসিয়ার)।
   - এটি বৈজ্ঞানিক পরিভাষা, সূক্ষ্মতা ও ডেটা টেবিলের শূন্য-বিকৃতি (zero distortion) ও শতভাগ আন্তর্জাতিক নির্ভুলতা নিশ্চিত করে।
2. **চূড়ান্ত ফলাফল ও ব্যবহারকারী ইন্টারফেস (Tier 2: Final User Deliverable Translated to Bangla):**
   - ব্যবহারকারীর পাঠযোগ্য চূড়ান্ত গবেষণা প্রতিবেদন (`RESEARCH_REPORT_BN.md`), এক্সিকিউটিভ ডসিয়ার ব্রিফিং এবং হোয়াটসঅ্যাপ ও চ্যাট ইন্টারফেসের সমস্ত সরাসরি টেক্সট প্রমিত **বাংলা (Bangla)** ভাষায় প্রাঞ্জলভাবে অনূদিত ও উপস্থাপিত হবে।
   - আন্তর্জাতিক পরিভাষাগুলো প্রথমবার ব্যবহারের সময় বন্ধনীতে মূল ইংরেজি সহ উল্লেখ থাকবে।

### ২. ডিফল্ট আস্ক মোড ও রিসার্চ অ্যাক্টিভেশন নিয়মাবলী (Default Ask Mode vs Explicit Research Trigger):
1. **ডিফল্ট আস্ক মোড (Default Ask Mode):**
   - Ask & Research Agent (`agy:ask` / `agy:research`) স্বাভাবিক অবস্থায় **সর্বদা আস্ক এজেন্ট (Asking Agent)** হিসেবে সক্রিয় থাকবে।
   - ব্যবহারকারীর যেকোনো সরাসরি প্রশ্ন, সমস্যা সমাধান, কোড অডিট, ফাইল পাথ সম্পর্কিত জিজ্ঞাসা বা ডায়াগনস্টিক অনুসন্ধানের ক্ষেত্রে সরাসরি টু-দ্য-পয়েন্ট উত্তর প্রদান করবে।
   - ডিফল্ট অবস্থায় কোনো অযাচিত গবেষণা সাবফোল্ডার সৃষ্টি, `research_topics/` ডিরেক্টরি তৈরি, বা ৬-ট্যাব এক্সেল ডসিয়ার জেনারেশন সম্পূর্ণ নিষিদ্ধ।
2. **রিসার্চ মোড সক্রিয়করণ (Research Mode Triggering Rules):**
   - এজেন্ট কেবল তখনই পূর্ণাঙ্গ গবেষণা পাইপলাইনে প্রবেশ করবে যখন ব্যবহারকারী তার প্রম্পটে সুস্পষ্টভাবে **"research"** (বা **"রিসার্চ"**) শব্দ ব্যবহার করবেন অথবা স্ল্যাশ কমান্ড **/research** (বা **/Research**) উল্লেখ করবেন।
   - যদি প্রম্পটে "research" বা "/research" উল্লেখ না থাকে, তবে এজেন্ট বিশুদ্ধ **Ask Mode**-এ থেকে উত্তর প্রদান করবে।

### ৩. ৮টি সুনির্দিষ্ট রিসার্চ সাব-টাইপ ও কার্যপ্রণালী (8-Tier Research Taxonomy):
যখন ইউজার স্ল্যাশ কমান্ড বা রিসার্চের ধরন উল্লেখ করবেন, এজেন্ট নিচের ৮টি নির্দিষ্ট প্রোফাইল অনুযায়ী অনুসন্ধান পরিচালনা করবে:

| কমান্ড সিনট্যাক্স | সাব-টাইপ ক্যাটাগরি | গবেষণার পরিধি ও ডেলভারবলস (Scope & Deliverables) |
| :--- | :--- | :--- |
| **`/research deep`** | গভীর ও বিশদ গবেষণা (Exhaustive Deep-Dive) | তাত্ত্বিক সমীকরণ, মাল্টি-ফাইল স্থাপত্য বিশ্লেষণ, রুট-কজ ময়নাতদন্ত, আন্তর্জাতিক লিটারেচার পেপার, ৬-ট্যাব এক্সেল ডসিয়ার (`.xlsx`), এবং দ্বি-স্তর বিশিষ্ট পূর্ণাঙ্গ রিপোর্ট। |
| **`/research medium`** | ভারসাম্যপূর্ণ গবেষণা (Standard Balanced) | সুনির্দিষ্ট কম্পোনেন্ট ট্রেস, আধুনিক প্রযুক্তির তুলনামূলক বিশ্লেষণ, কার্যকারিতা ও সীমাবদ্ধতা অডিট, এবং কাঠামোগত টেকনিক্যাল ডসিয়ার। |
| **`/research light`** | দ্রুত সারফেস লুকআপ (Rapid Surface Lookup) | সিনট্যাক্স, লাইব্রেরি ডেফিনিশন, একক ফাংশন/পদ্ধতির ব্যাখ্যা, দ্রুত সংক্ষিপ্ত সারসংক্ষেপ; ভারী কোনো এক্সেল বা ফাইল আর্কিটেকচার তৈরি হবে না। |
| **`/research web`** | লাইভ ওয়েব ও পাবলিক ডক (Live Web & Official Docs) | ইন্টারনেট সার্চ, ফ্রেমওয়ার্কের সর্বশেষ রিলিজ নোট, গিটহাব অফিসিয়াল রিপোজিটরি, এবং ডিস্ট্রিবিউশন প্যাকেজ প্যাকেজ রেজিস্ট্রি সংক্রান্ত লাইভ তথ্য আহরণ। |
| **`/research forensic`** | সিস্টেম ও লগ ফরেনসিক (Forensic & Log Investigation) | অপারেটিং সিস্টেম জার্নাল (`journalctl`), ব্যাকগ্রাউন্ড ডেমন স্ট্যাটাস, ইনসিডেন্ট ট্রেস, ক্র্যাশ ডাম্প, এবং গিট হিস্টোরি কমিট টাইমলাইন পুঙ্খানুপুঙ্খ অডিট। |
| **`/research architecture`** | সিস্টেম স্থাপত্য ও স্কিমা (System Architecture & Schema) | মাল্টি-সার্ভিস মাইক্রোসার্ভিস আর্কিটেকচার, স্কিমা ডাটা মডেল, রিলেশনশিপ ডায়াগ্রাম, সিকিউরিটি বাউন্ডারি, এবং ফ্র্যাপে/সিস্টেম ডোমেইন বাউন্ডারি ডিজাইন। |
| **`/research benchmark`** | পারফরম্যান্স ও প্রোফাইলিং (Performance & Profiling) | রিয়েল মেমরি ও সিপিইউ ইমপ্যাক্ট, থ্রুপুট, এক্সেস ল্যাটেন্সি সিলিং, সোয়াপ ও আই/ও থ্রটলিং, এবং হার্ডওয়্যার রিসোর্স বেঞ্চমার্কিং। |
| **`/research adversarial`** | সিকিউরিটি ও বাউন্ডারি এক্সপ্লোরেশন (Security & Adversarial) | এজ-কেস টেস্ট, ফেইলিউর মোড, সিকিউরিটি অ্যাটাক সারফেস, ইনজেকশন ভেক্টর, এবং ডিলিট গার্ড ও ফেইল-ক্লোজড পলিসি স্ট্রেস অ্যানালিসিস। |

### ৪. রিলেশনাল ডেটাবেজ সোর্স-অব-ট্রুথ ও এপিআই আর্কিটেকচার (SQLite Relational Source-of-Truth Architecture):
১. **SQLite হলো মূল সোর্স-অব-ট্রুথ (SQLite as Primary Source-of-Truth, Excel as Output/View):**
   - গবেষণার সমস্ত স্ট্রাকচার্ড ডেটা SQLite ডাটাবেজে সংরক্ষিত থাকে; Excel হলো কেবল একটি ভিউ/আউটপুট যা সরাসরি DB-এর ডেটা রিড করে স্বয়ংক্রিয়ভাবে জেনারেট হয়।
   - ডাটাবেজ অবস্থান:
     `/home/azureuser/IroScript_Projects/Ask-And-Research-Agent/ask_and_research.db`
২. **৫-স্তরীয় রিলেশনাল স্কিমা কাঠামো (5 Relational Tables):**
   - `research_runs`: মূল রান মেটাডেটা (`research_id` PK, `query`, `title`, `status`, `started_at`, `completed_at`, `metadata_json`)
   - `research_sources`: ব্যবহৃত গবেষণা সূত্র (`source_id` PK, `research_id` FK, `url`, `title`, `publisher`, `published_at`, `accessed_at`, `source_data`)
   - `research_findings`: প্রতিটি সুনির্দিষ্ট ফাইন্ডিংস ও প্রমাণ (`finding_id` PK, `research_id` FK, `claim`, `evidence`, `source_id` FK, `confidence`, `metadata_json`)
   - `research_elements`: গবেষণার কাঠামোগত সেকশন ও ট্যাব উপাদান (`element_id` PK, `research_id` FK, `element_type`, `content`, `metadata_json`)
   - `research_exports`: জেনারেট হওয়া এক্সেল ও মার্কডাউন ফাইলের রেজিস্ট্রি (`export_id` PK, `research_id` FK, `file_path`, `file_type`, `created_at`)
৩. **ব্যাকগ্রাউন্ড REST API সার্ভিস (Port 8095):**
   - সিস্টেমড সার্ভিস: `ask-research-api.service`
   - এন্ডপয়েন্টস:
     - `POST /api/research/run`: পূর্ণাঙ্গ রিলেশনাল রান, সোর্স, ফাইন্ডিংস, এলিমেন্টস ও এক্সপোর্টস একসাথে ট্রানজ্যাকশনালি সেভ।
     - `GET /api/research/runs/<research_id>`: সম্পূর্ণ গবেষণা বান্ডল রিকনস্ট্রাক্ট করা।
     - `GET /api/research/runs`: অতীত সকল গবেষণার তালিকা।
     - `POST /api/interactions` ও `GET /api/interactions`: আস্ক মোড ও সাধারণ ইন্টারেকশন ট্র্যাকিং।
     - `GET /api/stats` ও `GET /api/health`: লাইভ কাউন্ট ও সিস্টেম স্টেট পর্যবেক্ষণ।

### ৫. সর্বদা মোবাইল-বান্ধব ডাউনলোড লিংক নিশ্চিতকরণ (Mandatory Mobile-Friendly Download Links Mandate):
১. **বাধ্যতামূলক মোবাইল ডাউনলোড লিংক**: যখনই কোনো গবেষণা সম্পন্ন হবে, ফাইল তৈরি হবে বা ব্যবহারকারী ফাইলের বিষয়ে জানতে চাইবেন, এজেন্টের চূড়ান্ত টার্মিনাল রেসপন্স এবং হোয়াটসঅ্যাপ গ্রুপ ডেলিভারির মধ্যে অবশ্যই সক্রিয় ক্লাউডফ্লেয়ার টানেলের মাধ্যমে প্রস্তুতকৃত সরাসরি ১-ক্লিক মোবাইল ডাউনলোড লিংক (`https://.../api/raw?path=<filepath>&download=1`) প্রদান করতে হবে।
২. **সকল মূল ফাইলের ডাউনলোড ও প্রিভিউ লিংক**: প্রধান ৬-ট্যাব এক্সেল ডসিয়ার (`.xlsx`)-এর পাশাপাশি কোর ইংরেজি গবেষণা ডসিয়ার (`CORE_RESEARCH_EN.md`) এবং অনুবাদিত বাংলা গবেষণা প্রতিবেদন (`RESEARCH_REPORT_BN.md`)-এর সরাসরি ডাউনলোড লিংক এবং ইনলাইন প্রিভিউ লিংক দৃশ্যমান ও ক্লিকযোগ্যভাবে উপস্থাপন করতে হবে।
৩. **ইংরেজি ও বাংলা উভয় সংস্করণের পৃথক সরাসরি ডাউনলোড লিংক (Mandatory Both English & Bangla Download Links)**:
   - প্রতিটি গবেষণা আউটপুটে এবং হোয়াটসঅ্যাপ কার্ডে ইংরেজি এবং বাংলা উভয় ভাষার উপাদানের জন্য পৃথক ১-ক্লিক মোবাইল ডাউনলোড লিংক প্রদান বাধ্যতামূলক:
     - **ইংরেজি সংস্করণ (English Core Tier):** ৬-ট্যাব এক্সেল ডসিয়ার (`.xlsx`) এবং কোর গবেষণা ডসিয়ার (`CORE_RESEARCH_EN.md`) ডাউনলোড লিংক।
     - **বাংলা সংস্করণ (Bangla Final Deliverable Tier):** অনুবাদিত পূর্ণাঙ্গ বাংলা গবেষণা প্রতিবেদন (`RESEARCH_REPORT_BN.md`) ডাউনলোড লিংক এবং মোবাইল ব্রাউজারে ইনলাইন পড়ার অনলাইন প্রিভিউ লিংক।

---

## SECTION 8: 10-FOLD HARD-LOCKED AGENT PERPETUAL RESILIENCE ARCHITECTURE

### ১. প্রেক্ষাপট ও মূল উদ্দেশ্য (Context & Core Objective):
ওয়ার্কস্পেসের কোনো এজেন্ট (`agy:0`, `agy:yt`, `agy:frappe`, `agy:tg`, `agy:history`, `agy:kids`, `agy:rust`, `agy:article`, `agy:game`, `agy:research`, `agy:report`) যাতে কোনো অবস্থাতেই বন্ধ না হয়, ক্র্যাশ না করে বা র টার্মিনালে `-bash` প্রম্পটে ড্রপ করে নিষ্ক্রিয় অবস্থায় পড়ে না থাকে—তা নিশ্চিত করতে ১০টি হার্ড-লকড স্থাপত্যীয় নিরাপত্তা ব্যবস্থা (10 Hard-Locked Architectural Guard Systems) স্থায়ীভাবে বলবৎ করা হলো।

### ২. ১০টি হার্ড-লকড নিরাপত্তা ব্যবস্থা (The 10 Hard-Locked Systems):

| নং | সিস্টেমের নাম | প্রযুক্তি ও বাস্তবায়ন পথ | কার্যপ্রণালী ও সুরক্ষা বৈশিষ্ট্য |
| :--- | :--- | :--- | :--- |
| **১** | **ইনফিনিট রেসপন রানার র‍্যাপার** | `/home/azureuser/.webterminal/agent_runner_wrapper.sh` | প্রতিটি এজেন্টের জন্য অনন্ত লুপ (`while true; do agy ...; done`), ক্র্যাশ/সিগন্যালে অবিলম্বে ১ সেকেন্ডে স্বয়ংক্রিয় রিস্টার্ট, এবং রপিড ক্র্যাশ গার্ড (<৩ সেকেন্ডে ড্রপ হলে ৪ সেকেন্ড ব্যাকঅফ)। |
| **২** | **স্বয়ংক্রিয় প্রসেস গার্ডিয়ান ও ওয়াচডগ** | `/home/azureuser/.webterminal/agent_supervisor_watchdog.py` | প্রতি ১০ সেকেন্ড পর পর ১১টি এজেন্ট উইন্ডো ও সাব-প্রসেস অডিট; যদি কোনো এজেন্ট শেলে বা অচল অবস্থায় ড্রপ করে, অবিলম্বে টার্মিনালে র‍্যাপার ইনজেকশনের মাধ্যমে পুনরুজ্জীবন (<১০ সেকেন্ড রিকভারি)। |
| **৩** | **স্থায়ী সিস্টেমড ইউজার সার্ভিস** | `~/.config/systemd/user/agy-agent-watchdog.service` | ওএস ও সিস্টেমড ব্যাকগ্রাউন্ড ডেমন (`Restart=always`, `RestartSec=3s`); ভিএম রিবুট বা সেশন লগআউটেও লিঙ্গার মোডে নিরবচ্ছিন্নভাবে স্বচালিত। |
| **৪** | **স্ব-নিরাময়কারী মাস্টার সেশন ইনিশিয়ালাইজার** | `/home/azureuser/.webterminal/init_agy_sessions.sh` | উইন্ডো উপস্থিতি, ক্যানোনিকাল ডিরেক্টরি বাইন্ডিং (`cwd`), এবং উইন্ডো রিনেম লক (`allow-rename off`) নিশ্চিতকরণ। |
| **৫** | **ওয়ার্কস্পেস ফোল্ডার ট্রাস্ট প্রি-সিডিং** | `/home/azureuser/.gemini/antigravity-cli/settings.json` | ১১টি এজেন্টের সকল পাথ `trustedWorkspaces`-এ অগ্রিম নিবন্ধিত; স্টার্টআপে কোনো ট্রাস্ট কনফার্মেশন প্রম্পট আটকে থাকার সুযোগ নেই। |
| **৬** | **হোয়াটসঅ্যাপ ব্রিজ প্রি-ফ্লাইট ভেরিফিকেশন** | `/home/azureuser/.webterminal/whatsapp_bridge.js` | মেসেজ পাঠানোর পূর্বে এজেন্ট সক্রিয় আছে কিনা পরীক্ষা; শেলে ড্রপ থাকলে তাৎক্ষণিক রিস্টার্ট করে প্রম্পট বাফার ডেলিভারি নিশ্চিতকরণ। |
| **৭** | **স্টেট লক ও পাইপ স্যানিটাইজেশন প্রোটোকল** | ডিলিট গার্ড নিরাপদ গ্লোবাল আর্কাইভ প্রোটোকল | রিস্টার্টের পূর্বে ৬০ সেকেন্ডের পুরনো `.git/index.lock` ফাইল নিরাপদে `GLOBAL-ARCHIVE/stale_git_locks/`-এ স্থানান্তর (শূন্য `rm`), ড্যাঙ্গলিং ফাইল মুক্ত রাখা। |
| **৮** | **উচ্চ-নির্ভুল টেলিমেট্রি হার্টবিট ফাইল** | `/home/azureuser/.webterminal/agent_health_state.json` | প্রতি ১০ সেকেন্ডে পার-এজেন্ট পিআইডি, আরএসএস র‍্যাম মেমরি, আপটাইম, রিস্টার্ট কাউন্ট এবং লাইভ স্ট্যাটাস ধারণকারী স্থায়ী JSON ফাইল। |
| **৯** | **সেন্টিনেল রিপোর্টার ও লাইভ হোয়াটসঅ্যাপ অ্যালার্ট** | `/home/azureuser/.webterminal/Agy Whatsapp Agents/Reporting-Agent/sentinel_reporter.py` | সেন্টিনেল প্রতি ৩০ মিনিটে `agent_health_state.json` রিড করে ১১টি এজেন্টের লাইভ পিআইডি ও মেমরি হোয়াটসঅ্যাপে সম্প্রচার করে এবং ব্যর্থতায় অ্যালার্ট নথিভুক্ত করে। |
| **১০** | **মাস্টার গভর্নেন্স সেটিং ৭৮ ও রিমোট গিট লক** | `/home/azureuser/.gemini/AGENTS.md` ও গিট সিঙ্ক | একক নিয়ন্ত্রক নথিতে গভর্নেন্স লক, `unverified:` প্রিফিক্স সহ গিট কমিট এবং গিটহাব রিমোট `main` শাখায় এসএইচএ নিশ্চিতকরণ। |

### ৩. ১১টি এজেন্টের ক্যানোনিকাল বাইন্ডিং ও সার্বক্ষণিক পর্যবেক্ষণ ম্যাট্রিক্স:
1. `agy:0` (Master Agent) -> `/home/azureuser`
2. `agy:yt` (YouTube Pipeline) -> `/home/azureuser/IrakIroan/IroScript_Projects/Social Media/youtube`
3. `agy:frappe` (Frappe ERP) -> `/home/azureuser/Frappe-erp-Alco`
4. `agy:tg` (Telegram Bot) -> `/home/azureuser/IrakIroan/IroScript_Projects/Social Media/telegram-bot`
5. `agy:history` (Personal AI & History) -> `/home/azureuser/IrakIroan/IroScript_Projects/Personal Life/Digital History management/PERSONAL AI AGENT`
6. `agy:kids` (Kids Tube) -> `/home/azureuser/IrakIroan/IroScript_Projects/Personal Life/kids_tube_with_folder_seection`
7. `agy:rust` (Rust Task) -> `/home/azureuser/IrakIroan/IroScript_Projects/Personal Life/Rust_Task_With_Time_Keeping_And_Live_Note`
8. `agy:article` (Article Platform) -> `/home/azureuser/IrakIroan/IroScript_Projects/Publishing Websites/Article-Publishing-Platform`
9. `agy:game` (3D Game Studio) -> `/home/azureuser/IrakIroan/IroScript_Projects/Publishing Websites/3D-Game-Design-Studio`
10. `agy:research` (Ask & Research Agent) -> `/home/azureuser/IrakIroan/IroScript_Projects/Ask-And-Research-Agent`
11. `agy:report` (Reporting Agent) -> `/home/azureuser/.webterminal/Agy Whatsapp Agents/Reporting-Agent`









