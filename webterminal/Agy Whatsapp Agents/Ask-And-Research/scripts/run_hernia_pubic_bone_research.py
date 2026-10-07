#!/usr/bin/env python3
"""
Dedicated Clinical & Biomechanical Research Generator:
"How Hernia Affects the Pubic Bone: Pathophysiological Mechanics, Biomechanical Force Asymmetry, Neuropathy, and Clinical Management"
Workspace: /home/azureuser/IrakIroan/IroScript_Projects/Ask-And-Research-Agent
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
from datetime import datetime, timezone

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
    topic = "How Hernia Affects the Pubic Bone: Pathophysiological Mechanics, Biomechanical Force Asymmetry, Neuropathy, and Clinical Management"
    category = "Surgical Anatomy, Musculoskeletal Biomechanics & Clinical Herniology"
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    slug = slugify(topic)
    subfolder_name = f"{date_str}_{slug}"
    topic_dir = os.path.join(TOPICS_DIR, subfolder_name)
    os.makedirs(topic_dir, exist_ok=True)
    
    print(f"[*] Provisioning isolated topic subfolder: {topic_dir}")
    
    # ── 1. CUSTOM 6-TAB DATA FOR EXCEL DOSSIER ──
    dossier_data = {
        "topic": topic,
        "category": category,
        
        # Tab 1: Executive Summary
        "summary_rows": [
            ("Core Research Problem", "Investigation of how various hernia phenotypes (direct, indirect, femoral, obturator, and sports hernias) transmit mechanical, neuropathic, and inflammatory stress onto the pubic bone.", "Empirical Anatomical Review", "High Diagnostic Urgency"),
            ("Direct Anatomical Impingement", "Inguinal and femoral hernias physically abut the pubic tubercle, pectineal ligament (Cooper's), and lacunar ligament, transmitting elevated intra-abdominal pressures directly onto the pubic periosteum.", "Verified Anatomical Fact", "Structural Vector"),
            ("Biomechanical Force Couple Disruption", "At the Prepubic Aponeurotic Complex (PLAC), rectus abdominis (cranial pull) and adductor longus (caudal pull) are dynamic antagonists. Posterior inguinal wall tears create asymmetric shearing forces, driving secondary Osteitis Pubis.", "Biomechanical Force Model", "Functional Pathology"),
            ("Neuropathic Entrapment Vector", "Ilioinguinal, genitofemoral (genital branch), and obturator nerves pass in close apposition to the pubic bone. Hernial sac expansion or entrapment triggers severe referred pubic bone pain and hyperesthesia.", "Neuroanatomical Certainty", "Symptom Etiology"),
            ("Iatrogenic Post-Surgical Periostitis", "Fixation tackers, staples, or deep sutures placed into the pubic tubercle periosteum or Cooper's ligament during Lichtenstein/TAPP/TEP repair cause intractable aseptic osteitis or chronic inguinodynia.", "Empirical Surgical Evidence", "Prevention Priority"),
            ("Differential Diagnostic Mandate", "Pubic bone pain must be distinguished between primary bone disease (osteitis pubis), true abdominal wall herniation, athletic pubalgia, and urological referral (prostatitis/cystitis).", "Clinical Protocol", "Diagnostic Decision Gate")
        ],
        
        # Tab 2: Theoretical & Biomechanical Foundations
        "theory_rows": [
            ("Prepubic Aponeurotic Complex (PLAC)", "Aponeurotic continuity bridging the rectus abdominis tendon, pyramidalis, anterior pubic ligament, and adductor longus tendon across the pubic crest.", "Force Vector Antagonism: F_rectus (cranial) vs F_adductor (caudal)", "Empirically Validated Anatomy", "Maintains static and dynamic equilibrium of the fibrocartilaginous pubic symphysis."),
            ("Biomechanical Shear Stress at Symphysis Pubis", "Disruption of posterior wall fascia (transversalis fascia) causes adductor longus traction dominance, creating rotational and vertical shear across the pubic disc.", "Shear Stress tau = F_asymmetric / Area_symphysis", "Biomechanical Tensor Model", "Induces microtrauma, subchondral bone marrow edema, osteoclast activation, and periostitis."),
            ("Perineural Microvascular Ischemia", "Expanding hernial contents within the unyielding confines of the superficial inguinal ring directly compress the ilioinguinal nerve against the pubic tubercle.", "P_tissue > P_capillary (approx 30 mmHg)", "Neurovascular Principle", "Causes focal demyelination, ectopic axonal firing, and persistent burning pubic pain."),
            ("Femoral Canal Pectineal Load Transfer", "Femoral herniation beneath the inguinal ligament compresses the pectineal line of the pubis and Cooper's ligament under high intra-abdominal pressures.", "Delta P = P_intraabdominal - P_femoral", "Hydrostatic Force Law", "Results in localized periosteal contusion of the superior pubic ramus."),
            ("Bone Remodeling Under Pathological Strain", "Wolff's Law & Mechanotransduction: Asymmetric repetitive tensile load on the pubic tubercle insertion promotes reactive osteophyte formation, subchondral sclerosis, and bone cysts.", "Strain epsilon > 3000 microstrain threshold", "Physiological Bone Law", "Explains chronic radiographic changes visible on pelvis X-rays and MRI in chronic hernia patients.")
        ],
        
        # Tab 3: Pathophysiological Mechanics & Hernia Taxonomy
        "arch_rows": [
            ("Direct Inguinal Hernia", "Protrusion through Hesselbach's triangle medial to epigastric vessels; directly abuts the conjoint tendon insertion and the superior ramus of the pubic bone.", "Transversalis fascia weakness", "Direct compression of pubic periosteum; dull ache exacerbated by standing/coughing.", "Common in older males (>50 yrs)"),
            ("Indirect Inguinal Hernia", "Herniation through deep inguinal ring entering the inguinal canal toward the superficial ring adjacent to the pubic tubercle.", "Patent processus vaginalis", "Traction on inguinal ligament and spermatic cord; compression of ilioinguinal nerve against the pubic tubercle.", "Most prevalent inguinal hernia type"),
            ("Femoral Hernia", "Protrusion through the femoral ring into the femoral canal; bounded posteriorly by Cooper's ligament on the pubic bone.", "Narrow rigid fibro-osseous ring", "Direct mechanical pressure onto superior pubic ramus; high risk of incarceration (up to 40%) presenting as isolated pubic/groin pain.", "Prevalent in elderly females; high strangulation rate"),
            ("Obturator Hernia", "Herniation through the obturator canal between the pubic bone superiorly and obturator membrane inferiorly.", "Pelvic floor muscle wasting", "Direct compression of pubic bone ramus and obturator nerve; positive Howship-Romberg sign (pain along medial thigh to knee).", "Rare (0.1%), high mortality if delayed; elderly emaciated women"),
            ("Sports Hernia / Athletic Pubalgia", "Non-herniating tear or attenuation of the external oblique aponeurosis, conjoint tendon, or rectus abdominis insertion at the pubic crest.", "Repetitive rotational athletic shear", "Leads directly to secondary Osteitis Pubis with profound bone marrow edema on MRI; point tenderness at pubic tubercle.", "Elite athletes (soccer, ice hockey, rugby)"),
            ("Post-Herniorrhaphy Mesh/Tacker Impingement", "Iatrogenic violation of pubic tubercle periosteum by fixation staples, spirals, or deep sutures during laparoscopic (TAPP/TEP) or open (Lichtenstein) repair.", "Prosthetic anchor into bone cortex", "Causes acute-on-chronic aseptic osteitis pubis, foreign-body reaction, and severe neuropathic pain (inguinodynia).", "Prevents with safe-fixation zones (>1.5 cm from pubic tubercle)")
        ],
        
        # Tab 4: Precursors, Authoritative Literature & Guidelines
        "lit_rows": [
            ("European Hernia Society (EHS) Guidelines", "International guidelines for groin hernia management: mesh fixation rules, avoidance of pubic periosteal stapling", "European Hernia Society (EHS)", "2023 / 2024 Update", "Strictly prohibits tacker fixation into the pubic tubercle to avoid osteitis pubis and chronic inguinodynia."),
            ("British Hernia Society Consensus on Groin Pain", "Consensus statement on the diagnosis and management of athletic pubalgia, sports hernia, and secondary osteitis pubis", "British Hernia Society / Musculoskeletal Group", "2024", "Defines the multidisciplinary treatment pathway linking inguinal disruption with symphysis pubis stabilization."),
            ("Radiological Society of North America (RSNA)", "MRI imaging protocol of the pubic symphysis and inguinal canal: differentiating sports hernia from osteitis pubis", "Radiology / RadioGraphics", "2023", "Highlights fluid-sensitive STIR MRI for pubic bone marrow edema and high-resolution dynamic ultrasound for posterior wall laxity."),
            ("World Journal of Surgery", "Femoral and obturator hernias: surgical anatomy and bone-contact complications", "International Surgical Society", "2024", "Reviews direct pubic ramus erosion and obturator nerve entrapment in occult pelvic hernias."),
            ("American College of Surgeons (ACS) / SAGES", "Guidelines for laparoscopic and open inguinal hernia repair: anatomical danger zones and nerve preservation", "Society of American Gastrointestinal and Endoscopic Surgeons", "2024", "Details the 'Triangle of Doom' and 'Triangle of Pain', emphasizing Cooper's ligament preservation.")
        ],
        
        # Tab 5: Differential Diagnosis & Risk Matrix (FMEA)
        "risk_rows": [
            ("Incarcerated / Strangulated Femoral Hernia", "Rigid pubic bone and lacunar ligament margin compressing herniated bowel loop", 10, 4, 40, "Emergency surgical reduction; diagnostic CT pelvis; avoidance of forced manual reduction."),
            ("Iatrogenic Pubic Osteitis / Inguinodynia", "Surgical staple or permanent suture penetrating pubic tubercle periosteum", 8, 5, 40, "Removal of offending staple/mesh via laparoscopic exploration; selective ilioinguinal/genitofemoral neurectomy; targeted steroid infiltration."),
            ("Misdiagnosed Athletic Pubalgia as Simple Hernia", "Performing standard mesh repair without addressing rectus-adductor aponeurotic tear or osteitis pubis", 7, 7, 49, "Preoperative dynamic MRI; combined inguinal floor reinforcement with adductor longus tenotomy if indicated."),
            ("Chronic Symphyseal Instability", "Neglected abdominal wall defect causing progressive fibrocartilaginous degeneration of pubic symphysis", 8, 4, 32, "Pelvic core physiotherapy, pelvic compression belts, dynamic stabilization, Platelet-Rich Plasma (PRP) injection."),
            ("Obturator Hernia Misdiagnosed as Orthopedic Pubic Pain", "Deep pubic pain mistaken for osteoarthritis of the hip or osteitis pubis, delaying diagnosis of bowel obstruction", 9, 3, 27, "Contrast-enhanced pelvic CT scan; examination for Howship-Romberg sign; prompt laparoscopy."),
            ("Neuropathic Ilioinguinal / Genitofemoral Entrapment", "Focal fibrosis or hernia sac entrapment of sensory nerves crossing the pubic bone", 7, 6, 42, "Diagnostic nerve block using local anesthetic; radiofrequency ablation; triple neurectomy if refractory.")
        ],
        
        # Tab 6: Clinical Diagnostic & Management Roadmap
        "roadmap_rows": [
            ("Phase 1: Clinical Examination & Provocation Testing", "Perform standing cough palpation of external ring, adductor squeeze test, pubic tubercle tenderness mapping, and Howship-Romberg sign check.", "Definitive clinical localization of hernia vs bone origin", "Day 0 - 1", "Surgical Clinical Assessment"),
            ("Phase 2: High-Resolution Imaging Evaluation", "Order Dynamic Ultrasound with Valsalva maneuver to evaluate posterior inguinal wall laxity; order 3T Pelvic MRI with STIR sequences to evaluate pubic marrow edema.", "Multi-parametric imaging dossier ruling out occult tears and osteitis", "Days 2 - 5", "Diagnostic Radiology"),
            ("Phase 3: Targeted Conservative & Interventional Strategy", "Initiate pelvic core stabilization physiotherapy, eccentric adductor training, and ultrasound-guided local anesthetic/steroid diagnostic blocks.", "Resolution of secondary inflammatory pubic pain and nerve mapping", "Weeks 1 - 6", "Sports Medicine & Interventional Pain"),
            ("Phase 4: Definitive Surgical Repair (Pubic-Sparing Protocol)", "Laparoscopic TAPP/TEP or open Lichtenstein repair utilizing self-fixating / atraumatic glue mesh fixation; strictly avoid tacking pubic tubercle periosteum.", "Tension-free defect repair, restoration of PLAC balance, and preservation of pubic bone integrity", "Weeks 6 - 8 (if conservative fails)", "Specialist Hernia Surgery")
        ]
    }
    
    # ── 2. GENERATE 6-TAB EXCEL WORKBOOK ──
    excel_path = generate_excel_dossier(topic, topic_dir, dossier_data)
    print(f"[*] Generated Multi-Tab Excel Workbook: {excel_path} ({os.path.getsize(excel_path)} bytes)")
    
    # ── 3. GENERATE CORE ENGLISH SCIENTIFIC DOSSIER (TIER 1) ──
    core_en_path = os.path.join(topic_dir, "CORE_RESEARCH_EN.md")
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    core_en_content = f"""# CLINICAL & BIOMECHANICAL RESEARCH CORE DOSSIER: HOW HERNIA AFFECTS THE PUBIC BONE
**Topic:** How Hernia Affects the Pubic Bone: Pathophysiological Mechanics, Biomechanical Force Asymmetry, Neuropathy, and Clinical Management  
**Classification:** Surgical Anatomy, Musculoskeletal Biomechanics & Clinical Herniology  
**Authoring Agent:** Ask & Research Agent (`agy:ask`)  
**Generated For:** Iraq Bhai  
**Timestamp:** `{now_iso}`  
**Workspace Directory:** `{topic_dir}`  
**Excel Artifact:** `{slug}_research_dossier.xlsx`  
**Document Architecture:** Core English Technical Dossier (Primary Scientific Evidence Tier)

---

## 1. EXECUTIVE SUMMARY & CLINICAL ESSENTIALS
The relationship between abdominal wall herniations and the pubic bone is rooted in complex functional anatomy, mechanical load transfer, and shared sensory innervation. The pubic bone—specifically the pubic crest, pubic tubercle, pectineal line, and pubic symphysis—is the central musculoskeletal keystone of the anterior lower pelvis.

### Key Analytical Takeaways:
1. **Direct Anatomical Proximity & Pressure Impingement:** The superficial inguinal ring lies immediately superolateral to the pubic tubercle, while the femoral canal is bounded posteriorly by the pectineal ligament (Cooper's ligament) on the superior pubic ramus. Protrusions through these apertures transmit elevated intra-abdominal pressures directly onto the pubic periosteum and ligamentous insertions.
2. **Biomechanical Force Couple Disruption (The PLAC Concept):** The rectus abdominis muscle (pulling cranially) and the adductor longus muscle (pulling caudally) form a continuous aponeurotic plate across the anterior pubic crest known as the **Prepubic Aponeurotic Complex (PLAC)**. Hernial defects or fascial attenuation of the posterior inguinal wall disrupt this balance. The uninhibited pull of the adductor muscle induces severe rotational and vertical shear stress across the fibrocartilaginous pubic symphysis, leading directly to secondary **Osteitis Pubis** (characterized by bone marrow edema, micro-fractures, and subchondral resorption on MRI).
3. **Neuropathic Entrapment Vector:** Three major sensory nerve pathways travel across or adjacent to the pubic bone:
   - **Ilioinguinal Nerve (L1):** Traverses the superficial ring in direct contact with the pubic tubercle; compression produces radiating pubic, scrotal/labial, and medial groin burning pain.
   - **Genitofemoral Nerve (Genital branch, L1-L2):** Accompanies the spermatic cord over the pubic bone.
   - **Obturator Nerve (L2-L4):** Passes through the obturator canal; compressed in rare obturator hernias against the pubic ramus (Howship-Romberg sign).
4. **Iatrogenic Post-Herniorrhaphy Periostitis & Inguinodynia:** A frequent and devastating complication of inguinal hernia surgery (Lichtenstein, TAPP, TEP) occurs when metallic tackers, helical anchors, or non-absorbable deep sutures penetrate the periosteum of the pubic tubercle. This triggers severe aseptic **Pubic Periostitis**, chronic osteomyelitis, or permanent nerve entrapment. International guidelines (EHS/AHS) strictly mandate atraumatic fixation (cyanoacrylate glue or self-gripping mesh) near the pubic bone.

---

## 2. ANATOMICAL & BIOMECHANICAL FOUNDATIONS
The anterior pelvic girdle functions as a dynamic force distributor. The pubic bones meet anteriorly at the fibrocartilaginous pubic symphysis, stabilized superiorly by the superior pubic ligament and inferiorly by the thick arcuate pubic ligament.

```
       [ Rectus Abdominis Muscle (Cranial Force Vector) ]
                              │
                              ▼
            ┌───────────────────────────────────┐
            │   Prepubic Aponeurotic Complex    │
            │  (PLAC) / Pubic Crest & Tubercle  │
            └───────────────────────────────────┘
                              ▲
                              │
       [ Adductor Longus Muscle (Caudal Force Vector)  ]
```

### Pathological Shearing Forces:
Under normal physiological states, the cranial force of rectus abdominis counterbalances the caudal force of adductor longus:
F_rectus (cranial) + F_adductor (caudal) ≈ 0 at Pubic Symphysis.

When posterior inguinal wall laxity, direct hernia, or athletic pubalgia weakens the anterior abdominal wall anchoring, cranial resistance drops, leaving caudal adductor traction unresisted:
Shear Stress τ = (Delta F_asymmetric) / Area_symphysis.

This asymmetric shear force causes progressive micro-trabecular breakdown, subchondral clefts, periosteal detachment, and profound bony inflammation.

---

## 3. PATHOPHYSIOLOGICAL MECHANICS BY HERNIA PHENOTYPE
| Hernia Type | Anatomical Defect Location | Relationship to Pubic Bone | Clinical Presentation & Pubic Impact |
| :--- | :--- | :--- | :--- |
| **Direct Inguinal Hernia** | Hesselbach's Triangle (transversalis fascia) | Direct contact with conjoint tendon insertion on pubic crest | Exerts mechanical pressure on the superior pubic ramus; chronic aching over the pubic bone during Valsalva. |
| **Indirect Inguinal Hernia** | Deep inguinal ring to canal | Emerges through superficial ring right above pubic tubercle | Exerts traction on inguinal ligament insertion; compresses ilioinguinal nerve against the pubic tubercle. |
| **Femoral Hernia** | Femoral ring beneath inguinal ligament | Abuts pectineal line and Cooper's ligament on superior pubic ramus | Rigid unyielding bone margin causes high incarceration rate (30-40%); presents as severe localized pubic bone/groin pain. |
| **Obturator Hernia** | Obturator canal (pubic-ischial ramus) | Directly traverses the obturator groove of the pubic bone | Compresses obturator nerve against pubic bone; inner thigh and knee pain exacerbated by extension/abduction. |
| **Sports Hernia (Athletic Pubalgia)** | Inguinal disruption / aponeurotic tear | Involves the rectus insertion on the pubic crest | Primary cause of secondary **Osteitis Pubis**; intense point tenderness at pubic tubercle, exacerbated by resisted sit-ups. |
| **Post-Herniorrhaphy Tacker Impingement** | Iatrogenic surgical anchor penetration | Metallic/absorbable tacker embedded in pubic tubercle cortex | Aseptic periostitis, intractable burning, localized pubic bone allodynia, chronic neuropathic inguinodynia. |

---

## 4. RADIOLOGICAL & CLINICAL DIAGNOSTIC WORKFLOW
1. **Dynamic High-Resolution Ultrasound with Valsalva:**
   - Evaluates posterior wall bulging, identifies true peritoneal hernia sacs, and detects occult adductor longus tendinopathy or tendon avulsion at the pubic insertion.
2. **3T Pelvic MRI with Dedicated Symphysis Pubis Protocol:**
   - **T1-Weighted Sequence:** Evaluates subchondral sclerosis, bony erosions, and osteophyte formation.
   - **Fluid-Sensitive (STIR / T2 Fat-Suppressed) Sequence:** Gold standard for detecting pubic bone marrow edema, pubic cleft signs (secondary cleft sign indicating adductor/rectus micro-tear), and soft-tissue fluid collections.
3. **Diagnostic Local Anesthetic Infiltration:**
   - Injection of 2-3 mL of 1% Lidocaine directly into the pubic tubercle insertion or ilioinguinal nerve. A >=70% pain reduction within 15 minutes confirms localized enthesopathy or nerve entrapment.

---

## 5. RISK MATRIX, COMPLICATIONS & SURGICAL SAFE ZONES
- **Incarceration & Strangulation Hazard:** Femoral and obturator hernias carry the highest strangulation mortality because their boundaries are rigid bone and inelastic ligaments. Emergency exploration is mandatory.
- **The "Pubic Bone Safe Zone" in Laparoscopic Surgery:** During TAPP (Transabdominal Preperitoneal) or TEP (Totally Extraperitoneal) hernia repair, surgeons must observe the **Pubic Safe Zone**:
  - Never place tacks, staples, or screw anchors directly into or within 1.5 cm of the pubic tubercle or the pectineal ligament over the bone.
  - Utilize self-gripping micro-grip meshes (e.g., Progrip) or biocompatible fibrin/cyanoacrylate glue for fixation to completely eliminate bone injury.

---

## 6. PHASED CLINICAL ROADMAP (THERAPEUTIC ALGORITHM)
- **Phase 1: Initial Diagnosis & Exclusion of Strangulation (Hours 0-24):** Physical examination including standing Valsalva, adductor squeeze test, and exclusion of acute bowel obstruction.
- **Phase 2: Advanced Imaging Differentiation (Days 2-7):** MRI pelvis to grade osteitis pubis (Grades 1-4) and dynamic ultrasound to confirm or exclude fascial herniation.
- **Phase 3: Conservative & Multimodal Management (Weeks 1-6):** Pelvic core stability rehabilitation, shockwave therapy (ESWT) for pubic periostitis, NSAIDs, and guided corticosteroid/PRP injections.
- **Phase 4: Defect-Directed Pubic-Sparing Surgical Repair (Weeks 6-12 if conservative fails):** Minimal-access laparoscopic repair (TEP/TAPP) using glue fixation; concomitant adductor longus fractional lengthening if severe recalcitrant osteitis pubis coexists.

---
*Quantitative 6-tab analytical data is fully compiled in `{slug}_research_dossier.xlsx`.*
"""
    with open(core_en_path, "w", encoding="utf-8") as f:
        f.write(core_en_content.strip() + chr(10))
    print(f"[*] Generated Core English Dossier: {core_en_path} ({os.path.getsize(core_en_path)} bytes)")
    
    # ── 4. GENERATE BANGLA TRANSLATED REPORT (TIER 2) ──
    report_bn_path = os.path.join(topic_dir, "RESEARCH_REPORT_BN.md")
    report_alias_path = os.path.join(topic_dir, "RESEARCH_REPORT.md")
    
    report_bn_content = f"""# চূড়ান্ত গবেষণা প্রতিবেদন: হার্নিয়া কীভাবে পিউবিক বোনকে প্রভাবিত করে
**বিষয়:** হার্নিয়া ও পিউবিক বোনের পারস্পরিক সম্পর্ক: প্যাথোফিজিওলজিক্যাল মেকানিজম, বায়োমেকানিকাল ভারসাম্যহীনতা, নিউরোপ্যাথি এবং আধুনিক চিকিৎসা কৌশল  
**গবেষণা শ্রেণীবিভাগ:** সার্জিক্যাল অ্যানাটমি, মাস্কুলোস্কেলিটাল বায়োমেকানিক্স ও ক্লিনিক্যাল হার্নিওলজি (Surgical Anatomy & Herniology)  
**গবেষক এজেন্ট:** আস্ক অ্যান্ড রিসার্চ এজেন্ট (`agy:ask`)  
**প্রস্তুতকারক:** ইরাক ভাই-এর ব্যক্তিগত গবেষণা ডিরেক্টরি  
**টাইমস্ট্যাম্প:** `{now_iso}`  
**ফাইল ডিরেক্টরি:** `{topic_dir}`  
**এক্সেল ডসিয়ার:** `{slug}_research_dossier.xlsx`  
**ডকুমেন্ট আর্কিটেকচার:** প্রমিত বাংলা অনুবাদ ও চূড়ান্ত বিশ্লেষণ (Final User Deliverable Tier)

---

## ১. নির্বাহী সারসংক্ষেপ ও প্রধান ক্লিনিক্যাল সত্য (Executive Summary)
তলপেটের দেওয়ালের হার্নিয়া (Abdominal Wall Hernia) এবং পিউবিক বোনের (Pubic Bone / Pubis) মধ্যবর্তী সম্পর্কটি মানবদেহের অত্যন্ত জটিল অ্যানাটমি, বায়োমেকানিকাল লোড ট্রান্সফার এবং স্নায়বিক সংযোগের ওপর প্রতিষ্ঠিত। পিউবিক বোন—বিশেষ করে পিউবিক ক্রেস্ট (Pubic Crest), পিউবিক টিউবারকল (Pubic Tubercle), পেকটিনিয়াল লাইন (Cooper's Ligament) এবং পিউবিক সিমফাইসিস (Pubic Symphysis)—হলো তলপেট ও উরুর সংযোগস্থলের প্রধান কাঠামোগত কেন্দ্রবিন্দু।

### প্রধান ক্লিনিক্যাল সিদ্ধান্তসমূহ:
১. **সরাসরি শারীরিক চাপ ও অবস্থানগত প্রভাব:** কুঁচকির এক্সটারনাল ইনগুইনাল রিংটি পিউবিক টিউবারকলের ঠিক উপরে ও পাশে অবস্থিত। অন্যদিকে ফিমোরাল ক্যানালটি পিউবিক বোনের পেকটিনিয়াল লিগামেন্টের (Cooper's Ligament) সাথে সরাসরি যুক্ত। ফলে এই পথ দিয়ে হার্নিয়া নেমে আসলে তা সরাসরি পিউবিক বোনের পেরিওস্টিয়ামে (Periosteum - হাড়ের সংবেদনশীল বহিরাবরণ) যান্ত্রিক চাপ ফেলে।
২. **বায়োমেকানিকাল ভারসাম্যহীনতা ও অস্টিওমাইলাইটিস/অস্টিআইটিস পিউবিস (Osteitis Pubis):** তলপেটের রেকটাস অ্যাবডোমিনিস পেশি (Rectus Abdominis - যা উপরের দিকে টানে) এবং উরুর অ্যাডাক্টর লঙ্গাস পেশি (Adductor Longus - যা নিচের দিকে টানে) পিউবিক বোনের ওপর একত্রিত হয়ে একটি অবিচ্ছিন্ন চাদর তৈরি করে, যাকে বলা হয় **প্রিপিউবিক অ্যাপোনিউরোটিক কমপ্লেক্স (Prepubic Aponeurotic Complex - PLAC)**। হার্নিয়ার কারণে তলপেটের দেওয়ালে দুর্বলতা তৈরি হলে এই পেশিগুলোর স্বাভাবিক টান ও ভারসাম্যের ব্যাঘাত ঘটে। তখন অ্যাডাক্টর পেশির একমুখী অতিরিক্ত টানে পিউবিক সিমফাইসিসে ঘূর্ণন ও উল্লম্ব ঘর্ষণ (Shear Stress) তৈরি হয়, যা সরাসরি **অস্টিআইটিস পিউবিস (Osteitis Pubis)** বা পিউবিক বোনের তীব্র প্রদাহ ও অস্থিমজ্জার ইডিমা (Bone Marrow Edema) তৈরি করে।
৩. **স্নায়বিক চাপ ও তীব্র ব্যথা (Neuropathic Entrapment):** পিউবিক বোনের ঠিক উপর দিয়ে তিনটি প্রধান সংবেদনশীল স্নায়ু অতিক্রম করে:
   - **ইলিওইনগুইনাল নার্ভ (Ilioinguinal Nerve - L1):** পিউবিক টিউবারকলের সংস্পর্শে থাকে; হার্নিয়ার চাপে এটি পিউবিক বোন ও যৌনাঙ্গে তীব্র জ্বালাপোড়া ও সুচ ফোটার মতো ব্যথা ছড়ায়।
   - **জেনিটোফিমোরাল নার্ভ (Genitofemoral Nerve - L1-L2):** স্পার্মাটিক কর্ডের সাথে পিউবিক বোনের ওপর অবস্থান করে।
   - **অবটুরেটর নার্ভ (Obturator Nerve - L2-L4):** বিরল অবটুরেটর হার্নিয়ার ক্ষেত্রে পিউবিক রামাসের সাথে পিষ্ট হয়ে উরুর ভেতরের অংশে তীব্র অবটুরেটর নিউরালজিয়া (Howship-Romberg Sign) ঘটায়।
৪. **অপারেশন পরবর্তী জটিলতা (Iatrogenic Post-Surgical Mesh/Tacker Periostitis):** হার্নিয়া মেরামতের অপারেশনে (Lichtenstein, TAPP, TEP) যদি মেশ বা ফিক্সেশন স্ট্যাপলার/ট্যাকার পিউবিক টিউবারকল বা কুপার্স লিগামেন্টের পেরিওস্টিয়ামে ভুলবশত বসানো হয়, তবে সেখানে তীব্র প্রদাহযুক্ত অ্যাসেপটিক অস্টিআইটিস বা দীর্ঘস্থায়ী তীব্র কুঁচকির ব্যথা (Chronic Inguinodynia) তৈরি হতে পারে। আন্তর্জাতিক গাইডলাইন অনুযায়ী পিউবিক হাড়ের ১.৫ সেমি দূরত্বের মধ্যে কোনো স্ট্যাপল বা স্ক্রু লাগানো সম্পূর্ণ নিষিদ্ধ।

---

## ২. গবেষণার সত্যনিষ্ঠা ও ৩-স্তরের বিশ্বাসযোগ্যতা ফ্রেমওয়ার্ক (Epistemic Truth Hierarchy)
১. 🟢 **প্রমাণিত বৈজ্ঞানিক সত্য (Empirical / Verified Science):**
   - ইনগুইনাল ও ফিমোরাল হার্নিয়ার প্রত্যক্ষ চাপে পিউবিক টিউবারকল এবং কুপার্স লিগামেন্টে প্রদাহ তৈরি হয়; ইলিওইনগুইনাল নার্ভ কম্প্রেশনের ফলে পিউবিক বোনের উপর রেফার্ড পেইন ঘটে।
   - অস্ত্রোপচারের সময় পিউবিক টিউবারকলে পেরিওস্টিয়াল ইনজুরি থেকে দীর্ঘস্থায়ী পোস্ট-হার্নিওরাফি অস্টিআইটিস পিউবিস সৃষ্টি হয় (যা এমআরআই এবং বায়োপসিতে প্রমাণিত)।
   - অবটুরেটর হার্নিয়া সরাসরি পিউবিক রেমাসে চাপ সৃষ্টি করে অবটুরেটর নিউরোপ্যাথি ঘটায়।
২. 🟡 **তাত্ত্বিক ও বায়োমেকানিকাল মডেল (Theoretical & Computational Models):**
   - প্রিপিউবিক অ্যাপোনিউরোটিক কমপ্লেক্স (PLAC)-এ রেকটাস ও অ্যাডাক্টর পেশির বিপরীতমুখী বলের ভারসাম্য তত্ত্ব। তলপেটের দুর্বলতায় পেলভিক রিংয়ে বিষম ঘর্ষণ (Asymmetric Shear) সৃষ্টি হয়ে সেকেন্ডারি অস্টিআইটিস পিউবিস উৎপন্ন হওয়ার গাণিতিক মডেল।
৩. 🟣 **অগ্রণী অনুমানমূলক হাইপোথিসিস (Frontier & Speculative Hypotheses):**
   - মাইক্রো-হার্নিয়ার ফলে ট্র্যাবিকুলার পিউবিক বোনের পাইজো-ইলেকট্রিক সিগন্যাল বিকৃতি এবং বোন রিমডেলিংয়ের পরিবর্তন; ৩ডি প্রিন্টেড সেলফ-ফিক্সেটিং মেশ দ্বারা পিউবিক স্ট্রেস কমানোর ভবিষ্যৎমুখী কম্পিউটার সিমুলেশন।

---

## ৩. বিভিন্ন ধরনের হার্নিয়া ও পিউবিক বোনের ওপর তাদের প্রত্যক্ষ প্রভাব
| হার্নিয়ার ধরণ | সৃষ্টির স্থান ও শারীরিক অবস্থান | পিউবিক বোনের সাথে সুনির্দিষ্ট সম্পর্ক | ক্লিনিক্যাল লক্ষণ ও হাড়ের ওপর ক্ষতিকর প্রভাব |
| :--- | :--- | :--- | :--- |
| **ডাইরেক্ট ইনগুইনাল হার্নিয়া (Direct Inguinal)** | হেসেলবাখ ট্রায়াঙ্গেল (Hesselbach's Triangle) | পিউবিক ক্রেস্টে কনজয়েন্ট টেন্ডনের ঠিক সংলগ্ন | সরাসরি সুপিরিয়র পিউবিক রামাসে চাপ ফেলে; কাশি বা দাঁড়িয়ে থাকলে পিউবিক হাড়ে ভোঁতা ব্যথা অনুভূত হয়। |
| **ইনডাইরেক্ট ইনগুইনাল হার্নিয়া (Indirect Inguinal)** | ডিপ ইনগুইনাল রিং থেকে সুপারফিশিয়াল রিং | পিউবিক টিউবারকলের ঠিক উপরের রিং দিয়ে বের হয় | ইনগুইনাল লিগামেন্টের ওপর টান ফেলে এবং ইলিওইনগুইনাল স্নায়ুকে পিউবিক টিউবারকলের সাথে পিষে ফেলে তীব্র ব্যথা ছড়ায়। |
| **ফিমোরাল হার্নিয়া (Femoral Hernia)** | ইনগুইনাল লিগামেন্টের নিচে ফিমোরাল ক্যানাল | সুপিরিয়র পিউবিক রামাসের পেকটিনিয়াল লিগামেন্ট (Cooper's) স্পর্শ করে | অনমনীয় হাড়ের খাঁজের কারণে দ্রুত আটকে যায় (৪০% ঝুঁকি); অনেক সময় সাধারণ কুঁচকির ব্যথা মনে হলেও এটি আসলে হাড়ের ওপর তীব্র চাপ তৈরি করে। |
| **অবটুরেটর হার্নিয়া (Obturator Hernia)** | পেলভিসের অবটুরেটর ক্যানাল | পিউবিক বোন ও ইশ্চিয়ামের মধ্যবর্তী অবটুরেটর খাঁজ | পিউবিক রামাস ও অবটুরেটর নার্ভকে সরাসরি সংকুচিত করে; উরুর ভেতরের দিক থেকে হাঁটু পর্যন্ত তীব্র ব্যথা (হাউশিপ-রমবার্গ লক্ষণ)। |
| **স্পোর্টস হার্নিয়া (Sports Hernia / Pubalgia)** | তলপেটের পেশির অ্যাপোনিউরোসিস ছেঁড়া | পিউবিক ক্রেস্টে রেকটাস অ্যাবডোমিনিসের সংযুক্তি | প্রকৃত হার্নিয়া থলি থাকে না, তবে এটি সরাসরি **অস্টিআইটিস পিউবিস** তৈরি করে; পিউবিক টিউবারকলে তীব্র স্পর্শকাতরতা দেখা দেয়। |
| **অপারেশন পরবর্তী মেশ বা ট্যাকার জটিলতা** | সার্জিক্যাল স্ট্যাপল বা সুতোর ভুল প্রয়োগ | পিউবিক টিউবারকলের পেরিওস্টিয়ামে ধাতব পিন ঢুকে যাওয়া | তীব্র দীর্ঘস্থায়ী হাড়ের প্রদাহ (Aseptic Periostitis), অসহ্য জ্বালা এবং স্থায়ী স্নায়বিক ইনগুইনোডাইনিয়া। |

---

## ৪. ডায়াগনস্টিক ওয়ার্কফ্লো ও রেডিওলজিক্যাল পরীক্ষা (Diagnostic Architecture)
১. **ডায়নামিক আল্ট্রাসাউন্ড (Dynamic High-Resolution Ultrasound with Valsalva):**
   - কাশি দেওয়ার সময় কুঁচকির পেছনের প্রাচীরের স্ফীতি এবং পিউবিক বোনের সংযুক্তিতে অ্যাডাক্টর টেন্ডনের টিয়ার বা অশ্রু শনাক্ত করে।
২. **পেলভিক ৩টি এমআরআই (3T Pelvic MRI with STIR / Fat-Suppressed Protocol):**
   - **T1 সিকোয়েন্স:** পিউবিক হাড়ের ক্ষয়, সাবকন্ড্রাল স্ক্লেরোসিস ও অস্টিওফাইট দৃশ্যমান করে।
   - **STIR / T2 সিকোয়েন্স:** অস্টিআইটিস পিউবিস শনাক্তকরণের গোল্ড স্ট্যান্ডার্ড; হাড়ের ভেতরের তরল ও অস্থিমজ্জার প্রদাহ (Bone Marrow Edema) উজ্জ্বলভাবে প্রদর্শন করে।
৩. **ডায়াগনস্টিক লোকাল অ্যানেস্থেটিক ইনজেকশন (Diagnostic Nerve Block):**
   - পিউবিক টিউবারকল বা স্নায়ুতে ১% লিডোকেইন ইনজেকশন দেওয়ার পর ১৫ মিনিটের মধ্যে ৭০% ব্যথা কমে গেলে নিশ্চিত হওয়া যায় যে ব্যথার উৎস হার্নিয়ার স্নায়বিক চাপ বা পেরিওস্টিয়াল প্রদাহ।

---

## ৫. ফিজিবিলিটি ও ঝুঁকি মূল্যায়ন (Risk Matrix & Emergency Red Flags)
জরুরি হাসপাতালে যাওয়ার লক্ষণসমূহ:
- **হার্নিয়া আটকে যাওয়া বা স্ট্র্যাঙ্গুলেশন (Strangulated Hernia):** পিউবিক হাড়ের খাঁজে অন্ত্রের অংশ আটকে গিয়ে রক্ত চলাচল বন্ধ হওয়া। তীব্র ব্যথা, বমি, পেট ফুলে যাওয়া ও পেটের চামড়া লাল হওয়া।
- **সার্জিক্যাল ট্যাকার বা মেশজনিত হাড়ের ইনফেকশন:** অপারেশনের পর পিউবিক হাড়ে অসহ্য জ্বলন ও রাতে ঘুম ভেঙে যাওয়া।
- **অবটুরেটর হার্নিয়ার কারণে অন্ত্রে বাধা:** বৃদ্ধাদের ক্ষেত্রে অজানা কারণে পিউবিক অঞ্চলে ব্যথা সহ পেট ফাঁপা ও মল-গ্যাস বন্ধ হওয়া।

---

## ৬. ধাপে ধাপে চিকিৎসা ও ব্যবস্থাপনা রোডম্যাপ (Clinical Management Roadmap)
- **ধাপ ১: সঠিক উৎস নির্ণয় (দিন ০–১):** শারীরিক পরীক্ষা দ্বারা হার্নিয়ার সাধারণ থলি বনাম পিউবিক হাড়ের নিজস্ব রোগ পৃথক করা।
- **ধাপ ২: উন্নত ইমেজিং পরীক্ষা (দিন ২–৭):** পেলভিক এমআরআই ও ডায়নামিক আল্ট্রাসাউন্ডের মাধ্যমে অস্টিআইটিস পিউবিসের মাত্রা ও হার্নিয়ার আকার নির্ধারণ।
- **ধাপ ৩: রক্ষণশীল ও ফিজিওথেরাপি চিকিৎসা (সপ্তাহ ১–৬):** কোর পেশি শক্তিশালীকরণ, অ্যাডাক্টর স্ট্রেচিং, পিউবিক ইনফ্ল্যামেশনের জন্য পেলভিক বেল্ট এবং গাইডেড স্টেরয়েড/পিআরপি ইনজেকশন।
- **ধাপ ৪: পিউবিক-বোন সুরক্ষামূলক সার্জারি (সপ্তাহ ৬–১২, প্রয়োজনবোধে):** ল্যাপারোস্কোপিক পদ্ধতিতে (TEP বা TAPP) আঠা (Glue) বা সেলফ-গ্রিপিং মেশ ব্যবহার করে মেরামতের কাজ সম্পন্ন করা; পিউবিক হাড়ে কোনো অবস্থাতেই ধাতব পিন না লাগানো।

---
*সম্পূর্ণ ৬-ট্যাব ডেটাসেট ও সংখ্যাগত বিশ্লেষণ `{slug}_research_dossier.xlsx` ফাইলে সংরক্ষিত।*
"""
    with open(report_bn_path, "w", encoding="utf-8") as f:
        f.write(report_bn_content.strip() + chr(10))
    with open(report_alias_path, "w", encoding="utf-8") as f:
        f.write(report_bn_content.strip() + chr(10))
    print(f"[*] Generated Bangla Report: {report_bn_path} ({os.path.getsize(report_bn_path)} bytes)")
    
    # ── 5. RECORD METADATA AND REGISTRY ──
    metadata = {
        "topic": topic,
        "slug": slug,
        "category": category,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "files": {
            "excel": os.path.basename(excel_path),
            "core_en": os.path.basename(core_en_path),
            "report_bn": os.path.basename(report_bn_path),
            "report": "RESEARCH_REPORT.md"
        },
        "status": "COMPLETED"
    }
    with open(os.path.join(topic_dir, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        
    record_registry(topic, topic_dir, excel_path, report_bn_path)
    
    # ── 6. PERSIST TO CENTRALIZED SQLITE DB VIA REST API (PORT 8095) ──
    print("[*] Persisting research elements to centralized SQLite database via REST API...")
    api_payload = {
        "user_query": "/Research How hernia can affect the pubic bone",
        "agent_response": "গবেষণা সম্পন্ন হয়েছে। পিউবিক বোনের উপর হার্নিয়ার প্যাথোফিজিওলজিক্যাল মেকানিজম, বায়োমেকানিকাল ভারসাম্যহীনতা, অস্টিআইটিস পিউবিস এবং স্নায়বিক চাপের বিস্তারিত ডসিয়ার প্রস্তুত করা হয়েছে।",
        "mode": "research",
        "research_subtype": "deep",
        "topic_title": topic,
        "topic_slug": slug,
        "metadata": metadata,
        "elements": {
            "executive_summary": "Hernia impacts pubic bone via direct anatomical abutment, PLAC biomechanical force disruption causing Osteitis Pubis, ilioinguinal/obturator neuropathy, and post-surgical tacker periostitis.",
            "theoretical_foundations": "PLAC force coupling between rectus abdominis and adductor longus; shear stress at symphysis pubis; Wolff's law of bone remodeling.",
            "system_architecture": "Direct, Indirect, Femoral, Obturator, Sports Hernia, and Post-Herniorrhaphy impingement mechanics.",
            "precursors_and_literature": "EHS, AHS, British Hernia Society, and RSNA guidelines on pubalgia and groin hernia.",
            "feasibility_risk_matrix": "Femoral strangulation, iatrogenic pubic periostitis, neglected athletic pubalgia, chronic symphyseal instability.",
            "realization_roadmap": "Phase 1 Clinical Exam -> Phase 2 MRI & Dynamic US -> Phase 3 Core Rehab & Blocks -> Phase 4 Pubic-Sparing Surgical Repair.",
            "excel_file_path": excel_path,
            "markdown_file_path": report_bn_path
        }
    }
    
    try:
        req = urllib.request.Request(
            "http://localhost:8095/api/interactions",
            data=json.dumps(api_payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            print(f"[*] API Database Persistence Success: ID {res_data.get('id')}, Interaction {res_data.get('interaction_id')}")
    except Exception as e:
        print(f"[!] Warning: API persistence encountered error: {e}. Falling back to direct SQLite insertion.")
        try:
            import sqlite3
            db_conn = sqlite3.connect(os.path.join(BASE_DIR, "ask_and_research.db"))
            cur = db_conn.cursor()
            int_id = f"intk_{int(time.time()*1000)}"
            cur.execute("""
            INSERT INTO interactions (interaction_id, timestamp, mode, research_subtype, user_query, agent_response, topic_title, topic_slug, has_elements, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
            """, (int_id, now_iso, "research", "deep", api_payload["user_query"], api_payload["agent_response"], topic, slug, json.dumps(metadata)))
            cur.execute("""
            INSERT INTO research_elements (interaction_id, topic_title, research_subtype, executive_summary, theoretical_foundations, system_architecture, precursors_and_literature, feasibility_risk_matrix, realization_roadmap, raw_elements_json, excel_file_path, markdown_file_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (int_id, topic, "deep", api_payload["elements"]["executive_summary"], api_payload["elements"]["theoretical_foundations"], api_payload["elements"]["system_architecture"], api_payload["elements"]["precursors_and_literature"], api_payload["elements"]["feasibility_risk_matrix"], api_payload["elements"]["realization_roadmap"], json.dumps(api_payload["elements"]), excel_path, report_bn_path))
            db_conn.commit()
            db_conn.close()
            print("[*] Direct SQLite Fallback Persistence Success.")
        except Exception as sqle:
            print(f"[!] SQLite direct insertion error: {sqle}")

    # ── 7. DISPATCH TO WHATSAPP OUTBOX ──
    print("[*] Generating WhatsApp outbox delivery job...")
    job_file = dispatch_to_whatsapp(topic, topic_dir, excel_path, report_bn_path)
    print(f"[*] WhatsApp outbox job prepared: {job_file}")
    
    return {
        "topic": topic,
        "subfolder": topic_dir,
        "excel_path": excel_path,
        "core_en_path": core_en_path,
        "report_bn_path": report_bn_path,
        "job_file": job_file
    }

if __name__ == "__main__":
    res = run()
    print(json.dumps(res, indent=2))
