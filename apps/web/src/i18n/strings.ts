/**
 * Interface chrome, in both languages.
 *
 * What is *not* here: the disclosure banner, the "what this is" text, the no-real-
 * data warning, the scope statement, what a confirmation means, the acknowledgement
 * caveat, the policy anchor, and every error message. All of those come from the API
 * (`app/copy.py`, `app/errors.py`) and are rendered verbatim, so there is exactly one
 * authoritative wording and `apps/api/tests/test_copy_lint.py` can assert it once and
 * cover every screen. A stale frontend bundle still shows the current disclosure.
 *
 * What is here: button labels, headings, field labels and step names -- copy that
 * describes the interface rather than making a claim about the world.
 *
 * Every entry has both languages. A missing Hindi string is a bug, not a fallback:
 * `t()` is typed so it cannot be called with a key that lacks one.
 */

import type { Lang } from "../api/types";

export interface Phrase {
  en: string;
  hi: string;
}

export const UI = {
  "app.name": { en: "Handover29C", hi: "Handover29C" },
  "app.tagline": {
    en: "Hand a registered vehicle to an authorised dealer, with both sides agreeing to the same details.",
    hi: "पंजीकृत वाहन किसी अधिकृत डीलर को सौंपें, जहाँ दोनों पक्ष समान विवरण पर सहमत हों।",
  },

  "a11y.skipToMain": { en: "Skip to main content", hi: "मुख्य सामग्री पर जाएँ" },
  "a11y.stepProgress": { en: "Progress through the handover", hi: "हस्तांतरण की प्रगति" },
  "a11y.statusUpdates": { en: "Status updates", hi: "स्थिति अद्यतन" },

  "nav.language": { en: "Language", hi: "भाषा" },
  "nav.english": { en: "English", hi: "English" },
  "nav.hindi": { en: "हिंदी", hi: "हिंदी" },
  "nav.details": { en: "Prototype details", hi: "प्रोटोटाइप विवरण" },
  "nav.close": { en: "Close", hi: "बंद करें" },

  "step.route": { en: "Route", hi: "मार्ग" },
  "step.vehicle": { en: "Vehicle", hi: "वाहन" },
  "step.dealer": { en: "Dealer", hi: "डीलर" },
  "step.readiness": { en: "Readiness", hi: "तैयारी" },
  "step.review": { en: "Shared review", hi: "साझा समीक्षा" },
  "step.outcome": { en: "Outcome", hi: "परिणाम" },

  "route.heading": { en: "What are you doing with the vehicle?", hi: "आप वाहन के साथ क्या कर रहे हैं?" },
  "route.dealer.title": {
    en: "Handing it to an authorised dealer",
    hi: "अधिकृत डीलर को सौंप रहे हैं",
  },
  "route.dealer.desc": {
    en: "The dealer takes delivery of the vehicle and an intimation of delivery is recorded. This is the journey this prototype covers.",
    hi: "डीलर वाहन की सुपुर्दगी लेता है और सुपुर्दगी की सूचना दर्ज होती है। यह प्रोटोटाइप यही प्रक्रिया कवर करता है।",
  },
  "route.private.title": { en: "Selling to a private buyer", hi: "निजी खरीदार को बेच रहे हैं" },
  "route.private.desc": {
    en: "An ownership transfer between two individuals. A different process, not covered here.",
    hi: "दो व्यक्तियों के बीच स्वामित्व हस्तांतरण। यह एक अलग प्रक्रिया है, यहाँ शामिल नहीं है।",
  },
  "route.private.heading": { en: "Out of scope", hi: "कार्यक्षेत्र से बाहर" },
  "route.private.next": {
    en: "Choose the authorised-dealer route to continue, or close this and come back.",
    hi: "आगे बढ़ने के लिए अधिकृत-डीलर मार्ग चुनें, या इसे बंद करके बाद में आएँ।",
  },
  "route.start": { en: "Start this handover", hi: "यह हस्तांतरण शुरू करें" },
  "route.chooseOther": { en: "Choose a different route", hi: "दूसरा मार्ग चुनें" },

  "vehicle.heading": { en: "Which vehicle?", hi: "कौन सा वाहन?" },
  "vehicle.intro": {
    en: "Enter the details of one of the fictional demo vehicles below.",
    hi: "नीचे दिए गए काल्पनिक डेमो वाहनों में से किसी एक का विवरण दर्ज करें।",
  },
  "vehicle.registration": { en: "Registration number", hi: "पंजीकरण संख्या" },
  "vehicle.chassis": { en: "Last 5 characters of the chassis number", hi: "चेसिस संख्या के अंतिम 5 अक्षर" },
  "vehicle.lookup": { en: "Look up vehicle", hi: "वाहन खोजें" },
  "vehicle.samples": { en: "Fictional demo vehicles", hi: "काल्पनिक डेमो वाहन" },
  "vehicle.use": { en: "Use this one", hi: "इसे चुनें" },
  "vehicle.found": { en: "Vehicle record found", hi: "वाहन रिकॉर्ड मिला" },
  "vehicle.owner": { en: "Registered owner", hi: "पंजीकृत स्वामी" },
  "vehicle.model": { en: "Make and model", hi: "निर्माता और मॉडल" },
  "vehicle.change": { en: "Change vehicle", hi: "वाहन बदलें" },
  "vehicle.continue": { en: "Continue to the dealer", hi: "डीलर चरण पर जाएँ" },

  "dealer.heading": { en: "Which authorised dealer?", hi: "कौन सा अधिकृत डीलर?" },
  "dealer.intro": {
    en: "The dealer's authorisation is looked up in a simulated registry that stands in for the Form 29B authorisation state.",
    hi: "डीलर का प्राधिकरण एक सिम्युलेटेड रजिस्ट्री में देखा जाता है, जो फॉर्म 29B प्राधिकरण स्थिति का स्थान लेती है।",
  },
  "dealer.authorisation": { en: "Dealer authorisation number", hi: "डीलर प्राधिकरण संख्या" },
  "dealer.verify": { en: "Check authorisation", hi: "प्राधिकरण जाँचें" },
  "dealer.samples": { en: "Fictional demo dealers", hi: "काल्पनिक डेमो डीलर" },
  "dealer.status": { en: "Authorisation status", hi: "प्राधिकरण स्थिति" },
  "dealer.validity": { en: "Valid", hi: "वैधता" },
  "dealer.blocked": {
    en: "This handover cannot continue with this dealer.",
    hi: "इस डीलर के साथ यह हस्तांतरण आगे नहीं बढ़ सकता।",
  },
  "dealer.chooseAnother": { en: "Try a different authorisation number", hi: "दूसरी प्राधिकरण संख्या आज़माएँ" },
  "dealer.change": { en: "Change dealer", hi: "डीलर बदलें" },
  "dealer.continue": { en: "Continue to readiness", hi: "तैयारी चरण पर जाएँ" },

  "readiness.heading": { en: "Readiness checklist", hi: "तैयारी सूची" },
  "readiness.intro": {
    en: "Each row says where its answer came from: a simulated record, or something you are declaring yourself.",
    hi: "प्रत्येक पंक्ति बताती है कि उसका उत्तर कहाँ से आया: सिम्युलेटेड रिकॉर्ड से, या आपकी स्वयं की घोषणा से।",
  },
  "readiness.yourDeclarations": { en: "Your declarations", hi: "आपकी घोषणाएँ" },
  "readiness.dealerDeclarations": { en: "Dealer declarations", hi: "डीलर की घोषणाएँ" },
  "readiness.dealerPending": {
    en: "The dealer has not joined yet, so dealer declarations are not available on this device.",
    hi: "डीलर अभी शामिल नहीं हुआ है, इसलिए डीलर की घोषणाएँ इस डिवाइस पर उपलब्ध नहीं हैं।",
  },
  "readiness.save": { en: "Save declarations", hi: "घोषणाएँ सहेजें" },
  "readiness.saved": { en: "Declarations saved", hi: "घोषणाएँ सहेजी गईं" },
  "readiness.outstanding": { en: "Still outstanding", hi: "अभी शेष" },
  "readiness.allClear": { en: "Nothing outstanding at this stage", hi: "इस चरण में कुछ शेष नहीं" },
  "readiness.continue": { en: "Continue to shared review", hi: "साझा समीक्षा पर जाएँ" },
  "readiness.checkedLater": {
    en: "Checked again when the record is sent",
    hi: "रिकॉर्ड भेजते समय दोबारा जाँचा जाएगा",
  },

  "provenance.simulated": { en: "Checked against a simulated record", hi: "सिम्युलेटेड रिकॉर्ड से जाँचा गया" },
  "provenance.declared": { en: "You are declaring this", hi: "यह आपकी घोषणा है" },
  "provenance.both": {
    en: "Simulated record, plus your declaration",
    hi: "सिम्युलेटेड रिकॉर्ड, और आपकी घोषणा",
  },
  "provenance.info": { en: "For information", hi: "जानकारी हेतु" },

  "result.pass": { en: "Ready", hi: "तैयार" },
  "result.pending": { en: "Not yet done", hi: "अभी नहीं हुआ" },
  "result.fail": { en: "Blocked", hi: "अवरुद्ध" },
  "result.info": { en: "Note", hi: "टिप्पणी" },

  "pair.heading": { en: "Bring the dealer in", hi: "डीलर को शामिल करें" },
  "pair.intro": {
    en: "Show this code to the dealer on their own device. It works once and then expires.",
    hi: "यह कोड डीलर को उनके डिवाइस पर दिखाएँ। यह एक बार काम करता है और फिर समाप्त हो जाता है।",
  },
  "pair.generate": { en: "Create a pairing code", hi: "पेयरिंग कोड बनाएँ" },
  "pair.regenerate": { en: "Create a new code", hi: "नया कोड बनाएँ" },
  "pair.code": { en: "Pairing code", hi: "पेयरिंग कोड" },
  "pair.expiresIn": { en: "Expires in", hi: "समाप्ति में" },
  "pair.expired": { en: "This code has expired.", hi: "यह कोड समाप्त हो गया है।" },
  "pair.seconds": { en: "seconds", hi: "सेकंड" },
  "pair.scan": { en: "Or scan this", hi: "या इसे स्कैन करें" },
  "pair.qrAlt": {
    en: "Square pattern encoding the dealer joining link for this handover",
    hi: "इस हस्तांतरण के डीलर लिंक को दर्शाने वाला वर्गाकार पैटर्न",
  },
  "pair.copyLink": { en: "Copy the dealer link", hi: "डीलर लिंक कॉपी करें" },
  "pair.copied": { en: "Link copied", hi: "लिंक कॉपी हो गया" },
  "pair.waiting": { en: "Waiting for the dealer to join", hi: "डीलर के शामिल होने की प्रतीक्षा" },
  "pair.joined": { en: "The dealer has joined", hi: "डीलर शामिल हो गया है" },
  "pair.continue": { en: "Continue to shared review", hi: "साझा समीक्षा पर जाएँ" },

  "join.heading": { en: "Join a handover as the dealer", hi: "डीलर के रूप में हस्तांतरण में शामिल हों" },
  "join.intro": {
    en: "Enter the code the seller is showing you, or open the link they shared.",
    hi: "विक्रेता द्वारा दिखाया गया कोड दर्ज करें, या उनके साझा किए लिंक को खोलें।",
  },
  "join.code": { en: "Pairing code", hi: "पेयरिंग कोड" },
  "join.join": { en: "Join this handover", hi: "इस हस्तांतरण में शामिल हों" },
  "join.joining": { en: "Joining", hi: "शामिल हो रहे हैं" },

  "review.heading": { en: "Both sides review the same details", hi: "दोनों पक्ष समान विवरण की समीक्षा करें" },
  "review.details": { en: "Handover details", hi: "हस्तांतरण विवरण" },
  "review.declarations": { en: "Declarations recorded", hi: "दर्ज घोषणाएँ" },
  "review.handoverTime": { en: "Handover time", hi: "हस्तांतरण समय" },
  "review.confirm": { en: "These details are correct", hi: "ये विवरण सही हैं" },
  "review.youConfirmed": { en: "You have confirmed these details", hi: "आपने इन विवरणों की पुष्टि की है" },
  "review.withdraw": { en: "Withdraw my confirmation", hi: "मेरी पुष्टि वापस लें" },
  "review.sellerConfirmed": { en: "Seller has confirmed", hi: "विक्रेता ने पुष्टि की" },
  "review.dealerConfirmed": { en: "Dealer has confirmed", hi: "डीलर ने पुष्टि की" },
  "review.sellerWaiting": { en: "Waiting for the seller", hi: "विक्रेता की प्रतीक्षा" },
  "review.dealerWaiting": { en: "Waiting for the dealer", hi: "डीलर की प्रतीक्षा" },
  "review.bothConfirmed": {
    en: "Both sides have confirmed the same details.",
    hi: "दोनों पक्षों ने समान विवरण की पुष्टि की है।",
  },
  "review.send": { en: "Send the delivery record", hi: "सुपुर्दगी रिकॉर्ड भेजें" },
  "review.sendNote": {
    en: "This sends the details to the simulated Form 29C adapter inside this prototype. Nothing leaves it.",
    hi: "यह विवरण इस प्रोटोटाइप के अंदर सिम्युलेटेड फॉर्म 29C एडाप्टर को भेजता है। कुछ भी बाहर नहीं जाता।",
  },
  "review.changed": {
    en: "The details changed, so earlier confirmations were cleared. Review the updated details and confirm again.",
    hi: "विवरण बदल गए, इसलिए पहले की पुष्टियाँ रद्द कर दी गईं। अद्यतन विवरण देखकर पुनः पुष्टि करें।",
  },
  "review.editDetails": { en: "Change the details", hi: "विवरण बदलें" },
  "review.roleSeller": { en: "You are the seller on this device", hi: "इस डिवाइस पर आप विक्रेता हैं" },
  "review.roleDealer": { en: "You are the dealer on this device", hi: "इस डिवाइस पर आप डीलर हैं" },
  "review.roleObserver": {
    en: "This device is watching this handover and cannot act on it.",
    hi: "यह डिवाइस इस हस्तांतरण को देख रहा है और इस पर कार्रवाई नहीं कर सकता।",
  },

  "submitting.heading": { en: "Sending the delivery record", hi: "सुपुर्दगी रिकॉर्ड भेजा जा रहा है" },
  "submitting.body": {
    en: "Waiting for the simulated adapter to answer. Do not close this window.",
    hi: "सिम्युलेटेड एडाप्टर के उत्तर की प्रतीक्षा। इस विंडो को बंद न करें।",
  },
  "submitting.notYet": {
    en: "Sent is not the same as acknowledged. This screen stays until an acknowledgement is recorded.",
    hi: "भेजा जाना पावती मिलने के समान नहीं है। पावती दर्ज होने तक यह स्क्रीन बनी रहेगी।",
  },

  "outcome.ack.heading": { en: "Delivery acknowledged", hi: "सुपुर्दगी की पावती मिली" },
  "outcome.ack.body": {
    en: "The simulated adapter recorded this handover and returned an acknowledgement number.",
    hi: "सिम्युलेटेड एडाप्टर ने इस हस्तांतरण को दर्ज किया और एक पावती संख्या दी।",
  },
  "outcome.ack.number": { en: "Acknowledgement number", hi: "पावती संख्या" },
  "outcome.rejected.heading": { en: "Not accepted", hi: "स्वीकार नहीं किया गया" },
  "outcome.rejected.body": {
    en: "The simulated adapter declined this record. Nothing was acknowledged.",
    hi: "सिम्युलेटेड एडाप्टर ने इस रिकॉर्ड को अस्वीकार किया। किसी भी बात की पावती नहीं मिली।",
  },
  "outcome.rejected.next": { en: "Go back and review the details", hi: "वापस जाकर विवरण देखें" },
  "outcome.temporary.heading": { en: "Could not be sent", hi: "भेजा नहीं जा सका" },
  "outcome.temporary.body": {
    en: "The simulated adapter was temporarily unavailable. Nothing was acknowledged, and your confirmations are still valid.",
    hi: "सिम्युलेटेड एडाप्टर अस्थायी रूप से अनुपलब्ध था। किसी बात की पावती नहीं मिली, और आपकी पुष्टियाँ अभी भी मान्य हैं।",
  },
  "outcome.temporary.retry": { en: "Try sending again", hi: "पुनः भेजने का प्रयास करें" },
  "outcome.unknown.heading": { en: "Outcome not known", hi: "परिणाम ज्ञात नहीं" },
  "outcome.unknown.body": {
    en: "The record was sent but no answer came back, so this prototype does not know whether it was recorded. It will not guess.",
    hi: "रिकॉर्ड भेजा गया था लेकिन कोई उत्तर नहीं मिला, इसलिए यह प्रोटोटाइप नहीं जानता कि वह दर्ज हुआ या नहीं। यह अनुमान नहीं लगाएगा।",
  },
  "outcome.unknown.reconcile": { en: "Check the status again", hi: "स्थिति दोबारा जाँचें" },
  "outcome.unknown.warning": {
    en: "Do not start a second handover for this vehicle while the outcome is unknown.",
    hi: "जब तक परिणाम अज्ञात है, इस वाहन के लिए दूसरा हस्तांतरण शुरू न करें।",
  },
  "outcome.cancelled.heading": { en: "Handover cancelled", hi: "हस्तांतरण रद्द" },
  "outcome.cancelled.body": {
    en: "This handover was cancelled and nothing was sent.",
    hi: "यह हस्तांतरण रद्द कर दिया गया और कुछ भी नहीं भेजा गया।",
  },
  "outcome.attempts": { en: "Attempts", hi: "प्रयास" },
  "outcome.reason": { en: "Reason given", hi: "दिया गया कारण" },

  "common.retry": { en: "Try again", hi: "पुनः प्रयास करें" },
  "common.cancelHandover": { en: "Cancel this handover", hi: "यह हस्तांतरण रद्द करें" },
  "common.cancelConfirm": {
    en: "Cancel this handover? It cannot be resumed.",
    hi: "यह हस्तांतरण रद्द करें? इसे फिर शुरू नहीं किया जा सकता।",
  },
  "common.back": { en: "Back", hi: "पीछे" },
  "common.loading": { en: "Loading", hi: "लोड हो रहा है" },
  "common.working": { en: "Working", hi: "कार्य चल रहा है" },
  "common.startOver": { en: "Start a new handover", hi: "नया हस्तांतरण शुरू करें" },
  "common.dismiss": { en: "Dismiss", hi: "हटाएँ" },
  "common.simulated": { en: "Simulated", hi: "सिम्युलेटेड" },
  "common.fictional": { en: "Fictional data", hi: "काल्पनिक डेटा" },
  "common.required": { en: "required", hi: "आवश्यक" },
  "common.yes": { en: "Yes", hi: "हाँ" },
  "common.no": { en: "No", hi: "नहीं" },

  "error.heading": { en: "That did not work", hi: "यह नहीं हो सका" },
  "error.notFound.heading": { en: "Handover not found", hi: "हस्तांतरण नहीं मिला" },
  "error.noSession": {
    en: "This device does not hold a party token for this handover, so it can watch but not act.",
    hi: "इस डिवाइस के पास इस हस्तांतरण का पक्षकार टोकन नहीं है, इसलिए यह देख सकता है पर कार्रवाई नहीं कर सकता।",
  },

  "drawer.heading": { en: "Prototype details", hi: "प्रोटोटाइप विवरण" },
  "drawer.intro": {
    en: "Everything a reviewer needs in order to check what this prototype is doing. None of it is needed to use the app.",
    hi: "समीक्षक को यह जाँचने के लिए आवश्यक सब कुछ कि यह प्रोटोटाइप क्या कर रहा है। ऐप उपयोग करने के लिए इसकी आवश्यकता नहीं है।",
  },
  "drawer.build": { en: "Build", hi: "बिल्ड" },
  "drawer.policyVersion": { en: "Rule set applied", hi: "लागू नियम-समूह" },
  "drawer.inForce": { en: "In force", hi: "प्रभावी" },
  "drawer.notInForce": { en: "Not in force", hi: "प्रभावी नहीं" },
  "drawer.caseId": { en: "Handover reference", hi: "हस्तांतरण संदर्भ" },
  "drawer.state": { en: "Recorded state", hi: "दर्ज स्थिति" },
  "drawer.payloadDigest": { en: "Detail digest", hi: "विवरण डाइजेस्ट" },
  "drawer.digestNote": {
    en: "A digest of the reviewed details. It detects a change between review and confirmation. It is not a signature and it does not identify anyone.",
    hi: "समीक्षित विवरणों का डाइजेस्ट। यह समीक्षा और पुष्टि के बीच बदलाव पकड़ता है। यह हस्ताक्षर नहीं है और किसी की पहचान नहीं करता।",
  },
  "drawer.updates": { en: "Live updates", hi: "लाइव अद्यतन" },
  "drawer.updates.socket": { en: "Push channel open", hi: "पुश चैनल खुला" },
  "drawer.updates.polling": { en: "Periodic refresh", hi: "समय-समय पर ताज़ा" },
  "drawer.updates.connecting": { en: "Connecting", hi: "जुड़ रहा है" },
  "drawer.snapshots": { en: "Snapshots applied", hi: "लागू स्नैपशॉट" },
  "drawer.trail": { en: "Recorded events", hi: "दर्ज घटनाएँ" },
  "drawer.trailNote": {
    en: "Each event carries a digest of the one before it, so an edit made directly to the stored log would show up here. That is tamper evidence for a demo, not an independent audit.",
    hi: "प्रत्येक घटना अपने पूर्ववर्ती का डाइजेस्ट रखती है, इसलिए संग्रहीत लॉग में सीधा किया गया बदलाव यहाँ दिखेगा। यह डेमो के लिए छेड़छाड़ का संकेत है, स्वतंत्र ऑडिट नहीं।",
  },
  "drawer.chainIntact": { en: "Event chain intact", hi: "घटना श्रृंखला अक्षुण्ण" },
  "drawer.chainBroken": { en: "Event chain does not verify", hi: "घटना श्रृंखला सत्यापित नहीं" },
  "drawer.about": { en: "What this is", hi: "यह क्या है" },
  "drawer.anchor": { en: "What it models", hi: "यह किसका मॉडल है" },
  "drawer.rules": { en: "Rule set rows", hi: "नियम-समूह पंक्तियाँ" },
  "drawer.source": { en: "Reference", hi: "संदर्भ" },
  "drawer.resetDemo": { en: "Clear all demo data", hi: "सभी डेमो डेटा साफ़ करें" },
  "drawer.resetNote": {
    en: "Deletes every handover in this instance. The fictional vehicles and dealers are files, so they survive.",
    hi: "इस इंस्टेंस के प्रत्येक हस्तांतरण को हटाता है। काल्पनिक वाहन और डीलर फ़ाइलें हैं, इसलिए वे बने रहते हैं।",
  },
} as const satisfies Record<string, Phrase>;

export type UiKey = keyof typeof UI;

export function phrase(key: UiKey, lang: Lang): string {
  return UI[key][lang];
}

/** Pick the right half of any bilingual payload the API sent. */
export function pick(value: { en: string; hi: string } | null | undefined, lang: Lang): string {
  if (!value) return "";
  return value[lang];
}
