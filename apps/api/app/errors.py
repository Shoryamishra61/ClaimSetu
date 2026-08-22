"""The single error contract (SRS section 12).

Every failure the client can encounter is one of these codes. Three properties
matter:

*   **No stack traces or internals leak.** The generic handler converts anything
    unexpected into ``INTERNAL_ERROR`` with a fixed message.
*   **``recoverable`` is machine-readable**, so the UI can decide between "fix
    this and retry" and "this journey cannot continue" without string-matching.
*   **Messages are bilingual.** Error copy is critical copy, so it is covered by
    the English/Hindi requirement rather than left to the frontend to guess.

The messages say what happened and what to do next. None of them claim a
government system said anything -- where a simulated registry or adapter is the
source, the message says so.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ErrorSpec:
    code: str
    http_status: int
    recoverable: bool
    message_en: str
    message_hi: str


def _spec(
    code: str, status: int, recoverable: bool, en: str, hi: str
) -> tuple[str, ErrorSpec]:
    return code, ErrorSpec(
        code=code,
        http_status=status,
        recoverable=recoverable,
        message_en=en,
        message_hi=hi,
    )


ERROR_CATALOGUE: dict[str, ErrorSpec] = dict(
    [
        _spec(
            "UNSUPPORTED_JOURNEY",
            409,
            False,
            "This prototype only covers handing a vehicle to an authorised dealer. "
            "A sale to a private buyer follows a different process and is out of "
            "scope here.",
            "यह प्रोटोटाइप केवल अधिकृत डीलर को वाहन सौंपने की प्रक्रिया कवर करता है। "
            "निजी खरीदार को बिक्री की प्रक्रिया अलग है और यहाँ शामिल नहीं है।",
        ),
        _spec(
            "CASE_NOT_FOUND",
            404,
            False,
            "This handover could not be found. It may have been created in a "
            "different browser or on a reset demo database.",
            "यह हस्तांतरण नहीं मिला। यह किसी अन्य ब्राउज़र में या रीसेट किए गए डेमो "
            "डेटाबेस में बनाया गया हो सकता है।",
        ),
        _spec(
            "VEHICLE_NOT_FOUND",
            404,
            True,
            "No fictional demo vehicle matches those details. Pick one of the "
            "sample vehicles listed on this screen.",
            "इन विवरणों से कोई काल्पनिक डेमो वाहन मेल नहीं खाता। इस स्क्रीन पर दिए गए "
            "नमूना वाहनों में से कोई चुनें।",
        ),
        _spec(
            "DEALER_NOT_FOUND",
            404,
            True,
            "The simulated dealer registry has no record of that authorisation "
            "number. Check the number and try again.",
            "सिम्युलेटेड डीलर रजिस्ट्री में उस प्राधिकरण संख्या का कोई रिकॉर्ड नहीं है। "
            "संख्या जाँचकर पुनः प्रयास करें।",
        ),
        _spec(
            "DEALER_NOT_ACTIVE",
            409,
            False,
            "The simulated registry reports that this dealer's authorisation is "
            "not currently active, so the handover cannot continue.",
            "सिम्युलेटेड रजिस्ट्री के अनुसार इस डीलर का प्राधिकरण अभी सक्रिय नहीं है, "
            "इसलिए हस्तांतरण आगे नहीं बढ़ सकता।",
        ),
        _spec(
            "PREFLIGHT_BLOCKED",
            409,
            True,
            "Some readiness items are still outstanding. Resolve them and try "
            "again.",
            "कुछ तैयारी बिंदु अभी शेष हैं। उन्हें पूरा करके पुनः प्रयास करें।",
        ),
        _spec(
            "STALE_PAYLOAD",
            409,
            True,
            "The handover details changed after you reviewed them. Review the "
            "updated details and confirm again.",
            "आपके समीक्षा करने के बाद हस्तांतरण विवरण बदल गए हैं। अद्यतन विवरण देखकर "
            "पुनः पुष्टि करें।",
        ),
        _spec(
            "INVALID_STATE",
            409,
            True,
            "That step is not available right now. This screen has been refreshed "
            "with the current status.",
            "यह चरण अभी उपलब्ध नहीं है। इस स्क्रीन पर वर्तमान स्थिति दिखा दी गई है।",
        ),
        _spec(
            "PAIR_CODE_INVALID",
            404,
            True,
            "That pairing code is not recognised. Ask the seller to show the code "
            "again.",
            "यह पेयरिंग कोड मान्य नहीं है। विक्रेता से कोड दोबारा दिखाने को कहें।",
        ),
        _spec(
            "PAIR_CODE_EXPIRED",
            410,
            True,
            "That pairing code has expired. Ask the seller to generate a new one.",
            "यह पेयरिंग कोड समाप्त हो चुका है। विक्रेता से नया कोड बनवाएँ।",
        ),
        _spec(
            "PAIR_CODE_ALREADY_USED",
            410,
            True,
            "That pairing code has already been used once. Ask the seller to "
            "generate a new one.",
            "यह पेयरिंग कोड एक बार उपयोग हो चुका है। विक्रेता से नया कोड बनवाएँ।",
        ),
        _spec(
            "UNAUTHORISED_ACTOR",
            403,
            False,
            "This device is not recognised as a party to this handover, so it "
            "cannot take that action.",
            "यह डिवाइस इस हस्तांतरण के पक्षकार के रूप में मान्य नहीं है, इसलिए यह "
            "कार्रवाई नहीं कर सकता।",
        ),
        _spec(
            "CONFIRMATIONS_INCOMPLETE",
            409,
            True,
            "Both the seller and the dealer must confirm the same details before "
            "the Form 29C record can be sent.",
            "फ़ॉर्म 29C रिकॉर्ड भेजने से पहले विक्रेता और डीलर दोनों को समान विवरण की "
            "पुष्टि करनी होगी।",
        ),
        _spec(
            "IDEMPOTENCY_KEY_REQUIRED",
            400,
            True,
            "This request must carry an Idempotency-Key header.",
            "इस अनुरोध के साथ Idempotency-Key हेडर आवश्यक है।",
        ),
        _spec(
            "IDEMPOTENCY_KEY_REUSED",
            409,
            True,
            "That submission reference has already been used for different "
            "handover details. Reload the page and try again.",
            "यह सबमिशन संदर्भ पहले भिन्न विवरणों के लिए उपयोग हो चुका है। पृष्ठ पुनः "
            "लोड करके प्रयास करें।",
        ),
        _spec(
            "SUBMISSION_IN_PROGRESS",
            409,
            True,
            "A submission is already in progress for this handover. Wait for the "
            "result.",
            "इस हस्तांतरण के लिए सबमिशन पहले से चल रहा है। परिणाम की प्रतीक्षा करें।",
        ),
        _spec(
            "ALREADY_ACKNOWLEDGED",
            409,
            False,
            "This handover already has a simulated acknowledgement and cannot be "
            "changed.",
            "इस हस्तांतरण की सिम्युलेटेड पावती पहले ही मिल चुकी है और इसे बदला नहीं "
            "जा सकता।",
        ),
        _spec(
            "VALIDATION_ERROR",
            422,
            True,
            "Some of the details sent were not in the expected format. Check the "
            "highlighted fields.",
            "भेजे गए कुछ विवरण अपेक्षित प्रारूप में नहीं थे। चिह्नित फ़ील्ड जाँचें।",
        ),
        _spec(
            "INVALID_GSTIN",
            400,
            True,
            "Invalid GSTIN format structure.",
            "GSTIN का प्रारूप मान्य नहीं है।",
        ),
        _spec(
            "DEALER_IDENTIFIER_REQUIRED",
            400,
            True,
            "Enter a GSTIN or trade certificate number.",
            "GSTIN या ट्रेड सर्टिफिकेट संख्या दर्ज करें।",
        ),
        _spec(
            "INVALID_ODOMETER",
            400,
            True,
            "Odometer reading must be greater than zero.",
            "ओडोमीटर रीडिंग शून्य से अधिक होनी चाहिए।",
        ),
        _spec(
            "CUSTODY_INVALID_TRANSITION",
            422,
            True,
            "That custody state cannot follow the case's current state.",
            "यह कस्टडी स्थिति मामले की वर्तमान स्थिति के बाद नहीं आ सकती।",
        ),
        _spec(
            "SELLER_NOT_FOUND",
            404,
            True,
            "The selected fictional seller does not match this demo vehicle.",
            "चुना गया काल्पनिक विक्रेता इस डेमो वाहन से मेल नहीं खाता।",
        ),
        _spec(
            "FORM_NOT_READY",
            409,
            True,
            "The prototype Form 29C record is not ready yet.",
            "प्रोटोटाइप फ़ॉर्म 29C रिकॉर्ड अभी तैयार नहीं है।",
        ),
        _spec(
            "RATE_LIMITED",
            429,
            True,
            "Too many attempts in a short time. Wait a moment and try again.",
            "थोड़े समय में बहुत अधिक प्रयास। कुछ देर रुककर पुनः प्रयास करें।",
        ),
        _spec(
            "INTERNAL_ERROR",
            500,
            True,
            "Something went wrong in the prototype. Nothing was submitted. Reload "
            "the page to see the current status.",
            "प्रोटोटाइप में कोई त्रुटि हुई। कुछ भी सबमिट नहीं किया गया। वर्तमान स्थिति "
            "देखने के लिए पृष्ठ पुनः लोड करें।",
        ),
    ]
)


class AppError(Exception):
    """A failure with a defined client contract.

    ``detail`` carries non-sensitive extra context (for example which readiness
    items are outstanding). It must never contain a pair token, a session token,
    or a stack trace; ``tests/test_error_contract.py`` asserts the shape.
    """

    __slots__ = ("detail", "spec")

    def __init__(self, code: str, *, detail: dict[str, object] | None = None) -> None:
        try:
            self.spec = ERROR_CATALOGUE[code]
        except KeyError as exc:  # pragma: no cover - programming error
            raise KeyError(
                f"Unknown error code {code!r}. Add it to ERROR_CATALOGUE with "
                "bilingual copy rather than inventing an ad-hoc message."
            ) from exc
        self.detail = detail or {}
        super().__init__(f"{code}: {self.spec.message_en}")

    @property
    def code(self) -> str:
        return self.spec.code

    @property
    def http_status(self) -> int:
        return self.spec.http_status

    def to_body(self) -> dict[str, object]:
        body: dict[str, object] = {
            "code": self.spec.code,
            "message": self.spec.message_en,
            "message_hi": self.spec.message_hi,
            "recoverable": self.spec.recoverable,
        }
        if self.detail:
            body["detail"] = self.detail
        return {"error": body}
