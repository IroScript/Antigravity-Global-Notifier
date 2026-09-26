import sys

text = """ইরাক ভাইয়া,

আপনি সিস্টেমের সবচেয়ে মৌলিক সত্য এবং অফিসিয়াল
পারমিশন মেকানিজমটি নিখুঁতভাবে চিহ্নিত করেছেন!

«──────────────────────────────»
💎 *অফিসিয়াল প্রি-সিডেন্স ও বাস্তবায়নের ভিত্তি*
«──────────────────────────────»
আপনার উল্লেখ করা পয়েন্টটিই এই পুরো সিস্টেমের
ভিত্তিমূল:
Antigravity-এর অফিশিয়াল আর্কিটেকচারে:
`deny > ask > allow`
প্রিসিডেন্স কার্যকর থাকে এবং হুকের এক্সিট কোড
নন-জিরো বা টাইমআউট হলে সিস্টেম সরাসরি
Fail-Closed আচরণ করে।

যেহেতু আমরা headless / WhatsApp মোডে কাজ করছি,
তাই আমাদের পলিসিতে কোনো `ask` বা ইন্টারঅ্যাক্টিভ
প্রম্পটের অবকাশ নেই। আমাদের গেটওয়ে হবে একটি
লৌহকঠিন বাইনারি সিদ্ধান্ত ইঞ্জিন:
সরাসরি *ALLOW* অথবা কঠোর *DENY*!

«──────────────────────────────»
🛡️ *রানটাইম স্টেট ও রিকভারি আপডেট*
«──────────────────────────────»
রুল ১০ (তথ্যের শতভাগ সততা)-এর আলোকে রানটাইমের
বাস্তব অবস্থা জানাচ্ছি:

১. *ব্যাকগ্রাউন্ড টাস্ক নিষ্পত্তি:*
   পূর্বে ডাবল কোটের ভেতরে ব্যাকটিক কমান্ডের
   কারণে সৃষ্ট ব্যাকগ্রাউন্ড `task-5034` সম্পূর্ণ
   কিল করা হয়েছে।

২. *হুক এনভায়রনমেন্ট সচল:*
   [`file:///home/azureuser/.gemini/config`](file:///home/azureuser/.gemini/config)
   ডিরেক্টরিটি রিক্রিয়েট করায় সিএলআই তাৎক্ষণিক
   আনব্লক হয়েছে এবং সব টুল কল স্বাভাবিকভাবে কাজ
   করছে (যা প্রমাণ করে ডিরেক্টরি মিসিং হলেও CLI
   টুল রান হতে দেয় না—অর্থাৎ Fail-Closed)।

৩. *ক্যানোনিকাল ফাইল অক্ষত:*
   [`file:///home/azureuser/AGY-MASTER/AGENTS.md`](file:///home/azureuser/AGY-MASTER/AGENTS.md)
   [`file:///home/azureuser/MASTER_MULTI_AGENT_HIERARCHICAL_ARCHITECTURE.txt`](file:///home/azureuser/MASTER_MULTI_AGENT_HIERARCHICAL_ARCHITECTURE.txt)
   [`file:///home/azureuser/AGY-MASTER/POLICIES/safety_levels.json`](file:///home/azureuser/AGY-MASTER/POLICIES/safety_levels.json)
   [`file:///home/azureuser/AGY-MASTER/PROJECT_REGISTRY.md`](file:///home/azureuser/AGY-MASTER/PROJECT_REGISTRY.md)
   সবগুলো ফাইল ক্লাউড ব্যাকআপ থেকে অক্ষতভাবে
   পুনরুদ্ধার ও সিঙ্ক করা হয়েছে।

৪. *সিএলআই বাইনারি সচল:*
   [`file:///home/azureuser/.local/bin/agy`](file:///home/azureuser/.local/bin/agy)
   বাইনারি সচল রয়েছে (Version 1.2.8)।

«──────────────────────────────»
📋 *Phased & Test-Driven ব্লুপ্রিন্ট*
«──────────────────────────────»
আপনার নির্দেশ অনুযায়ী কোনো প্রোডাকশন মডিফিকেশন
না করে আমরা নিচের ক্রমানুসারে এগোব:

🔹 *Phase B (তাৎক্ষণিক পরবর্তী ধাপ):*
   *Offline Standalone Gateway & Test Suite*
   - [`file:///home/azureuser/AGY-MASTER/POLICIES/policy_gateway.py`](file:///home/azureuser/AGY-MASTER/POLICIES/policy_gateway.py)
     স্ক্রিপ্ট তৈরি করা হবে।
   - একটি স্বয়ংসম্পূর্ণ অফলাইন টেস্ট স্যুট
     (`test_policy_gateway.py`) দিয়ে লেভেল ০, ১,
     ২A, ২B, ৩, পাথ ট্রাভার্সাল, অবৈধ JSON,
     এবং রুট/সুডো ব্লক ১০০% টেস্ট করা হবে।
   - হুক ফাইলে যুক্ত করার আগে শতভাগ টেস্ট পাস
     নিশ্চিত করা হবে।

🔹 *Phase C: PreToolUse হুক সংযোগ*
   অফলাইন টেস্টে ১০০% উত্তীর্ণ হওয়ার পর
   [`file:///home/azureuser/.gemini/config/hooks.json`](file:///home/azureuser/.gemini/config/hooks.json)
   ফাইলে গেটওয়ে এনরোল করা হবে।

🔹 *Phase D: লাইভ নন-ডেস্ট্রাক্টিভ ভেরিফিকেশন*
   সিএলআই-এর ভেতর টেস্ট টুল কল দিয়ে লাইভ
   ইন্টারসেপশন এবং ডিনাই মেকানিজম পরীক্ষা করা।

🔹 *Phase E: ওএস-লেভেল ডিফেন্স-ইন-ডেপথ*
   ওয়ার্কার এজেন্টদের জন্য সুডো ও ডকার
   প্রিভিলেজ সীমাবদ্ধকরণ।

🔹 *Phase F: প্রজেক্ট রুল লোকালইজেশন*
   মূল AGENTS.md-এর ৭৭ কেবি ডুপ্লিকেট না করে
   প্রজেক্ট অনুযায়ী প্রয়োজনীয় সংক্ষিপ্ত ডোমেন
   নির্দেশনা ইনজেক্ট করা (জিরো টোকেন ব্লোট)।

🔹 *Phase G: কনকারেন্সি ও ৩-টায়ার ভেরিফিকেশন*
   অ্যাকশন এজেন্টের রিপেয়ারের পর রিপোর্টিং
   এজেন্টের নিরপেক্ষ হেলথ চেক এবং মাস্টারের
   চূড়ান্ত অ্যাকসেপ্টেন্স পাইপলাইন।

«──────────────────────────────»
🎯 *আপনার অনুমতি ও পরবর্তী নির্দেশ*
«──────────────────────────────»
আমরা কি এখন *Phase B*-এর অধীন অফলাইন
`policy_gateway.py` এবং এর স্বয়ংসম্পূর্ণ টেস্ট
স্যুট তৈরি করে অফলাইন টেস্ট সম্পন্ন করব
ইরাক ভাইয়া?
"""

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
