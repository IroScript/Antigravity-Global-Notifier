import sys

text = """ইরাক ভাইয়া,

রুল ১০ (তথ্যের শতভাগ স্পষ্টতা)-এর আলোকে
সম্পূর্ণ সরাসরি এবং অকপটে বলছি:

«──────────────────────────────»
🛑 *Azure VM-এর ডিস্কে বর্তমান প্রকৃত সত্য*
«──────────────────────────────»
বাইরের লিংকের কথা বাদ দিলে, এই মুহূর্তে
*Azure VM-এর লোকাল ডিস্কে* প্রজেক্টগুলোর
কোড ফোল্ডারগুলো (Frappe, Telegram, Kids,
Rust, 3D Game, Article Publishing)
*লোকাল ড্রাইভ থেকে সত্যি মুছে গেছে।*

Azure VM-এর লোকাল পাথে সেগুলো আর বিদ্যমান নেই।

«──────────────────────────────»
📂 *Azure VM-এ বর্তমানে বাস্তবে কী কী আছে?*
«──────────────────────────────»
আপনার এই Azure সার্ভারে বর্তমানে কেবল নিচের
ফাইলগুলো শারীরিকভাবে বিদ্যমান আছে:

১. *ইউটিউব ডাটাবেজ (লোকাল রিস্টোরকৃত):*
   [`file:///home/azureuser/.openclaw/workspace/IROSCRIPT-CEO/social-media/youtube/Youtube%20Automation/PromptDatabase/database/youtube_pipeline.db`](file:///home/azureuser/.openclaw/workspace/IROSCRIPT-CEO/social-media/youtube/Youtube%20Automation/PromptDatabase/database/youtube_pipeline.db)
   (৩৮ মেগাবাইট লাইভ ডাটাবেজ + ৪.১ এমবি WAL)।

২. *টিএমপি ডিরেক্টরির ডাটাবেজ ডাম্পসমূহ (/tmp):*
   - `/tmp/final_staged_clean.sqlite` (২৪ এমবি)
   - `/tmp/restored_clean.sqlite` (২৪ এমবি)
   - `/tmp/fixed_dump.sql` (২০ এমবি)

৩. *হোয়াটসঅ্যাপ ব্রিজ ও কনফিগ:*
   [`file:///home/azureuser/.webterminal/whatsapp_bridge.js`](file:///home/azureuser/.webterminal/whatsapp_bridge.js)
   [`file:///home/azureuser/.webterminal/wa_auth`](file:///home/azureuser/.webterminal/wa_auth)
   [`file:///home/azureuser/.webterminal/init_agy_sessions.sh`](file:///home/azureuser/.webterminal/init_agy_sessions.sh)

৪. *আর্কিটেকচার ও পলিসি ফাইলসমূহ:*
   [`file:///home/azureuser/AGY-MASTER/AGENTS.md`](file:///home/azureuser/AGY-MASTER/AGENTS.md)
   [`file:///home/azureuser/AGY-MASTER/POLICIES/safety_levels.json`](file:///home/azureuser/AGY-MASTER/POLICIES/safety_levels.json)
   [`file:///home/azureuser/AGY-MASTER/PROJECT_REGISTRY.md`](file:///home/azureuser/AGY-MASTER/PROJECT_REGISTRY.md)

৫. *সিএলআই বাইনারি:*
   [`file:///home/azureuser/.local/bin/agy`](file:///home/azureuser/.local/bin/agy) (Version 1.2.8)

«──────────────────────────────»
🔧 *Azure ডিস্কে প্রজেক্ট ফিরিয়ে আনার উপায়*
«──────────────────────────────»
যেহেতু Azure VM-এর লোকাল ডিস্ক থেকে কোডগুলো
মুছে গেছে, কিন্তু আপনার গিটহাবে (`IroScript`)
সব কোড অক্ষত আছে, তাই:

*এই Azure সার্ভারে কোডগুলো ফিরিয়ে আনতে হলে*
*গিটহাব থেকে সরাসরি ক্লোন করতে হবে।*

যেমন:
১. `git clone https://github.com/IroScript/frappe-erp-alco-project.git /home/azureuser/Frappe-erp-Alco`
২. `git clone https://github.com/IroScript/telegram-scraper-and-automation.git /home/azureuser/telegram-bot`
৩. `git clone https://github.com/IroScript/kids_tube_with_folder_seection.git /home/azureuser/kids_tube_with_folder_seection`
৪. `git clone https://github.com/IroScript/Rust_Task_With_Time_Keeping_And_Live_Note.git /home/azureuser/Rust_Task_With_Time_Keeping_And_Live_Note`
৫. `git clone https://github.com/IroScript/3d-web-templates.git /home/azureuser/3D-Game-Design-Studio`
৬. `git clone https://github.com/IroScript/personal_ai_agent.git "/home/azureuser/.openclaw/workspace/IROSCRIPT-CEO/PERSONAL AI AGENT"`

«──────────────────────────────»
🎯 *আপনার সিদ্ধান্ত*
«──────────────────────────────»
আপনি অনুমতি দিলে আমি এক নিমিষেই এই Azure VM-এ
কমান্ডগুলো এক্সিকিউট করে প্রতিটি প্রজেক্টকে
তার নিজ নিজ লোকাল ডিরেক্টরিতে আবার ফিরিয়ে
আনতে পারি।

আমি কি ক্লোন করে লোকাল ডিস্কে রিস্টোর
করব ইরাক ভাইয়া?"""

lines = text.splitlines()
max_len = 0
for idx, line in enumerate(lines):
    if "file:///" in line or "https://" in line:
        continue
    if len(line) > 50:
        print(f"Line {idx+1} too long ({len(line)} chars): {line}")
    if len(line) > max_len:
        max_len = len(line)
print(f"Max non-URL line length: {max_len}")
