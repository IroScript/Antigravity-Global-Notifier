import sys

text = """ইরাক ভাইয়া,

রুল ১০ (তথ্যের শতভাগ সততা ও নির্ভুলতা)-এর
আলোকে কোনো লুকোচুরি না করে কী ঘটেছে এবং
বাস্তবে কী কী ডিলিট হয়েছিল, তার সম্পূর্ণ
ফরেনসিক অডিট রিপোর্ট নিচে তুলে ধরছি:

«──────────────────────────────»
⚠️ *কীভাবে ডিলিটটি ঘটেছিল (Mechanism)*
«──────────────────────────────»
টাস্ক `task-5034`-এ রেসপন্সের লাইন দৈর্ঘ্য
যাচাই করার জন্য একটি `python3 -c` কমান্ড
রান করা হয়েছিল।
কমান্ডটি ব্যাশের ডাবল কোট (`"..."`)-এ থাকায়
টেক্সটের ভেতরে ব্যাকটিকে থাকা `find -delete`
শব্দটিকে ব্যাশ কমান্ড সাবস্টিটিউশন হিসেবে গ্রহণ
করে ফেলে এবং `/home/azureuser` পাথে
`find . -delete` কার্যকর হয়ে যায়।

যেহেতু `azureuser`-এর নিজস্ব ফাইলগুলোর ওপর
ডিলিট পারমিশন ছিল, তাই এটি পোস্ট-অর্ডারে
ফাইল ও খালি ডিরেক্টরি মুছে ফেলে।

«──────────────────────────────»
🛑 *বাস্তবে যা যা ডিলিট হয়েছিল*
«──────────────────────────────»
১. *রুট কনফিগ ও লগ:*
   - [`file:///home/azureuser/.gemini/config/`](file:///home/azureuser/.gemini/config/) (hooks.json)
   - `settings.json` ও সিএলআই লগসমূহ
   - `~/.bash_history`
   - রুটের পুরোনো ৭৭ কেবির `AGENTS.md`

২. *আর্কিটেকচার ডিরেক্টরি:*
   - `/home/azureuser/AGY-MASTER/`
   - মূল আর্কিটেকচার টেক্সট ফাইল

৩. *প্রজেক্ট ওয়ার্কস্পেসসমূহ:*
   - `Frappe-erp-Alco`
   - `telegram-bot`
   - `kids_tube_with_folder_seection`
   - `Rust_Task_With_Time_Keeping_And_Live_Note`
   - `Article-Publishing-Platform`
   - `3D-Game-Design-Studio`
   - `Ask-And-Research`
   - `.webterminal`
   - `.openclaw/`-এর ভেতরের কিছু স্ক্রিপ্ট

«──────────────────────────────»
🛡️ *যা যা সম্পূর্ণ অক্ষত রয়েছে*
«──────────────────────────────»
১. *বর্তমান ব্রেইন ও ট্রান্সক্রিপ্ট:*
   [`file:///home/azureuser/.gemini/antigravity-cli/brain/47f3f05e-b686-4d3d-9ae2-f215c03ab86b/`](file:///home/azureuser/.gemini/antigravity-cli/brain/47f3f05e-b686-4d3d-9ae2-f215c03ab86b/)
   আমাদের বর্তমান সেশনের সমস্ত হিস্ট্রি, লগ
   ও টুল মেমোরি সম্পূর্ণ অক্ষত।

২. *রুট/ডকার সুরক্ষিত ফাইল:*
   `.openclaw`-এর ভেতরের ডকার প্রোফাইল
   ও রুট-ওউনড ফাইলগুলো পারমিশন ডিনাইড
   হওয়ায় ডিলিট হতে পারেনি।

৩. *টিএমপিতে রক্ষিত বিশাল ডাটাবেজ:*
   `/tmp/`-এ থাকা সমস্ত ডাম্প অক্ষত রয়েছে:
   - `final_staged_clean.sqlite` (২৪ এমবি)
   - `restored_clean.sqlite` (২৪ এমবি)
   - `fixed_dump.sql` (২০ এমবি)
   - `test_copy.db` (২৪ এমবি)
   - `test_reindex.db` (২৪ এমবি)

৪. *মেমোরিতে চলমান প্রসেসসমূহ:*
   টিমাক্সের ১১টি উইন্ডো ও রানিং প্রসেস
   মেমোরিতে সচল ছিল।

৫. *ক্লাউড ও গিটহাব ব্যাকআপ:*
   - ৩D গেম কোড জিপ:
     https://litter.catbox.moe/kvbqnn.zip
   - রাস্ট টাস্ক রিলিজ এপিকে:
     https://litter.catbox.moe/4mw2qz.apk
   - ডিজিটাল হিস্ট্রি রিপোর্ট:
     https://litter.catbox.moe/o2m0d7.md

«──────────────────────────────»
🔧 *যা যা ইতোমধ্যে পুনরুদ্ধার সম্পন্ন*
«──────────────────────────────»
আমরা তাৎক্ষণিকভাবে নিচের রিকভারি করেছি:

✅ *১. ক্ষতিকর টাস্ক কিল:* `task-5034` টার্মিনেট।
✅ *২. হুক ডিরেক্টরি রিক্রিয়েট:* সিএলআই আনব্লক।
✅ *৩. agy বাইনারি রিকভারি:* মেমোরি থেকে
   [`file:///home/azureuser/.local/bin/agy`](file:///home/azureuser/.local/bin/agy)
   (Version 1.2.8) সফলভাবে পুনরুদ্ধার।
✅ *৪. ক্যানোনিকাল আর্কিটেকচার ফাইল:*
   ক্লাউড (`paste.rs`) থেকে সব ফাইল রিস্টোর:
   - [`file:///home/azureuser/AGY-MASTER/AGENTS.md`](file:///home/azureuser/AGY-MASTER/AGENTS.md)
   - [`file:///home/azureuser/MASTER_MULTI_AGENT_HIERARCHICAL_ARCHITECTURE.txt`](file:///home/azureuser/MASTER_MULTI_AGENT_HIERARCHICAL_ARCHITECTURE.txt)
   - [`file:///home/azureuser/AGY-MASTER/POLICIES/safety_levels.json`](file:///home/azureuser/AGY-MASTER/POLICIES/safety_levels.json)
   - [`file:///home/azureuser/AGY-MASTER/PROJECT_REGISTRY.md`](file:///home/azureuser/AGY-MASTER/PROJECT_REGISTRY.md)
   - [`file:///home/azureuser/AGY-MASTER/REPORTS/`](file:///home/azureuser/AGY-MASTER/REPORTS/)
✅ *৫. ইউটিউব পাইপলাইন ডাটাবেজ:*
   রানিং পাইথন প্রসেসের ওপেন ফাইল ডেসক্রিপ্টর
   থেকে ৩৮ মেগাবাইটের সম্পূর্ণ ডাটাবেজ
   `youtube_pipeline.db` ও WAL রিস্টোর সম্পন্ন!

«──────────────────────────────»
📋 *পরবর্তী পদক্ষেপ ও প্রজেক্ট রিকভারি*
«──────────────────────────────»
বাকি প্রজেক্টগুলো গিটহাব রিমোট এবং ক্যাটবক্স
ব্যাকআপ জিপ থেকে সরাসরি রিস্টোর করা সম্ভব।

আপনার নির্দেশ পেলেই আমরা সেগুলো সিঙ্ক ও
রিস্টোর সম্পন্ন করব ইরাক ভাইয়া!"""

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
