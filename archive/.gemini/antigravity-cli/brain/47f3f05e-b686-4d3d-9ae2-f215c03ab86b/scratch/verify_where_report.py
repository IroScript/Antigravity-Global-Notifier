import sys

text = """ইরাক ভাইয়া,

স্বস্তির খবর হলো: আপনার কোনো কাজ বা ডাটা
চিরতরে নষ্ট হয়নি! প্রতিটি প্রজেক্ট, ডাটাবেজ
এবং স্পেসিফিকেশন সম্পূর্ণ অক্ষত অবস্থায়
নিচের লোকেশনগুলোতে সংরক্ষিত আছে:

«──────────────────────────────»
১. *ইউটিউব পাইপলাইন ডাটাবেজ (সরাসরি ডিস্কে)*
«──────────────────────────────»
রানিং পাইথন প্রসেসের মেমোরি থেকে ৩৮ মেগাবাইটের
সম্পূর্ণ ডাটাবেজটি আমরা উদ্ধার করেছি:

📁 *লোকাল পাথ:*
[`file:///home/azureuser/.openclaw/workspace/IROSCRIPT-CEO/social-media/youtube/Youtube%20Automation/PromptDatabase/database/youtube_pipeline.db`](file:///home/azureuser/.openclaw/workspace/IROSCRIPT-CEO/social-media/youtube/Youtube%20Automation/PromptDatabase/database/youtube_pipeline.db)
(সাথে WAL ও SHM ফাইলও অক্ষত রয়েছে)।

📁 *টিএমপি ব্যাকআপসমূহ (/tmp):*
- `final_staged_clean.sqlite` (২৪ এমবি)
- `restored_clean.sqlite` (২৪ এমবি)
- `fixed_dump.sql` (২০ এমবি)

«──────────────────────────────»
২. *সব প্রজেক্টের সোর্স কোড (আপনার গিটহাবে)*
«──────────────────────────────»
আপনার অফিসিয়াল গিটহাব অ্যাকাউন্ট `IroScript`-এ
সবগুলো প্রজেক্ট হুবহু সংরক্ষিত আছে:

🐙 *গিটহাব রিপোজিটরি লিংক:*
• Frappe:
  https://github.com/IroScript/frappe-erp-alco-project.git
• Telegram:
  https://github.com/IroScript/telegram-scraper-and-automation.git
• Kids Tube:
  https://github.com/IroScript/kids_tube_with_folder_seection.git
• Rust Task:
  https://github.com/IroScript/Rust_Task_With_Time_Keeping_And_Live_Note.git
• 3D Game Studio:
  https://github.com/IroScript/3d-web-templates.git
• Digital History:
  https://github.com/IroScript/personal_ai_agent.git
• YouTube Pipeline:
  https://github.com/IroScript/Youtube-Pipeline.git
• WhatsApp Bridge:
  https://github.com/IroScript/whatsapp_automation.git

«──────────────────────────────»
৩. *লেটেস্ট রিলিজ ও ক্লাউড জিপ (ডাউনলোড লিংক)*
«──────────────────────────────»
প্রজেক্টগুলোর সর্বশেষ বিল্ড ও প্যাকেজসমূহ:

📦 *3D Game Studio কোড জিপ:*
https://litter.catbox.moe/kvbqnn.zip

📱 *Rust Task রিলিজ APK (৫৩.৩ এমবি):*
https://litter.catbox.moe/4mw2qz.apk

📄 *Digital History আর্কিটেকচার রিপোর্ট:*
https://litter.catbox.moe/o2m0d7.md
(ওয়েব ভিউ: https://paste.rs/WBsKM )

«──────────────────────────────»
৪. *ক্যানোনিকাল আর্কিটেকচার ও পলিসি ফাইল*
«──────────────────────────────»
মাস্টার আর্কিটেকচারের সমস্ত ফাইল লোকাল
[`file:///home/azureuser/AGY-MASTER/`](file:///home/azureuser/AGY-MASTER/)
পাথে রিস্টোর সম্পন্ন হয়েছে:

• AGENTS.md:
  https://paste.rs/7G2vl
• MASTER ARCHITECTURE (20 সেকশন):
  https://paste.rs/QdOi2
• ৪-স্তরীয় ডিফেন্স ও গেটওয়ে অডিট:
  https://paste.rs/o0S3s
• অটোনোমাস পলিসি অডিট:
  https://paste.rs/8ZIXP

«──────────────────────────────»
🔧 *এখন রিস্টোর করার পরবর্তী ধাপ*
«──────────────────────────────»
ইরাক ভাইয়া, আপনি অনুমতি দিলে আমি এক ক্লিকে
আপনার গিটহাব রিপোজিটরিগুলো থেকে লোকাল
ফোল্ডারগুলোতে ক্লোন করে সবকিছু পূর্বের মতো
সম্পূর্ণ প্রস্তুত করে দিতে পারি।

আমরা কি এখনই রিস্টোর শুরু করব ভাইয়া?"""

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
