export type Lang = "en" | "hi";
interface Phrase {
  en: string;
  hi: string;
}

export const UI = {
  "app.name": { en: "Identity Rescue", hi: "Identity Rescue" },
  "app.tagline": {
    en: "See what to fix first",
    hi: "पहले क्या सुधारें, समझें",
  },
  "disclosure.global": {
    en: "Independent hackathon prototype · Fictional data · No government connection",
    hi: "स्वतंत्र हैकाथॉन प्रोटोटाइप · काल्पनिक डेटा · किसी सरकारी सिस्टम से जुड़ा नहीं",
  },
  "disclosure.sensitive": {
    en: "This is fictional demo data. Do not enter real Aadhaar, PAN, UAN, OTP or payment details.",
    hi: "यह काल्पनिक डेमो डेटा है। असली Aadhaar, PAN, UAN, OTP या भुगतान विवरण दर्ज न करें।",
  },
  "disclosure.sensitiveExtended": {
    en: "Fictional demo only — never enter Aadhaar, PAN, UAN, OTP, payment or document details.",
    hi: "केवल काल्पनिक डेमो — Aadhaar, PAN, UAN, OTP, भुगतान या दस्तावेज़ का विवरण कभी दर्ज न करें।",
  },
  "a11y.skip": { en: "Skip to main content", hi: "मुख्य सामग्री पर जाएँ" },
  "nav.home": { en: "All demo cases", hi: "सभी डेमो केस" },
  "nav.sources": { en: "Sources & limits", hi: "स्रोत और सीमाएँ" },
  "nav.sourcesShort": { en: "Sources", hi: "स्रोत" },
  "nav.privacy": { en: "Privacy", hi: "गोपनीयता" },
  "nav.language": { en: "Language", hi: "भाषा" },
  "nav.english": { en: "English", hi: "English" },
  "nav.hindi": { en: "हिन्दी", hi: "हिन्दी" },
  "home.eyebrow": {
    en: "A pre-flight debugger for public services",
    hi: "सार्वजनिक सेवाओं के लिए पहले से जाँच",
  },
  "home.title": {
    en: "Find what is blocking your government service",
    hi: "जानें कि आपकी सरकारी सेवा कहाँ रुक रही है",
  },
  "home.body": {
    en: "Choose the failed task, describe what happened, and run a fictional pre-flight check. We’ll identify the real blocker, compare fixes, and show the official next step.",
    hi: "रुका हुआ काम चुनें, बताएं कि क्या हुआ और काल्पनिक प्री-फ्लाइट जाँच चलाएँ। हम असली रुकावट, सुधार के विकल्प और आधिकारिक अगला कदम दिखाएँगे।",
  },
  "home.demoCue": {
    en: "For the 60-second journey, start with the Driving Licence case.",
    hi: "60 सेकंड की यात्रा के लिए Driving Licence केस से शुरू करें।",
  },
  "intake.goal": { en: "Service goal", hi: "सेवा का लक्ष्य" },
  "intake.failure": { en: "Failure message", hi: "दिखा हुआ संदेश" },
  "intake.failure.mismatch": { en: "Details do not match", hi: "विवरण मेल नहीं खाते" },
  "intake.failure.notFound": { en: "Record could not be found", hi: "रिकॉर्ड नहीं मिला" },
  "intake.failure.other": { en: "Something else happened", hi: "कोई दूसरी समस्या हुई" },
  "intake.describe": { en: "Describe what happened", hi: "बताएँ कि क्या हुआ" },
  "intake.describeHelp": {
    en: "Describe the problem only. Do not enter ID numbers or sensitive information.",
    hi: "केवल समस्या बताएँ। कोई ID नंबर या संवेदनशील जानकारी दर्ज न करें।",
  },
  "intake.profile": { en: "Fictional profile (for demo only)", hi: "काल्पनिक प्रोफ़ाइल (केवल डेमो)" },
  "intake.records": { en: "Records this demo will compare", hi: "इस डेमो में तुलना किए जाने वाले रिकॉर्ड" },
  "intake.included": { en: "Included", hi: "शामिल" },
  "intake.possible": { en: "Possible blocker", hi: "संभावित रुकावट" },
  "intake.goalNode": { en: "Selected goal", hi: "चुना हुआ लक्ष्य" },
  "intake.submit": { en: "Run pre-flight diagnosis", hi: "प्री-फ्लाइट जाँच चलाएँ" },
  "intake.next": { en: "Next: see the blocking record", hi: "अगला: रुकावट वाला रिकॉर्ड देखें" },
  "intake.routeTitle": { en: "Your service route", hi: "आपकी सेवा की राह" },
  "intake.resultTitle": { en: "Your result will show", hi: "परिणाम में यह दिखेगा" },
  "intake.result.blocker": { en: "Blocking record and field", hi: "रुकावट वाला रिकॉर्ड और फ़ील्ड" },
  "intake.result.blockerBody": { en: "Exactly what stops the selected task.", hi: "चुना हुआ काम ठीक कहाँ रुकता है।" },
  "intake.result.why": { en: "Why it matters", hi: "यह क्यों मायने रखता है" },
  "intake.result.whyBody": { en: "The rule, evidence and uncertainty.", hi: "नियम, प्रमाण और अनिश्चितता।" },
  "intake.result.routes": { en: "Correction routes", hi: "सुधार के रास्ते" },
  "intake.result.routesBody": { en: "The smallest safe options to compare.", hi: "तुलना के लिए कम असर वाले सुरक्षित विकल्प।" },
  "intake.result.destination": { en: "Official destination", hi: "आधिकारिक स्थान" },
  "intake.result.destinationBody": { en: "Where to verify and act next.", hi: "अगली जाँच और कार्रवाई कहाँ करें।" },
  "intake.record.aadhaar": { en: "Aadhaar-linked identity", hi: "Aadhaar से जुड़ी पहचान" },
  "intake.record.dl": { en: "Driving Licence issuer record", hi: "Driving Licence जारीकर्ता रिकॉर्ड" },
  "intake.record.epfo": { en: "Fictional EPFO service history", hi: "काल्पनिक EPFO सेवा रिकॉर्ड" },
  "intake.record.pan": { en: "Fictional PAN display record", hi: "काल्पनिक PAN रिकॉर्ड" },
  "intake.route.identity": { en: "Aadhaar-linked identity", hi: "Aadhaar से जुड़ी पहचान" },
  "intake.route.transport": { en: "Transport issuer record", hi: "Transport जारीकर्ता रिकॉर्ड" },
  "intake.route.digilocker": { en: "DigiLocker retrieval", hi: "DigiLocker retrieval" },
  "intake.route.epfo": { en: "EPFO service history", hi: "EPFO सेवा रिकॉर्ड" },
  "intake.route.pfGoal": { en: "PF / KYC pre-flight", hi: "PF / KYC प्री-फ्लाइट" },
  "intake.route.chosenName": { en: "Chosen current name", hi: "चुना हुआ वर्तमान नाम" },
  "intake.route.reconcile": { en: "DL reconciliation goal", hi: "DL मिलान लक्ष्य" },
  "intake.error.short": { en: "Add a little more detail so the problem is clear.", hi: "समस्या स्पष्ट करने के लिए थोड़ा और विवरण दें।" },
  "intake.error.sensitive": { en: "Remove ID, OTP or other long numbers before continuing.", hi: "आगे बढ़ने से पहले ID, OTP या लंबे नंबर हटाएँ।" },
  "intake.contextLabel": { en: "WHAT YOU DESCRIBED", hi: "आपने जो बताया" },
  "intake.contextTitle": { en: "Problem context", hi: "समस्या का संदर्भ" },
  "intake.contextLimit": {
    en: "This browser-only note provides context. It cannot change the deterministic diagnosis.",
    hi: "यह नोट केवल इसी browser में संदर्भ के लिए है। यह deterministic जाँच का परिणाम नहीं बदल सकता।",
  },
  "scenario.fictional": { en: "FICTIONAL CASE", hi: "काल्पनिक केस" },
  "scenario.try": { en: "Try this case", hi: "यह केस आज़माएँ" },
  "scenario.coming": {
    en: "Being completed in the next build slice",
    hi: "अगले बिल्ड चरण में पूरा हो रहा है",
  },
  "scenario.dl.title": {
    en: "I can't fetch my Driving Licence",
    hi: "मैं अपना Driving Licence नहीं ला पा रहा/रही हूँ",
  },
  "scenario.dl.body": {
    en: "Trace a name mismatch across a mock Aadhaar and Driving Licence record.",
    hi: "काल्पनिक Aadhaar और Driving Licence रिकॉर्ड में नाम का अंतर समझें।",
  },
  "scenario.epfo.title": {
    en: "My PF/KYC issue isn't getting resolved",
    hi: "मेरी PF/KYC समस्या हल नहीं हो रही",
  },
  "scenario.epfo.body": {
    en: "Separate a visible identity difference from the real blocker.",
    hi: "दिखने वाले पहचान अंतर को असली रुकावट से अलग करें।",
  },
  "scenario.life.title": {
    en: "My name or address changed",
    hi: "मेरा नाम या पता बदल गया है",
  },
  "scenario.life.body": {
    en: "See which fictional record to update first and what it could affect.",
    hi: "समझें कि पहले कौन-सा काल्पनिक रिकॉर्ड बदलना है और उसका क्या असर हो सकता है।",
  },
  "case.demoData": { en: "DEMO / FICTIONAL DATA", hi: "डेमो / काल्पनिक डेटा" },
  "case.profile": { en: "Fictional profile", hi: "काल्पनिक प्रोफ़ाइल" },
  "case.goal": {
    en: "Goal: fetch a Driving Licence in DigiLocker",
    hi: "लक्ष्य: DigiLocker में Driving Licence प्राप्त करना",
  },
  "case.goal.dl": {
    en: "Goal: fetch a Driving Licence in DigiLocker",
    hi: "लक्ष्य: DigiLocker में Driving Licence प्राप्त करना",
  },
  "case.goal.epfo": {
    en: "Goal: understand why this fictional PF/KYC task is blocked",
    hi: "लक्ष्य: समझें कि यह काल्पनिक PF/KYC काम क्यों रुका है",
  },
  "case.goal.life": {
    en: "Goal: make the fictional DL path use the chosen current name",
    hi: "लक्ष्य: काल्पनिक DL प्रक्रिया में चुना हुआ वर्तमान नाम मिलाना",
  },
  "case.progress": { en: "Case progress", hi: "केस की प्रगति" },
  "progress.understand": { en: "Understand", hi: "समझें" },
  "progress.start": { en: "Start your check", hi: "जाँच शुरू करें" },
  "progress.start.help": { en: "Choose goal and describe", hi: "लक्ष्य चुनें और बताएँ" },
  "progress.diagnose": { en: "Diagnose blocker", hi: "रुकावट पहचानें" },
  "progress.diagnose.help": { en: "Find the real blocker", hi: "असली रुकावट खोजें" },
  "progress.compare": { en: "Compare", hi: "विकल्प देखें" },
  "progress.compare.help": { en: "See the safest options", hi: "सुरक्षित विकल्प देखें" },
  "progress.simulate": { en: "Simulate", hi: "डेमो करें" },
  "progress.next": { en: "Next action", hi: "अगला कदम" },
  "progress.next.help": { en: "Go to the official source", hi: "आधिकारिक स्रोत पर जाएँ" },
  "status.result": {
    en: "SIMULATED PREFLIGHT RESULT",
    hi: "सिम्युलेटेड प्री-फ्लाइट परिणाम",
  },
  "status.BLOCKED": { en: "Blocked", hi: "रुका हुआ" },
  "status.READY_SIMULATION": {
    en: "Ready in this simulation",
    hi: "इस डेमो में तैयार",
  },
  "status.NEEDS_REVIEW": { en: "Needs review", hi: "जाँच ज़रूरी" },
  "status.NOT_IDENTITY_ISSUE": {
    en: "Not an identity-data issue",
    hi: "पहचान डेटा की समस्या नहीं",
  },
  "diagnosis.dl.blocked": {
    en: "Blocked by one record mismatch",
    hi: "एक रिकॉर्ड अंतर के कारण प्रक्रिया रुकी है",
  },
  "diagnosis.dl.blocked_explanation": {
    en: "The Aadhaar-linked name and the mock Driving Licence source name do not reconcile for this retrieval rule.",
    hi: "इस retrieval नियम में Aadhaar से जुड़ा नाम और काल्पनिक Driving Licence स्रोत का नाम मेल नहीं खाते।",
  },
  "diagnosis.dl.ready": {
    en: "The blocking record now reconciles",
    hi: "रुकावट वाला रिकॉर्ड अब मेल खाता है",
  },
  "diagnosis.dl.ready_explanation": {
    en: "The modeled retrieval rules now pass. No government record was contacted or changed.",
    hi: "डेमो के retrieval नियम अब पास होते हैं। किसी सरकारी रिकॉर्ड से संपर्क या बदलाव नहीं हुआ।",
  },
  "diagnosis.epfo.blocked": {
    en: "The visible name difference is not the blocker",
    hi: "दिखने वाला नाम अंतर असली रुकावट नहीं है",
  },
  "diagnosis.epfo.blocked_explanation": {
    en: "Changing the name would not fix this fictional claim. The service-history date is the causal blocker in this simulation.",
    hi: "नाम बदलने से यह काल्पनिक claim ठीक नहीं होगा। इस डेमो में service-history की तारीख असली रुकावट है।",
  },
  "diagnosis.epfo.ready": {
    en: "The service-history condition now passes",
    hi: "service-history की शर्त अब पूरी होती है",
  },
  "diagnosis.epfo.ready_explanation": {
    en: "The fictional exit date now passes the modeled pre-flight. The visible name variation remains compatible here.",
    hi: "काल्पनिक exit date अब डेमो pre-flight पास करती है। दिखने वाला नाम अंतर यहाँ अनुकूल है।",
  },
  "diagnosis.life.blocked": {
    en: "One targeted name correction is enough",
    hi: "एक लक्षित नाम सुधार पर्याप्त है",
  },
  "diagnosis.life.blocked_explanation": {
    en: "The chosen current name and the fictional DL source name differ. The address difference does not block this selected goal.",
    hi: "चुना हुआ वर्तमान नाम और काल्पनिक DL स्रोत का नाम अलग है। पता अंतर इस लक्ष्य को नहीं रोकता।",
  },
  "diagnosis.life.ready": {
    en: "The minimum correction sequence is complete",
    hi: "न्यूनतम सुधार क्रम पूरा हुआ",
  },
  "diagnosis.life.ready_explanation": {
    en: "The selected DL name dependency now passes. Earlier PAN and address values remain visible but were not changed unnecessarily.",
    hi: "चुनी गई DL नाम निर्भरता अब पास है। पुराने PAN और पते के मान दिखते हैं, लेकिन उन्हें बिना ज़रूरत नहीं बदला गया।",
  },
  "diagnosis.next.compare": {
    en: "Compare the available correction routes.",
    hi: "उपलब्ध सुधार विकल्पों की तुलना करें।",
  },
  "diagnosis.next.official": {
    en: "Review the official next action.",
    hi: "आधिकारिक अगला कदम देखें।",
  },
  "diagnosis.compare": {
    en: "Compare ways to fix this",
    hi: "सुधार के विकल्प देखें",
  },
  "diagnosis.evidence": { en: "Show the evidence", hi: "वजह और रिकॉर्ड देखें" },
  "diagnosis.records": {
    en: "Records used for this result",
    hi: "इस परिणाम में उपयोग किए गए रिकॉर्ड",
  },
  "diagnosis.trail": {
    en: "Why this task is blocked",
    hi: "यह काम क्यों रुका है",
  },
  "record.fictional": { en: "FICTIONAL RECORD", hi: "काल्पनिक रिकॉर्ड" },
  "field.name": { en: "Name as stored", hi: "रिकॉर्ड में नाम" },
  "field.dob": { en: "Date of birth", hi: "जन्म तिथि" },
  "field.record_present": { en: "Record available", hi: "रिकॉर्ड उपलब्ध" },
  "field.address": { en: "Address as stored", hi: "रिकॉर्ड में पता" },
  "field.aadhaar_linked": { en: "Aadhaar linked", hi: "Aadhaar जुड़ा है" },
  "field.pan_linked": { en: "PAN linked", hi: "PAN जुड़ा है" },
  "field.date_of_exit": { en: "Date of exit", hi: "नौकरी छोड़ने की तारीख" },
  "field.last_contribution_month": {
    en: "Last contribution month",
    hi: "अंतिम contribution महीना",
  },
  "field.claim_attempt_date": {
    en: "Claim attempt date",
    hi: "claim कोशिश की तारीख",
  },
  "field.kyc_status": { en: "KYC status", hi: "KYC स्थिति" },
  "finding.MATCH_EXACT": { en: "Exact match", hi: "पूरी तरह मेल" },
  "finding.MATCH_RULE_COMPATIBLE": {
    en: "Compatible for this rule",
    hi: "इस नियम में अनुकूल",
  },
  "finding.MISMATCH_BLOCKING": {
    en: "Blocks this task",
    hi: "इसी वजह से काम रुक रहा है",
  },
  "finding.NON_IDENTITY_BLOCKER": {
    en: "Not an identity issue",
    hi: "पहचान की समस्या नहीं",
  },
  "finding.VARIANT_NON_BLOCKING": {
    en: "Different, but not the blocker",
    hi: "जानकारी अलग है, लेकिन काम नहीं रोक रही",
  },
  "finding.MISMATCH_REVIEW": {
    en: "Needs official review",
    hi: "आधिकारिक जाँच ज़रूरी",
  },
  "finding.dl.record_present.title": {
    en: "Issuer record is available",
    hi: "स्रोत रिकॉर्ड उपलब्ध है",
  },
  "finding.dl.record_present.pass": {
    en: "The fictional DL record exists in the modeled issuer source.",
    hi: "काल्पनिक DL रिकॉर्ड डेमो स्रोत में मौजूद है।",
  },
  "finding.dl.name.block_title": {
    en: "The name representations do not reconcile",
    hi: "नाम के रूप आपस में मेल नहीं खाते",
  },
  "finding.dl.name.block": {
    en: "The same tokens appear in a representation and order this mock retrieval rule does not accept.",
    hi: "नाम के शब्द ऐसे रूप और क्रम में हैं, जिसे यह डेमो retrieval नियम स्वीकार नहीं करता।",
  },
  "finding.dl.name.pass_title": {
    en: "The name representations reconcile",
    hi: "नाम के रूप अब मेल खाते हैं",
  },
  "finding.dl.name.pass": {
    en: "The controlled initial relation and token order now pass the configured rule.",
    hi: "नियंत्रित initial संबंध और शब्द क्रम अब डेमो नियम पास करते हैं।",
  },
  "finding.dl.name.uncertainty": {
    en: "The real issuer may apply additional checks that this prototype does not model.",
    hi: "वास्तविक स्रोत अतिरिक्त जाँच कर सकता है, जिन्हें यह प्रोटोटाइप मॉडल नहीं करता।",
  },
  "finding.dl.dob.title": {
    en: "Dates of birth match",
    hi: "जन्म तिथियाँ मेल खाती हैं",
  },
  "finding.dl.dob.pass": {
    en: "Both fictional records contain the same date.",
    hi: "दोनों काल्पनिक रिकॉर्ड में एक ही तिथि है।",
  },
  "finding.dl.dob.block": {
    en: "The dates differ in this demo.",
    hi: "इस डेमो में तिथियाँ अलग हैं।",
  },
  "finding.dl.dob.uncertainty": {
    en: "Date equality is a prototype rule for this case.",
    hi: "तिथि का पूरा मेल इस केस का डेमो नियम है।",
  },
  "finding.epfo.name.title": {
    en: "The names look different",
    hi: "नाम अलग दिखते हैं",
  },
  "finding.epfo.name.nonblocking": {
    en: "The explicit N → NARAYAN relation makes these fictional name forms compatible for this scenario. It is not the cause of the failure.",
    hi: "इस काल्पनिक प्रोफ़ाइल में स्पष्ट N → NARAYAN संबंध के कारण नाम अनुकूल हैं। यह विफलता की वजह नहीं है।",
  },
  "finding.epfo.name.review": {
    en: "The available relation is not enough to decide this name difference.",
    hi: "उपलब्ध संबंध से इस नाम अंतर का निर्णय नहीं हो सकता।",
  },
  "finding.epfo.name.uncertainty": {
    en: "This controlled relation applies only to this fictional profile.",
    hi: "यह नियंत्रित संबंध केवल इस काल्पनिक प्रोफ़ाइल पर लागू है।",
  },
  "finding.epfo.dob.title": {
    en: "Dates of birth match",
    hi: "जन्म तिथियाँ मेल खाती हैं",
  },
  "finding.epfo.dob.pass": {
    en: "The modeled records use the same date of birth.",
    hi: "डेमो रिकॉर्ड में एक ही जन्म तिथि है।",
  },
  "finding.epfo.history.block_title": {
    en: "The service-history date blocks this task",
    hi: "service-history की तारीख यह काम रोकती है",
  },
  "finding.epfo.history.block": {
    en: "The fictional date of exit is after the claim-attempt date, so this demo rule fails before identity matching matters.",
    hi: "काल्पनिक exit date claim कोशिश की तारीख के बाद है, इसलिए पहचान मिलान से पहले ही यह डेमो नियम विफल होता है।",
  },
  "finding.epfo.history.pass_title": {
    en: "The service-history condition passes",
    hi: "service-history की शर्त पूरी है",
  },
  "finding.epfo.history.pass": {
    en: "The fictional date sequence now passes the configured demo rule.",
    hi: "काल्पनिक तारीख क्रम अब डेमो नियम पास करता है।",
  },
  "finding.epfo.history.uncertainty": {
    en: "This exact date predicate is a prototype simulation, not EPFO's production claim logic.",
    hi: "यह सटीक तारीख नियम प्रोटोटाइप simulation है, EPFO का वास्तविक claim logic नहीं।",
  },
  "finding.life.target.block_title": {
    en: "The DL source still uses the earlier name",
    hi: "DL स्रोत में अभी पुराना नाम है",
  },
  "finding.life.target.block": {
    en: "The selected retrieval goal depends on the chosen current name and the fictional DL source name reconciling.",
    hi: "चुने हुए retrieval लक्ष्य में वर्तमान नाम और काल्पनिक DL स्रोत का नाम मिलना ज़रूरी है।",
  },
  "finding.life.target.pass_title": {
    en: "The selected name dependency passes",
    hi: "चुनी हुई नाम निर्भरता पूरी है",
  },
  "finding.life.target.pass": {
    en: "The fictional DL source now uses the citizen's chosen current name.",
    hi: "काल्पनिक DL स्रोत अब नागरिक का चुना हुआ वर्तमान नाम उपयोग करता है।",
  },
  "finding.life.target.uncertainty": {
    en: "The actual authority may require additional evidence or checks not modeled here.",
    hi: "वास्तविक authority अतिरिक्त प्रमाण या जाँच माँग सकती है, जिन्हें यहाँ मॉडल नहीं किया गया।",
  },
  "finding.life.pan.title": {
    en: "The PAN demo still uses the earlier name",
    hi: "PAN डेमो में अभी पुराना नाम है",
  },
  "finding.life.pan.nonblocking": {
    en: "That difference is outside this selected DL retrieval goal, so the minimum plan does not change it.",
    hi: "यह अंतर चुने गए DL retrieval लक्ष्य से बाहर है, इसलिए न्यूनतम plan इसे नहीं बदलता।",
  },
  "finding.life.address.title": {
    en: "The DL address also differs",
    hi: "DL का पता भी अलग है",
  },
  "finding.life.address.nonblocking": {
    en: "This selected goal depends on the name, not address, so the planner leaves it unchanged.",
    hi: "यह लक्ष्य नाम पर निर्भर है, पते पर नहीं, इसलिए planner इसे नहीं बदलता।",
  },
  "evidence.title": {
    en: "Why we reached this result",
    hi: "हम इस परिणाम तक क्यों पहुँचे",
  },
  "evidence.rule": { en: "Rule", hi: "नियम" },
  "evidence.inputs": { en: "Evidence used", hi: "उपयोग किए गए रिकॉर्ड" },
  "evidence.source": { en: "Source basis", hi: "स्रोत आधार" },
  "evidence.limit": { en: "Prototype limitation", hi: "प्रोटोटाइप सीमा" },
  "evidence.ruleId": { en: "Deterministic rule", hi: "निर्धारित नियम" },
  "options.title": {
    en: "Compare correction routes",
    hi: "सुधार के विकल्पों की तुलना करें",
  },
  "options.body": {
    en: "The planner recommends the lowest-cost route within this fictional rule set. It is not an official instruction.",
    hi: "प्लानर इस काल्पनिक नियम समूह में कम असर वाला रास्ता सुझाता है। यह आधिकारिक निर्देश नहीं है।",
  },
  "options.recommended": {
    en: "Recommended in this simulation",
    hi: "इस डेमो में सुझाया गया",
  },
  "options.alternative": { en: "Broader alternative", hi: "व्यापक विकल्प" },
  "options.change": { en: "What changes", hi: "क्या बदलेगा" },
  "options.effect": { en: "What it does", hi: "इससे क्या होगा" },
  "options.impact": {
    en: "What else may be affected",
    hi: "और कहाँ असर हो सकता है",
  },
  "options.effort": { en: "Route", hi: "प्रक्रिया" },
  "options.cost": { en: "Configured demo cost", hi: "डेमो में तय लागत" },
  "options.simulate": {
    en: "Simulate this route",
    hi: "इस विकल्प को डेमो में आज़माएँ",
  },
  "action.a1.title": {
    en: "Align the fictional DL source name",
    hi: "काल्पनिक DL स्रोत का नाम मिलाएँ",
  },
  "action.a1.effect": {
    en: "Resolves the modeled DigiLocker/DL name reconciliation blocker.",
    hi: "डेमो DigiLocker/DL नाम रुकावट को हल करता है।",
  },
  "action.a1.impact": {
    en: "Introduces no new conflict in the records modeled here.",
    hi: "यहाँ मॉडल किए गए रिकॉर्ड में कोई नई रुकावट नहीं बनती।",
  },
  "action.a2.title": {
    en: "Expand the fictional Aadhaar name",
    hi: "काल्पनिक Aadhaar नाम को पूरा लिखें",
  },
  "action.a2.effect": {
    en: "Changes a broadly reused upstream record but does not fix the token order by itself.",
    hi: "व्यापक रूप से उपयोग होने वाला ऊपर का रिकॉर्ड बदलता है, लेकिन अकेले शब्द क्रम की समस्या हल नहीं करता।",
  },
  "action.a2.impact": {
    en: "Needs official review and may affect more downstream services.",
    hi: "आधिकारिक जाँच चाहिए और अन्य सेवाओं पर अधिक असर हो सकता है।",
  },
  "action.b_name.title": {
    en: "Align the fictional PAN display name",
    hi: "काल्पनिक PAN नाम को मिलाएँ",
  },
  "action.b_name.effect": {
    en: "Removes the visible name variation but does not fix the service-history blocker.",
    hi: "दिखने वाला नाम अंतर हटता है, लेकिन service-history की रुकावट ठीक नहीं होती।",
  },
  "action.b_name.impact": {
    en: "Adds effort without making this selected task ready.",
    hi: "मेहनत बढ़ती है, लेकिन चुना हुआ काम तैयार नहीं होता।",
  },
  "action.b1.title": {
    en: "Correct the fictional service-history date",
    hi: "काल्पनिक service-history तारीख सुधारें",
  },
  "action.b1.effect": {
    en: "Resolves the causal date sequence in this simulation.",
    hi: "इस डेमो में असली तारीख क्रम की रुकावट हल होती है।",
  },
  "action.b1.impact": {
    en: "Leaves the compatible name representations unchanged.",
    hi: "अनुकूल नाम रिकॉर्ड बिना बदलाव रहते हैं।",
  },
  "action.c1.title": {
    en: "Use the chosen current name in the fictional DL source",
    hi: "काल्पनिक DL स्रोत में चुना हुआ वर्तमान नाम रखें",
  },
  "action.c1.effect": {
    en: "Resolves the selected DL name dependency with one change.",
    hi: "एक बदलाव से चुनी हुई DL नाम निर्भरता हल होती है।",
  },
  "action.c1.impact": {
    en: "Leaves the unrelated address and PAN record untouched.",
    hi: "असंबंधित पता और PAN रिकॉर्ड बिना बदलाव रहते हैं।",
  },
  "action.c2.title": {
    en: "Also change the fictional PAN name",
    hi: "काल्पनिक PAN नाम भी बदलें",
  },
  "action.c2.effect": {
    en: "Improves broader consistency but is not required for the selected DL goal.",
    hi: "व्यापक समानता बढ़ती है, लेकिन चुने हुए DL लक्ष्य के लिए ज़रूरी नहीं।",
  },
  "action.c2.impact": {
    en: "Adds an unnecessary second authority route for this goal.",
    hi: "इस लक्ष्य के लिए बिना ज़रूरत दूसरी authority प्रक्रिया जुड़ती है।",
  },
  "action.c3.title": {
    en: "Also change the fictional DL address",
    hi: "काल्पनिक DL पता भी बदलें",
  },
  "action.c3.effect": {
    en: "Changes address data that this selected name-only goal does not use.",
    hi: "ऐसा पता बदलता है जिसे चुना हुआ केवल-नाम लक्ष्य उपयोग नहीं करता।",
  },
  "action.c3.impact": {
    en: "Broadens the change without improving target readiness.",
    hi: "लक्ष्य की तैयारी सुधारे बिना बदलाव बढ़ता है।",
  },
  "effort.issuer": {
    en: "Issuer / official record correction",
    hi: "स्रोत / आधिकारिक रिकॉर्ड सुधार",
  },
  "effort.review": {
    en: "Aadhaar update / review",
    hi: "Aadhaar अपडेट / जाँच",
  },
  "effort.employer": {
    en: "Employer / EPFO service-history action",
    hi: "Employer / EPFO service-history प्रक्रिया",
  },
  "dialog.title": {
    en: "Simulate this correction?",
    hi: "इस सुधार को डेमो में आज़माएँ?",
  },
  "dialog.body": {
    en: "This changes only the fictional case in your browser. No government record will be contacted or updated.",
    hi: "यह केवल आपके ब्राउज़र के काल्पनिक केस को बदलता है। किसी सरकारी रिकॉर्ड से संपर्क या बदलाव नहीं होगा।",
  },
  "dialog.confirm": { en: "Simulate correction", hi: "सुधार का डेमो करें" },
  "dialog.cancel": { en: "Cancel", hi: "रद्द करें" },
  "result.title": {
    en: "The simulated blocker is resolved",
    hi: "डेमो की रुकावट हल हो गई",
  },
  "result.changed": {
    en: "What changed in this demo",
    hi: "इस डेमो में क्या बदला",
  },
  "result.before": { en: "Before", hi: "पहले" },
  "result.after": { en: "After", hi: "बाद में" },
  "result.undo": {
    en: "Undo last simulation",
    hi: "पिछला डेमो बदलाव वापस लें",
  },
  "result.noRealChange": {
    en: "No official record was changed",
    hi: "किसी आधिकारिक रिकॉर्ड में बदलाव नहीं हुआ",
  },
  "handoff.dl.title": { en: "What you would do next", hi: "अब आगे क्या करें" },
  "handoff.dl.step1": {
    en: "Open the official service for the record that needs review or correction.",
    hi: "जिस रिकॉर्ड की जाँच या सुधार चाहिए, उसकी आधिकारिक सेवा खोलें।",
  },
  "handoff.dl.step2": {
    en: "Confirm the current correction route and requirements on that official service.",
    hi: "वर्तमान सुधार प्रक्रिया और आवश्यकताएँ आधिकारिक सेवा पर जाँचें।",
  },
  "handoff.dl.step3": {
    en: "After the official record changes, retry the DigiLocker retrieval.",
    hi: "आधिकारिक रिकॉर्ड बदलने के बाद DigiLocker retrieval फिर आज़माएँ।",
  },
  "handoff.processes_change": {
    en: "Processes can change. Check the linked official service before acting.",
    hi: "प्रक्रियाएँ बदल सकती हैं। कदम उठाने से पहले लिंक की गई आधिकारिक सेवा जाँचें।",
  },
  "handoff.open": { en: "Open official source", hi: "आधिकारिक स्रोत खोलें" },
  "handoff.epfo.title": {
    en: "What you would do next",
    hi: "अब आगे क्या करें",
  },
  "handoff.epfo.step1": {
    en: "Review the service-history and date-of-exit guidance on the official EPFO source.",
    hi: "आधिकारिक EPFO स्रोत पर service-history और exit date मार्गदर्शन देखें।",
  },
  "handoff.epfo.step2": {
    en: "Use the current employer/member route specified by EPFO for the actual record.",
    hi: "वास्तविक रिकॉर्ड के लिए EPFO की वर्तमान employer/member प्रक्रिया उपयोग करें।",
  },
  "handoff.epfo.step3": {
    en: "Retry the relevant official task only after the official history is corrected.",
    hi: "आधिकारिक history सुधरने के बाद ही संबंधित काम फिर आज़माएँ।",
  },
  "handoff.life.title": {
    en: "What you would do next",
    hi: "अब आगे क्या करें",
  },
  "handoff.life.step1": {
    en: "Open the official service for the fictional DL source represented in this plan.",
    hi: "इस plan में दिखाए गए काल्पनिक DL स्रोत की आधिकारिक सेवा खोलें।",
  },
  "handoff.life.step2": {
    en: "Confirm the authority's current name-change evidence and process requirements.",
    hi: "authority की वर्तमान नाम-सुधार प्रमाण और प्रक्रिया आवश्यकताएँ जाँचें।",
  },
  "handoff.life.step3": {
    en: "Retry DigiLocker retrieval after the official issuer record is actually updated.",
    hi: "आधिकारिक issuer रिकॉर्ड सच में बदलने के बाद DigiLocker retrieval फिर आज़माएँ।",
  },
  "trail.dl.1": {
    en: "You want to fetch your Driving Licence.",
    hi: "आप अपना Driving Licence प्राप्त करना चाहते हैं।",
  },
  "trail.dl.2": {
    en: "DigiLocker asks the issuer source for the record.",
    hi: "DigiLocker स्रोत से रिकॉर्ड माँगता है।",
  },
  "trail.dl.3": {
    en: "This retrieval uses the Aadhaar-linked name.",
    hi: "इस retrieval में Aadhaar से जुड़ा नाम उपयोग होता है।",
  },
  "trail.dl.4": {
    en: "The fictional issuer record represents the name differently.",
    hi: "काल्पनिक स्रोत रिकॉर्ड नाम को अलग रूप में दिखाता है।",
  },
  "trail.dl.5": {
    en: "In this demo rule, that difference blocks retrieval.",
    hi: "इस डेमो नियम में यह अंतर retrieval रोकता है।",
  },
  "trail.epfo.1": {
    en: "You want to understand a blocked PF/KYC task.",
    hi: "आप रुके हुए PF/KYC काम की वजह समझना चाहते हैं।",
  },
  "trail.epfo.2": {
    en: "The name forms differ but have an explicit fictional initial relation.",
    hi: "नाम अलग दिखते हैं, लेकिन काल्पनिक initial संबंध स्पष्ट है।",
  },
  "trail.epfo.3": {
    en: "The claim-attempt date comes before the fictional exit date.",
    hi: "claim कोशिश की तारीख काल्पनिक exit date से पहले है।",
  },
  "trail.epfo.4": {
    en: "The service-history condition—not the name—is the causal blocker.",
    hi: "service-history की शर्त—नाम नहीं—असली रुकावट है।",
  },
  "trail.life.1": {
    en: "The citizen has chosen MEERA NAIR as the current name.",
    hi: "नागरिक ने MEERA NAIR को वर्तमान नाम चुना है।",
  },
  "trail.life.2": {
    en: "The selected goal is the fictional DL retrieval path.",
    hi: "चुना हुआ लक्ष्य काल्पनिक DL retrieval प्रक्रिया है।",
  },
  "trail.life.3": {
    en: "Only the DL name blocks that selected goal.",
    hi: "केवल DL नाम चुना हुआ लक्ष्य रोकता है।",
  },
  "trail.life.4": {
    en: "PAN name and DL address remain outside the minimum plan.",
    hi: "PAN नाम और DL पता न्यूनतम plan से बाहर रहते हैं।",
  },
  "records.other": {
    en: "See other affected fictional records",
    hi: "अन्य प्रभावित काल्पनिक रिकॉर्ड देखें",
  },
  "result.remaining": {
    en: "Still different, but not blocking this selected goal",
    hi: "अभी अलग है, लेकिन चुना हुआ लक्ष्य नहीं रोकता",
  },
  "sources.title": {
    en: "Sources and prototype limits",
    hi: "स्रोत और प्रोटोटाइप सीमाएँ",
  },
  "sources.body": {
    en: "Official sources support the public dependency or process. Exact predicates and simulations are labeled when they are prototype choices.",
    hi: "आधिकारिक स्रोत सार्वजनिक निर्भरता या प्रक्रिया का आधार देते हैं। सटीक डेमो नियम और simulation को प्रोटोटाइप विकल्प बताया गया है।",
  },
  "sources.checked": { en: "Last checked", hi: "अंतिम जाँच" },
  "sources.proposition": {
    en: "What this source supports",
    hi: "यह स्रोत किस बात का आधार है",
  },
  "sources.external": {
    en: "Open official source (new tab)",
    hi: "आधिकारिक स्रोत खोलें (नई टैब)",
  },
  "privacy.title": {
    en: "Privacy by not collecting",
    hi: "डेटा न लेकर गोपनीयता",
  },
  "privacy.body": {
    en: "Identity Rescue uses only bundled fictional profiles. It has no field for real Aadhaar, PAN, UAN, OTP, payment, biometric or identity documents.",
    hi: "Identity Rescue केवल पहले से बने काल्पनिक प्रोफ़ाइल उपयोग करता है। इसमें असली Aadhaar, PAN, UAN, OTP, भुगतान, biometric या पहचान दस्तावेज़ दर्ज करने की जगह नहीं है।",
  },
  "privacy.ai": {
    en: "The deterministic journey does not require AI. Any future AI explanation receives only a bounded fictional evidence packet.",
    hi: "निर्धारित यात्रा के लिए AI ज़रूरी नहीं है। भविष्य की AI व्याख्या को केवल सीमित काल्पनिक evidence packet मिलेगा।",
  },
  "common.back": { en: "Back", hi: "पीछे" },
  "common.reset": { en: "Reset demo", hi: "डेमो रीसेट करें" },
  "common.loading": {
    en: "Checking the fictional records…",
    hi: "काल्पनिक रिकॉर्ड जाँचे जा रहे हैं…",
  },
  "common.error": {
    en: "This demo case could not load. No government system was contacted. Please reset and try again.",
    hi: "यह डेमो केस लोड नहीं हुआ। किसी सरकारी सिस्टम से संपर्क नहीं हुआ। रीसेट करके फिर आज़माएँ।",
  },
  "common.yes": { en: "Yes", hi: "हाँ" },
  "common.no": { en: "No", hi: "नहीं" },
} as const satisfies Record<string, Phrase>;

export type UiKey = keyof typeof UI;
export function phrase(key: string, lang: Lang): string {
  return (UI as Record<string, Phrase>)[key]?.[lang] ?? key;
}
