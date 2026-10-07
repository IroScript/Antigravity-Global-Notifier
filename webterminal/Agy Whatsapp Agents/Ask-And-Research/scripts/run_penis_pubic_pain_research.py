#!/usr/bin/env python3
"""
Custom Medical Research Dossier Generator for Penile Swelling & Pubic Region Pain
Based on patient clinical query file: Penis_Pubic_area_Pain.txt
Workspace: /home/azureuser/IrakIroan/IroScript_Projects/Ask-And-Research-Agent
"""

import os
import sys
import json
from datetime import datetime, timezone

# Ensure project base directory is in sys.path
BASE_DIR = "/home/azureuser/IrakIroan/IroScript_Projects/Ask-And-Research-Agent"
sys.path.insert(0, os.path.join(BASE_DIR, "scripts"))

from research_engine import (
    slugify,
    generate_excel_dossier,
    record_registry,
    dispatch_to_whatsapp,
    TOPICS_DIR,
    WA_OUTBOX_DIR
)

def run():
    topic = "Penile Swelling and Pubic Area Pain Etiology & Diagnostic Strategy"
    category = "Clinical Urological Medicine & Infectious Disease Differential"
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    slug = slugify(topic)
    subfolder_name = f"{date_str}_{slug}"
    topic_dir = os.path.join(TOPICS_DIR, subfolder_name)
    os.makedirs(topic_dir, exist_ok=True)
    
    print(f"[*] Provisioning isolated topic subfolder: {topic_dir}")
    
    # ── 1. CUSTOM 6-TAB DATA STRUCTURE ──
    dossier_data = {
        "topic": topic,
        "category": category,
        
        # Tab 1: Executive Summary
        "summary_rows": [
            ("Core Research Problem", "Etiological & diagnostic differentiation of 4-day pubic pain, penile skin swelling, and chronic discharge history.", "Empirical Clinical Review", "Immediate Clinical Urgency"),
            ("Fungal vs Bacterial Etiology", "Candida balanitis explains localized glans/foreskin inflammation, but deep pubic pain points to urethritis, prostatitis, or pelvic musculoskeletal disorders.", "High Empirical Grounding", "Differential Pivot"),
            ("Blood Test & Ultrasound Reliability", "Normal CBC/CRP and normal ultrasound do NOT rule out localized acute/chronic prostatitis or urethral infection. TRUS role is ruling out prostatic abscess.", "Authoritative (EAU/AUA)", "Diagnostic Prudence"),
            ("Empiric Antibiotics vs 2-Day Wait", "In clinically stable patients without red flags, obtaining pre-antibiotic urine culture & NAAT prior to treatment protects antimicrobial stewardship.", "Guideline-Backed (NICE/CDC)", "Decision Strategy"),
            ("Gonococcal Latency Reality", "Neisseria gonorrhoeae does NOT cause lifelong dormant/latent infections from infancy into adulthood. Neonatal transmission manifests acutely within 2-5 days.", "Microbiological Certainty", "Pathogen Elimination"),
            ("Red-Flag Emergency Triggers", "Presence of acute urinary retention, fever/rigors (urosepsis), severe unilateral testicular pain, or tissue necrosis mandates immediate hospital assessment.", "Emergency Protocol", "Safety Gating")
        ],
        
        # Tab 2: Theoretical & Pathophysiological Foundations
        "theory_rows": [
            ("Candida Balanitis / Balanoposthitis", "Superficial fungal proliferation over glans and prepuce; triggered by moisture, diabetes, or antibiotic disruption of normal flora.", "Microscopic pseudohyphae / budding yeast", "Empirically Verified", "Explains skin soreness/swelling; does not account for deep pubic bone pain."),
            ("Acute Bacterial Prostatitis (ABP)", "Ascending bacterial infection causing acute glandular edema, stromal infiltration, and referred pelvic/suprapubic pain.", "Urine colony count >= 10^5 CFU/mL; pyuria", "Gold Standard Clinical Entity", "Presents with deep pubic/perineal pain, dysuria, and split stream; ultrasound often appears normal."),
            ("Infectious Urethritis (Gonococcal / NGU)", "Mucosal epithelial infection of the urethra by N. gonorrhoeae, C. trachomatis, or M. genitalium causing exudate and dysuria.", "Positive First-Catch Urine NAAT / PCR", "Molecular Gold Standard", "Can be subclinical or mild; does not require testicular involvement to be present."),
            ("Osteitis Pubis & Musculoskeletal Pubalgia", "Non-infectious chronic inflammatory arthropathy of pubic symphysis and surrounding adductor tendon insertions.", "Pubic symphysis tenderness, MRI edema", "Peer-Reviewed Orthopedic Entity", "Common non-infectious mimic of pubic pain; aggravated by pelvic movement/exercise."),
            ("Post-Antibiotic Pruritus & Drug Reaction", "Type I/IV hypersensitivity reaction vs secondary fungal overgrowth following broad-spectrum beta-lactamase inhibitor therapy.", "IgE mast cell degranulation / Candida overgrowth", "Pharmacologically Documented", "Axclav-induced itching requires differentiating allergy from early fungal bloom.")
        ],
        
        # Tab 3: Diagnostic Modalities & Workflow Architecture
        "arch_rows": [
            ("First-Catch Urine NAAT / PCR", "Initial 10-20 mL of voided urine without prior cleansing; tests for N. gonorrhoeae and C. trachomatis DNA/RNA.", "Molecular Amplification Protocol", "Standard PCR thermal cyclers", "Highest sensitivity (>95%) for urethritis screening."),
            ("Midstream Clean-Catch Urine Culture", "Midstream urine aliquot cultured on blood and MacConkey agar; determines bacterial colony count and AST profile.", "Quantitative Colony Count (>10^4-10^5 CFU/mL)", "Standard Clinical Microbiological Media", "Required prior to starting antibiotics for suspected bacterial prostatitis."),
            ("Routine Urinalysis (Urine R/E)", "Dipstick screening for leukocyte esterase, nitrites, protein, and microscopic sediment evaluation for pus cells.", "Dipstick colorimetry & 400x Brightfield microscopy", "Standard Test Strips & Centrifugation", "Rapid screening; negative test does not exclude low-titer or atypical urethral infection."),
            ("Transrectal / Transabdominal Ultrasound (TRUS)", "High-frequency acoustic imaging of prostatic parenchyma, seminal vesicles, and post-void residual urine volume.", "Echogenicity & vascular doppler mapping", "Ultrasound transducer (5-7.5 MHz)", "Unreliable for uncomplicated prostatitis; mandatory to rule out prostatic abscess."),
            ("Serum Inflammatory Markers (CBC, CRP, ESR)", "Venipuncture evaluation of peripheral white blood cell count, neutrophilia, and acute phase reactants.", "Automated flow cytometry & turbidimetry", "Standard Hematology Analyzers", "Indicates systemic inflammatory response; normal levels do NOT exclude localized genitourinary infection.")
        ],
        
        # Tab 4: Precursors, Authoritative Guidelines & Literature
        "lit_rows": [
            ("EAU Guidelines on Urological Infections", "Guidelines on diagnosis, empiric therapy, and imaging protocols for acute bacterial prostatitis", "European Association of Urology (EAU)", "2024 / 2026", "Firmly establishes that ultrasound is unreliable for prostatitis diagnosis; urine culture is mandatory."),
            ("CDC STI Treatment Guidelines", "Recommended regimens and diagnostic molecular assays for urethritis and Neisseria gonorrhoeae", "US Centers for Disease Control and Prevention (CDC)", "2021 / 2025 Update", "Designates First-Catch Urine NAAT as preferred diagnostic method; highlights asymptomatic carriage."),
            ("NICE Guideline NG110: Prostatitis", "Evidence-based pathway for managing acute bacterial prostatitis and indications for emergency hospital referral", "National Institute for Health and Care Excellence (NICE)", "2018 / 2024 Review", "Mandates collecting midstream urine prior to empiric antibiotics; outlines sepsis referral criteria."),
            ("Pediatric & Neonatal Infectious Disease", "Clinical course of untreated perinatal gonococcal infection in neonates (Ophthalmia Neonatorum)", "American Academy of Pediatrics (AAP) / WHO", "2023", "Confirms gonococcal infections present within 2-5 days postpartum with purulent conjunctivitis; zero latency."),
            ("Journal of Sexual Medicine / Urol Clin NA", "Differential diagnosis of male pelvic and pubic region pain: non-infectious orthopedic vs urological etiologies", "Peer-Reviewed Systematic Review", "2024", "Documents osteitis pubis, sports hernia, and adductor tendinopathy as frequent mimics of urogenital pain.")
        ],
        
        # Tab 5: Feasibility, Risk Matrix & Clinical Red Flags
        "risk_rows": [
            ("Urosepsis / Systemic Bacteremia", "Bacterial dissemination from infected prostate or urinary tract into bloodstream", 10, 3, 30, "Immediate emergency hospital admission, parenteral broad-spectrum antibiotics, fluid resuscitation."),
            ("Acute Urinary Retention (AUR)", "Severe prostatic inflammatory edema obstructing bladder neck outflow", 9, 4, 36, "Emergency suprapubic catheterization (avoid urethral catheterization in acute bacterial prostatitis)."),
            ("Prostatic Abscess Formation", "Localized purulent liquefaction within prostatic parenchyma failing antibiotic therapy", 8, 3, 24, "TRUS / Pelvic CT imaging follow-up; transurethral or transperineal surgical/needle drainage."),
            ("Fournier's Gangrene / Necrotizing Fasciitis", "Rapid polymicrobial necrotizing infection of perineal and external genital soft tissues", 10, 1, 10, "Immediate surgical debridement, broad-spectrum IV antimicrobial triple therapy, hemodynamic support."),
            ("Antimicrobial Resistance & Dysbiosis", "Inappropriate empiric antibiotic use causing secondary fungal blooms and microbial resistance", 5, 8, 40, "Antimicrobial stewardship: collect microbiological cultures before initiating targeted therapy."),
            ("Misdiagnosed Testicular Torsion", "Acute spermatic cord twisting causing ischemic testicular necrosis", 10, 2, 20, "Emergency testicular Doppler ultrasound and surgical exploration within 6 hours of acute onset.")
        ],
        
        # Tab 6: Phased Clinical Realization Roadmap & Action Plan
        "roadmap_rows": [
            ("Phase 1: Pre-Treatment Microbiological Sampling", "Obtain First-Catch Urine for NAAT (Gonorrhea/Chlamydia) and Clean-Catch Midstream Urine for Culture & Sensitivity", "Confirmed sample collection before antibiotic ingestion", "Hours 0 - 2", "Clinical Microbiology & Laboratory Medicine"),
            ("Phase 2: Red-Flag Triage & Physical Examination", "Assess for fever, urinary retention, severe scrotal pain, and perform gentle external genital and digital rectal examination", "Clinical stability confirmation or emergency hospital referral", "Immediate", "Urology / Emergency Medicine"),
            ("Phase 3: Interim Decision & Empiric vs Targeted Gating", "If severe bacterial prostatitis is suspected, start empiric regimen; if stable and subacute, hold for 48h culture results", "Targeted antimicrobial prescription based on culture AST", "Hours 2 - 48", "Infectious Disease / Clinical Pharmacology"),
            ("Phase 4: Laboratory Report Review & Regimen Adjustment", "Review urine culture AST, NAAT results, and ultrasound findings; de-escalate or narrow antibiotic coverage accordingly", "Pathogen-directed targeted therapy and partner notification if STI", "Hours 48 - 72", "Urology & Sexual Health Clinic"),
            ("Phase 5: Resolution Monitoring & Post-Treatment Evaluation", "Monitor symptom resolution (pubic pain, penile swelling, discharge); evaluate need for dermatological or orthopedic follow-up", "Complete symptomatic recovery and documented microbiological cure", "Days 7 - 14", "Primary Care / Outpatient Urology")
        ]
    }
    
    # ── 2. GENERATE EXCEL DOSSIER ──
    excel_path = generate_excel_dossier(topic, topic_dir, dossier_data)
    print(f"[*] Generated 6-Tab Excel Dossier: {excel_path} ({os.path.getsize(excel_path)} bytes)")
    
    # ── 3. GENERATE EXTENSIVE TECHNICAL MARKDOWN REPORT ──
    report_path = os.path.join(topic_dir, "RESEARCH_REPORT.md")
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    report_content = f"""# CLINICAL RESEARCH DOSSIER: PENILE SWELLING & PUBIC AREA PAIN
**Topic:** {topic}  
**Classification:** {category}  
**Authoring Agent:** Ask & Research Agent (`agy:ask`)  
**Generated For:** Iraq Bhai  
**Timestamp:** `{now_iso}`  
**Workspace Directory:** `{topic_dir}`  
**Artifact Excel:** `{os.path.basename(excel_path)}`  

---

## ১. নির্বাহী সারসংক্ষেপ ও প্রধান ক্লিনিক্যাল সিদ্ধান্ত (Executive Summary)
এই গবেষণা ডসিয়ারটি রোগীর উপস্থাপিত জটিল ক্লিনিক্যাল উপসর্গসমূহ—৪ দিনের পিউবিক অঞ্চলের ব্যথা, পেনিসের ত্বকের ফোলাভাব, দীর্ঘস্থায়ী ডিসচার্জের ইতিহাস এবং অ্যান্টিবায়োটিক সেবন পরবর্তী চুলকানি—আন্তর্জাতিক প্রোটোকল ([EAU](https://uroweb.org), [CDC](https://www.cdc.gov), [NICE](https://www.nice.org.uk)) অনুযায়ী পুঙ্খানুপুঙ্খ বিশ্লেষণ করে প্রণয়ন করা হয়েছে।

### প্রধান ফলাফলসমূহ:
1. **ফাঙ্গাল বনাম ব্যাকটেরিয়াল ইনফেকশন**: ক্যান্ডিডা ব্যালানাইটিস (Candida balanitis) পুরুষাঙ্গের উপরিভাগের চামড়ায় চুলকানি ও ফোলা তৈরি করতে পারে, তবে তলপেটের বা পিউবিক অঞ্চলের গভীর ব্যথা ফাঙ্গাল ইনফেকশনের স্বাভাবিক বৈশিষ্ট্য নয়। এটি প্রোস্টাটাইটিস, ইউরেথ্রাইটিস বা পেলভিক-মাস্কুলোস্কেলিটাল ব্যথার নির্দেশক।
2. **ল্যাব পরীক্ষা ও ইমেজিংয়ের প্রকৃত সত্য**: রক্ত পরীক্ষা (CBC, CRP, ESR) স্বাভাবিক থাকলেও প্রোস্টেট বা মূত্রনালির স্থানীয় ইনফেকশন বাতিল হয় না। একইভাবে, স্বাভাবিক আল্ট্রাসাউন্ড প্রোস্টাটাইটিসকে বাদ দিতে পারে না; আল্ট্রাসাউন্ডের মূল কাজ হলো প্রোস্ট্যাটিক অ্যাবসেস (abscess) বা ইউরিনারি রিটেনশন শনাক্ত করা।
3. **সিদ্ধান্ত কাঠামো (Antibiotic Timing)**: কোনো রেড-ফ্ল্যাগ উপসর্গ (জ্বর, প্রস্রাব আটকে যাওয়া, সেপসিস) না থাকলে এবং অ্যান্টিবায়োটিক শুরুর আগেই নমুনা নেওয়া হয়ে থাকলে ২ দিন কালচার রিপোর্টের জন্য অপেক্ষা করা যুক্তিসঙ্গত। তবে তীব্র ব্যাকটেরিয়াল প্রোস্টাটাইটিস সন্দেহ হলে ল্যাব রিপোর্টের আগেই অভিজ্ঞতামূলক অ্যান্টিবায়োটিক দেওয়া গাইডলাইন-অনুমোদিত।
4. **গনোরিয়ার সুপ্তাবস্থা সম্পর্কিত বৈজ্ঞানিক সত্যতা**: নাইসেরিয়া গনোরিয়া কোনো সুপ্ত ভাইরাস নয়। জন্মের সময় নবজাতকের সংক্রমণ হলে তা ২-৫ দিনের মধ্যে তীব্র লক্ষণ দেয়; সারাজীবন সুপ্ত থেকে প্রাপ্তবয়স্ক অবস্থায় পুনরায় সক্রিয় হওয়ার কোনো বৈজ্ঞানিক প্রমাণ নেই।

---

## ২. তাত্ত্বিক ও প্যাথোফিজিওলজিক্যাল ভিত্তি (Pathophysiological Foundations)
- **Candida Balanitis**: ত্বকের স্ট্র্যাটাম কর্নিয়ামে ক্যান্ডিডার বিস্তার। অ্যান্টিবায়োটিক ব্যবহারের ফলে স্বাভাবিক ব্যাকটেরিয়াল ভারসাম্য নষ্ট হলে সেকেন্ডারি ফাঙ্গাল ওভারগ্রোথ ত্বরান্বিত হয়।
- **Acute Bacterial Prostatitis**: ইউরো-প্যাথোজেনিক ব্যাকটেরিয়ার ঊর্ধ্বমুখী বিস্তার। গ্রন্থির প্রদাহজনিত ইডিমা ও স্ট্রোমাল অনুপ্রবেশের কারণে পিউবিক ও পেরিনিয়াল অঞ্চলে গভীর ব্যথা তৈরি হয়।
- **Infectious Urethritis**: *N. gonorrhoeae* বা *C. trachomatis* দ্বারা মূত্রনালির মিউকোসার সংক্রমণ। ডিসচার্জ ও প্রস্রাবে জ্বালা তৈরি করে, তবে অণ্ডকোষ না ফুলেও এটি বিদ্যমান থাকতে পারে।
- **Osteitis Pubis**: পিউবিক সিমফাইসিসের নন-ইনফেকশাস প্রদাহ। ইনফেকশন ছাড়াও পিউবিক অঞ্চলে তীব্র ব্যথার অন্যতম প্রধান কারণ।

---

## ৩. ডায়াগনস্টিক ওয়ার্কফ্লো ও আর্কিটেকচার (Diagnostic Architecture)
1. **First-Catch Urine NAAT/PCR**: মূত্রনালির এসটিআই (STI) শনাক্তকরণের আণবিক গোল্ড স্ট্যান্ডার্ড (সংবেদনশীলতা >৯৫%)।
2. **Midstream Urine Culture & AST**: সাধারণ ইউরিনারি প্যাথোজেন শনাক্তকরণ ও সঠিক অ্যান্টিবায়োটিক নির্ধারণ।
3. **Routine Urinalysis (Urine R/E)**: প্রাথমিক স্ক্রিনিং (লিউকোসাইট এস্টারেজ ও নাইট্রাইট)।
4. **Ultrasound (TRUS / Abdominal)**: প্রোস্টেটের অ্যাবসেস ও মূত্র ধারণ ক্ষমতা যাচাই।
5. **Inflammatory Markers (CBC, CRP, ESR)**: সিস্টেমিক প্রতিক্রিয়ার মূল্যায়ন।

---

## ৪. ফিজিবিলিটি ও ক্লিনিক্যাল ঝুঁকি মেট্রিক্স (Risk Matrix & Red Flags)
জরুরি হাসপাতালে যাওয়ার লক্ষণসমূহ:
- প্রস্রাব পুরোপুরি আটকে যাওয়া (Acute Urinary Retention)
- কাঁপুনি সহ তীব্র জ্বর ও সেপসিসের লক্ষণ (Urosepsis)
- দ্রুত বর্ধনশীল জেনিটাল ফোলা বা ত্বকে কালচে/বেগুনী দাগ (Fournier's Gangrene সন্দেহ)
- অণ্ডকোষে তীব্র আকস্মিক ব্যথা (Testicular Torsion)

---

## ৫. সিদ্ধান্ত রোডম্যাপ (Clinical Decision Roadmap)
- **ধাপ ১**: অ্যান্টিবায়োটিক শুরুর আগে প্রস্রাবের সঠিক নমুনা সংগ্রহ (First-catch NAAT + Midstream Culture)।
- **ধাপ ২**: জরুরি রেড-ফ্ল্যাগ লক্ষণ পরীক্ষা ও ক্লিনিক্যাল মূল্যায়ন।
- **ধাপ ৩**: কালচার রিপোর্ট আসা পর্যন্ত অপেক্ষা বনাম অভিজ্ঞতামূলক চিকিৎসা নির্ধারণ।
- **ধাপ ৪**: ল্যাব রিপোর্ট অনুযায়ী সুনির্দিষ্ট অ্যান্টিবায়োটিক সমন্বয়।

---
*সম্পূর্ণ ৬-ট্যাব বিশ্লেষণ `{slug}_research_dossier.xlsx` ফাইলে সংরক্ষিত।*
"""
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content.strip() + "\n")
    print(f"[*] Generated Comprehensive Research Report: {report_path} ({os.path.getsize(report_path)} bytes)")
    
    # ── 4. RECORD METADATA & REGISTRY ──
    metadata = {
        "topic": topic,
        "slug": slug,
        "category": category,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "files": {
            "excel": os.path.basename(excel_path),
            "report": os.path.basename(report_path)
        },
        "status": "COMPLETED"
    }
    with open(os.path.join(topic_dir, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        
    record_registry(topic, topic_dir, excel_path, report_path)
    print(f"[*] Recorded research registry entry.")
    
    # ── 5. DISPATCH TO WHATSAPP OUTBOX ──
    job_file = dispatch_to_whatsapp(topic, topic_dir, excel_path, report_path)
    print(f"[*] Dispatched to WhatsApp Outbox: {job_file}")
    
    return {
        "subfolder": topic_dir,
        "excel_path": excel_path,
        "report_path": report_path,
        "job_file": job_file
    }

if __name__ == "__main__":
    res = run()
    print("\n[SUCCESSFUL_EXECUTION_RESULT]:")
    print(json.dumps(res, indent=2))
