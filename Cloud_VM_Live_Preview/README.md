# 📌 Windows 11 Azure File Explorer & Live CPU/RAM Monitor — Complete Architecture & Operations Guideline

> **Repository:** [https://github.com/IroScript/Antigravity-Global-Notifier](https://github.com/IroScript/Antigravity-Global-Notifier)  
> **Target Directory:** `/home/azureuser/IroScript_Projects/Whatsapp_Agy_Agents/Antigravity-Global-Notifier/Cloud_VM_Live_Preview/`  
> **Active Public URL:** `https://individuals-practical-mile-bunny.trycloudflare.com`  
> **Internal Service Port:** `127.0.0.1:8088`

---

## ১. সার্বিক পরিচিতি ও ভেরিফিকেশন ফলাফল (Overview & Ground Truth)

### ক. সিস্টেম তথ্য ও মেমরি পরিমাপ (Hardware Truth)
পূর্ববর্তী কনফিগারেশনে ইন্টারফেস ও চার্টে ১৬ জিবি র‍্যাম প্রদর্শিত হচ্ছিল, যা একটি পুরাতন ভিএম কনফিগারেশন থেকে এসেছে। বর্তমান Azure VM-এর বাস্তবিক পরিমাপ নিচে দেওয়া হলো (উৎস: `/proc/meminfo` এবং `free -h`):
- **ফিজিক্যাল RAM (Physical RAM):** `7.76 GiB` (~8.0 GB)
  - `MemTotal`: ৮,১৩৩,৬৭৬ kB
  - স্বাভাবিক ব্যবহৃত: ~৪.১–৪.৩ GB (~৫৪–৫৫%)
  - উপলব্ধ মেমরি (Available): ~৩.৫–৩.৭ GB
- **ভার্চুয়াল প্রসেসর (vCPUs):** ৪টি কোর (`0.0% – 400.0%` স্কেল)
- **NVMe সোয়াপ (Swap Space):** `19.99 GiB` (~20.0 GB, `SwapTotal: 20971516 kB`)

### খ. প্রসেস ও CPU পরিমাপের যথার্থতা (Process & CPU Accuracy)
সিস্টেমের `/api/stats` এন্ডপয়েন্ট সরাসরি লিনাক্স কার্নেলের `ps -eo pid,user,%cpu,%mem,comm,args --sort=-%cpu` এবং `/proc/` থেকে প্রতি সেকেন্ডে লাইভ ডাটা গ্রহণ করে। প্রতিটি প্রসেসের PID, CPU লোড %, ব্যবহৃত RAM MB এবং সংশ্লিষ্ট AGY এজেন্টের নাম নির্ভুলভাবে ম্যাপ করা হয়।

---

## ২. ব্যাকএন্ডের প্রয়োজনীয় সাপোর্টিং কোড ও ফাইলসমূহ (Backend Supporting Components)

এই সম্পূর্ণ সমাধানটি চলার জন্য মোট ৮টি মূল ফাইল ও কম্পোনেন্ট কাজ করে:

```text
Cloud_VM_Live_Preview/
├── server.py                           # ১. মূল পাইথন HTTP ওয়েব সার্ভার (Port 8088)
├── start_tunnel.sh                     # ২. ক্লাউডফ্লেয়ার কুইক টানেল এক্সিকিউশন ও ইউআরএল পার্সার স্ক্রিপ্ট
├── azure-file-explorer.service         # ৩. ওয়েব সার্ভারের সিস্টেমড সার্ভিস ইউনিট
├── azure-file-explorer-tunnel.service  # ৪. টানেলের সিস্টেমড সার্ভিস ইউনিট
├── metrics_history.db                  # ৫. SQLite ডাটাবেস (টাইমলাইন ও হিস্ট্রি স্ন্যাপশট সংরক্ষক)
├── tunnel_url.txt                      # ৬. বর্তমান সক্রিয় ক্লাউডফ্লেয়ার লাইভ পাবলিক ইউআরএল
└── static/
    ├── index.html                      # ৭. উইন্ডোজ ১১ ফ্লুয়েন্ট UI (This PC ফাইল এক্সপ্লোরার + CPU মনিটর)
    ├── monitor.html                    # ৮. স্ট্যান্ডঅ্যালোন রিসোর্স ও প্রসেস মনিটর পেজ
    └── chart.min.js                    # ৯. অফলাইন Chart.js লাইব্রেরি (টাইমলাইন গ্রাফ রেন্ডারার)
```

---

## ৩. কম্পোনেন্টগুলোর বিস্তারিত কার্যপ্রণালী (Component Architecture)

### ১. `server.py` (Core Native HTTP Server)
- **কোনো এক্সটার্নাল ডিপেন্ডেন্সি নেই:** সম্পূর্ণ পাইথনের বিল্ট-ইন স্ট্যান্ডার্ড লাইব্রেরি (`ThreadingHTTPServer`, `BaseHTTPRequestHandler`, `sqlite3`, `subprocess`) দিয়ে চালিত।
- **মূল দায়িত্বসমূহ:**
  - **ফাইল এক্সপ্লোরার ব্যাকএন্ড:** `/api/browse` (ডিরেক্টরি ও ফাইলের তালিকা), `/api/drives` (ড্রাইভের স্পেস), `/api/content` (ইন-ব্রাউজার প্রিভিউ), `/api/raw` (ডাউনলোড), `/api/properties` (ফোল্ডার সাইজ গণনা)।
  - **রিসোর্স টেলিমেট্রি ইঞ্জিন:** `get_fallback_stats()` সরাসরি `ps` ও `/proc/meminfo` পড়ে প্রসেস ও মেমরি সংগ্রহ করে।
  - **এজেন্ট আইডেন্টিটি রেজোলিউশন:** `resolve_agent_identity(pid, cmd)` প্রতিটি প্রসেসের `tty`, `cwd` ও কমান্ড দেখে সেটিকে নির্দিষ্ট ভূমিকায় শনাক্ত করে (যেমন: `🧠 agy:0`, `💼 agy:frappe`, `💬 WhatsApp Bridge`, `🤖 agy:tg`, `🔍 agy:ask`, `🎬 agy:yt` ইত্যাদি)।
  - **মেট্রিক্স হিস্ট্রি ইঞ্জিন:** প্রতি ৩০ সেকেন্ডে SQLite ডাটাবেসে (`metrics_history.db`) স্ন্যাপশট সংরক্ষণ করে এবং `/api/history?range=...` এন্ডপয়েন্টে ১মি, ৫মি, ১৫মি, ৩০মি, ১ঘ, ৫ঘ, ১০ঘ, ২৪ঘ ও All হিস্ট্রি রিটার্ন করে।

### ২. `start_tunnel.sh` (Cloudflare Tunnel Runner)
- `/usr/bin/cloudflared tunnel --url http://127.0.0.1:8088` রান করে।
- লাইভ আউটপুট থেকে `https://*.trycloudflare.com` ফিল্টার করে লোকাল ফাইলসমূহে লিখে রাখে:
  - `tunnel_url.txt`
  - `/home/azureuser/windows_explorer_url.txt`
  - `/home/azureuser/.webterminal/windows_explorer_url.txt`

### ৩. `azure-file-explorer.service` (Systemd Service)
- অবস্থান: `/etc/systemd/system/azure-file-explorer.service`
- ব্যবহারকারী: `User=azureuser`
- রিস্টার্ট পলিসি: `Restart=always`, `RestartSec=3`
- সার্ভার ক্র্যাশ করলে বা টার্মিনেট হলে সিস্টেমড স্বয়ংক্রিয়ভাবে ৩ সেকেন্ডে পুনরায় চালু করে।

### ৪. `azure-file-explorer-tunnel.service` (Systemd Tunnel Service)
- অবস্থান: `/etc/systemd/system/azure-file-explorer-tunnel.service`
- ব্যাকগ্রাউন্ডে সবসময় টানেল কানেকশন সক্রিয় রাখে।

---

## ৪. প্রয়োজনীয় ব্যাকএন্ড কমান্ড ও অপারেশনাল রানবুক (Essential Commands)

### ক. সার্ভিস স্ট্যাটাস ও পর্যবেক্ষণ
```bash
# সার্ভিস দুটির বর্তমান অবস্থা যাচাই
systemctl status azure-file-explorer.service azure-file-explorer-tunnel.service

# বর্তমান পাবলিক লাইভ ইউআরএল দেখা
cat /home/azureuser/windows_explorer_url.txt

# লোকাল সকেট বাইন্ডিং পরীক্ষা (৮০৮৮ পোর্ট)
ss -tulpn | grep 8088
```

### খ. কোড পরিবর্তনের পর নিরাপদ রিস্টার্ট (Non-Root Soft Restart)
যেহেতু সার্ভিসটি `azureuser` এর অধীনে চলে এবং `Restart=always` কনফিগার করা, সুডো (`sudo`) ছাড়াই সাধারণ প্রসেস রিলোড করা যায়:
```bash
# পাইথন ওয়েব সার্ভার রিস্টার্ট (সিস্টেমড ৩ সেকেন্ডে নিজে রিলোড করবে)
pkill -f "Cloud_VM_Live_Preview/server.py"

# ক্লাউডফ্লেয়ার টানেল রিস্টার্ট
pkill -f "cloudflared tunnel --url http://127.0.0.1:8088"
```

### গ. লাইভ এন্ডপয়েন্ট ও হেলথ চেক কমান্ড
```bash
# লোকাল ওয়েব রেসপন্স ও হেডার চেক
curl -I http://127.0.0.1:8088/

# রিয়েল-টাইম CPU, ৮ জিবি RAM এবং টপ প্রসেস ডাটা দেখা
curl -s http://127.0.0.1:8088/api/stats | python3 -m json.tool | head -n 35

# টাইমলাইন হিস্ট্রি এন্ডপয়েন্ট চেক (গত ১৫ মিনিটের ডাটা)
curl -s "http://127.0.0.1:8088/api/history?range=15m" | python3 -m json.tool | head -n 25

# পাবলিক ক্লাউডফ্লেয়ার টানেল সংযোগ ভেরিফিকেশন
curl -I -s $(cat /home/azureuser/windows_explorer_url.txt)
```

### ঘ. কার্নেল ও প্রসেস ডাইরেক্ট অডিট কমান্ড
```bash
# টপ ২০ প্রসেস সরাসরি CPU ও মেমরি অনুযায়ী
ps -eo pid,user,%cpu,%mem,comm,args --sort=-%cpu | head -n 20

# মেমরি ও সোয়াপের গ্রাউন্ড ট্রুথ
free -h
cat /proc/meminfo | grep -E 'MemTotal|MemAvailable|SwapTotal|SwapFree'
```

---

## ৫. এপিআই এন্ডপয়েন্ট তালিকা (REST API Reference)

| এন্ডপয়েন্ট (Endpoint) | মেথড | বিবরণ |
| :--- | :--- | :--- |
| `/` বা `/index.html` | `GET` | ইউনিফাইড Windows 11 This PC ফাইল এক্সপ্লোরার ও রিসোর্স মনিটর |
| `/monitor` | `GET` | স্ট্যান্ডঅ্যালোন রিসোর্স, অ্যাপ রোলআপ ও প্রসেস অডিট ভিউ |
| `/api/stats` | `GET` | বর্তমান সার্বিক CPU %, ৪-কোর লোড, ৮ জিবি RAM, সোয়াপ, ২৬+ অ্যাপ রোলআপ ও ৪৪+ প্রসেস তালিকা |
| `/api/history?range=...` | `GET` | টাইম-সিরিজ হিস্ট্রি ডাটা (`1m`, `5m`, `15m`, `30m`, `1h`, `5h`, `10h`, `24h`, `all`) |
| `/api/browse?path=...` | `GET` | যেকোনো ডিরেক্টরির ফাইল ও ফোল্ডার তালিকা (নাম, সাইজ, মডিফিকেশন টাইম, পারমিশন) |
| `/api/drives` | `GET` | This PC ভিউর জন্য রুট (`/`), প্রজেক্ট ড্রাইভ ও ব্যাকআপ ড্রাইভের স্পেস |
| `/api/content?path=...` | `GET` | টেক্সট ফাইল, স্ক্রিপ্ট বা কনফিগারেশন ইন-ব্রাউজার প্রিভিউ |
| `/api/raw?path=...` | `GET` | ফাইল ব্রাউজার থেকে সরাসরি ফাইল ডাউনলোড বা মিডিয়া স্ট্রিমিং |
| `/api/properties?path=...`| `GET` | নির্দিষ্ট ফোল্ডারের ফাইল সংখ্যা, সাব-ফোল্ডার সংখ্যা ও মোট সাইজ গণনা |
| `/api/search?path=...&q=...`| `GET` | ডিরেক্টরির ভিতরে রিয়েল-টাইম ফাইল ও ফোল্ডার সার্চ |

---

## ৬. ট্রাবলশুটিং রানবুক (Troubleshooting)

1. **ব্রাউজারে কোনো প্রসেস বা অ্যাপ রোলআপ দেখা না গেলে:**
   - নিশ্চিত করুন `server.py` এর `get_fallback_stats()` ফাংশনে `ps` এক্সিকিউশন সক্রিয় আছে।
   - রান করুন: `curl -s http://127.0.0.1:8088/api/stats | grep top_procs`
2. **র‍্যামের গ্রাফ ৮ জিবির উপরে চলে গেলে:**
   - `metrics_history.db` তে কোনো পুরাতন ১৬ জিবি টেস্ট ডাটা রয়েছে কি না যাচাই করুন।
   - রান করুন: `python3 -c "import sqlite3; c=sqlite3.connect('metrics_history.db'); print(c.execute('SELECT max(ram_gb) FROM metrics').fetchone())"`
3. **পাবলিক ইউআরএল কাজ না করলে বা টানেল ড্রপ করলে:**
   - টানেল লগ পরীক্ষা করুন: `tail -n 25 /home/azureuser/IroScript_Projects/Whatsapp_Agy_Agents/Antigravity-Global-Notifier/Cloud_VM_Live_Preview/tunnel.log`
   - নতুন ইউআরএল পেতে টানেল রিস্টার্ট করুন: `pkill -f cloudflared`
