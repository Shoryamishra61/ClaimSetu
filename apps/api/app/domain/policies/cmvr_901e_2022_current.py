"""Current-law Form 29C preflight policy.

Policy version: ``CMVR_901E_2022_CURRENT``
Anchor: G.S.R. 901(E), Central Motor Vehicles (Twenty-Sixth Amendment) Rules,
2022 -- notified 22 Dec 2022, effective 1 Apr 2023. Source S03 in
14_SOURCE_LEDGER.md.

Every item below maps 1:1 onto a row of 20_POLICY_MAPPING.md. Nothing here is
invented: the declarations are the ones the *final* 2022 Form 29C already
contains. The July 2026 G.S.R. 649(E) proposals are draft and live in
``draft/gsr_649e_2026_draft.py``, which cannot be selected -- see that file's
docstring and ``PolicyService``.

Hindi strings are a first-pass engineering draft and are listed in
KNOWN_LIMITATIONS.md as awaiting native-speaker review. They are shipped because
a bilingual critical path with reviewed-pending copy is more useful than an
English-only one, not because they are certified.
"""

from __future__ import annotations

from ..policy_types import (
    BlockingStage,
    ItemResult,
    PolicyContext,
    PolicyDefinition,
    PolicyItem,
    ResponsibleActor,
    SourceType,
)

POLICY_VERSION = "CMVR_901E_2022_CURRENT"

_SOURCE_ID = "S03"


def _fixture_check(flag: str):
    """Evaluator for a purely fixture-backed document state."""

    def _eval(ctx: PolicyContext) -> ItemResult:
        if not ctx.vehicle_loaded:
            return ItemResult.PENDING
        return ItemResult.PASS if ctx.document_ready(flag) else ItemResult.FAIL

    return _eval


def _fixture_and_declaration(flag: str, code: str):
    """Evaluator for a hybrid row: fixture says it exists, owner says it is handed over.

    FAIL when the fixture is negative (the prototype has positive information the
    document is not in order) but PENDING when only the declaration is missing --
    the difference matters because one is a blocker the user cannot fix by
    ticking a box, and the other is.
    """

    def _eval(ctx: PolicyContext) -> ItemResult:
        if not ctx.vehicle_loaded:
            return ItemResult.PENDING
        if not ctx.document_ready(flag):
            return ItemResult.FAIL
        return ItemResult.PASS if ctx.declared(code) else ItemResult.PENDING

    return _eval


def _declaration(code: str):
    def _eval(ctx: PolicyContext) -> ItemResult:
        return ItemResult.PASS if ctx.declared(code) else ItemResult.PENDING

    return _eval


def _dealer_declaration(code: str):
    """Dealer-side declaration.

    Stays PENDING rather than FAIL before the dealer joins: the dealer has not
    had an opportunity to act, so calling it a failure would be untruthful and
    would push the seller toward "fixing" something that is not broken.
    """

    def _eval(ctx: PolicyContext) -> ItemResult:
        if not ctx.dealer_joined:
            return ItemResult.PENDING
        return ItemResult.PASS if ctx.declared(code) else ItemResult.PENDING

    return _eval


def _dealer_active(ctx: PolicyContext) -> ItemResult:
    if ctx.dealer_status is None:
        return ItemResult.PENDING
    return ItemResult.PASS if ctx.dealer_status == "ACTIVE" else ItemResult.FAIL


def _vehicle_loaded(ctx: PolicyContext) -> ItemResult:
    return ItemResult.PASS if ctx.vehicle_loaded else ItemResult.PENDING


def _informational(_: PolicyContext) -> ItemResult:
    return ItemResult.INFO


CURRENT_POLICY = PolicyDefinition(
    version=POLICY_VERSION,
    title="Current Form 29C readiness (G.S.R. 901(E), effective 1 Apr 2023)",
    source_id=_SOURCE_ID,
    source_locator="Rules 55A-55C and Form 29C",
    in_force=True,
    items=(
        PolicyItem(
            code="DEALER_AUTH_ACTIVE",
            label_en="Dealer authorisation is active",
            label_hi="डीलर का प्राधिकरण सक्रिय है",
            help_en=(
                "Rule 55A requires a valid Form 29B authorisation to act as a "
                "dealer of registered vehicles. This prototype checks a "
                "simulated registry, not a live one."
            ),
            help_hi=(
                "नियम 55A के अनुसार पंजीकृत वाहनों के डीलर के रूप में कार्य करने के लिए "
                "वैध फॉर्म 29B प्राधिकरण आवश्यक है। यह प्रोटोटाइप एक सिम्युलेटेड "
                "रजिस्ट्री की जाँच करता है, वास्तविक की नहीं।"
            ),
            source_type=SourceType.SIMULATED_CHECK,
            responsible=ResponsibleActor.SYSTEM,
            source_id=_SOURCE_ID,
            source_locator="Rule 55A / Form 29B",
            blocking_stage=BlockingStage.PREFLIGHT,
            evaluator=_dealer_active,
        ),
        PolicyItem(
            code="VEHICLE_RECORD_MATCH",
            label_en="Vehicle details match the fictional record",
            label_hi="वाहन का विवरण काल्पनिक रिकॉर्ड से मेल खाता है",
            help_en=(
                "Form 29C identifies the vehicle and its registered owner. Here "
                "those details come from a fictional fixture."
            ),
            help_hi=(
                "फॉर्म 29C वाहन और उसके पंजीकृत स्वामी की पहचान करता है। यहाँ ये "
                "विवरण एक काल्पनिक फिक्स्चर से आते हैं।"
            ),
            source_type=SourceType.SIMULATED_CHECK,
            responsible=ResponsibleActor.SYSTEM,
            source_id=_SOURCE_ID,
            source_locator="Form 29C, vehicle/owner particulars",
            blocking_stage=BlockingStage.PREFLIGHT,
            evaluator=_vehicle_loaded,
        ),
        PolicyItem(
            code="RC_READY",
            label_en="Registration certificate is being handed over",
            label_hi="पंजीकरण प्रमाणपत्र (RC) सौंपा जा रहा है",
            help_en=(
                "Form 29C records that the registration certificate is handed "
                "over to the dealer."
            ),
            help_hi=(
                "फॉर्म 29C में दर्ज होता है कि पंजीकरण प्रमाणपत्र डीलर को सौंप दिया गया है।"
            ),
            source_type=SourceType.SIMULATED_CHECK_WITH_DECLARATION,
            responsible=ResponsibleActor.SELLER,
            source_id=_SOURCE_ID,
            source_locator="Form 29C, documents handed over",
            blocking_stage=BlockingStage.PREFLIGHT,
            evaluator=_fixture_and_declaration("rc_ready", "RC_READY"),
        ),
        PolicyItem(
            code="PUCC_READY",
            label_en="Pollution certificate (PUCC) is being handed over",
            label_hi="प्रदूषण प्रमाणपत्र (PUCC) सौंपा जा रहा है",
            help_en=(
                "Form 29C records that a valid pollution-under-control "
                "certificate is handed over to the dealer."
            ),
            help_hi=(
                "फॉर्म 29C में दर्ज होता है कि वैध प्रदूषण नियंत्रण प्रमाणपत्र डीलर को "
                "सौंप दिया गया है।"
            ),
            source_type=SourceType.SIMULATED_CHECK_WITH_DECLARATION,
            responsible=ResponsibleActor.SELLER,
            source_id=_SOURCE_ID,
            source_locator="Form 29C, documents handed over",
            blocking_stage=BlockingStage.PREFLIGHT,
            evaluator=_fixture_and_declaration("pucc_ready", "PUCC_READY"),
        ),
        PolicyItem(
            code="INSURANCE_READY",
            label_en="Insurance certificate is being handed over",
            label_hi="बीमा प्रमाणपत्र सौंपा जा रहा है",
            help_en=(
                "Form 29C records that the certificate of insurance is handed "
                "over to the dealer."
            ),
            help_hi=(
                "फॉर्म 29C में दर्ज होता है कि बीमा प्रमाणपत्र डीलर को सौंप दिया गया है।"
            ),
            source_type=SourceType.SIMULATED_CHECK_WITH_DECLARATION,
            responsible=ResponsibleActor.SELLER,
            source_id=_SOURCE_ID,
            source_locator="Form 29C, documents handed over",
            blocking_stage=BlockingStage.PREFLIGHT,
            evaluator=_fixture_and_declaration(
                "insurance_ready", "INSURANCE_READY"
            ),
        ),
        PolicyItem(
            code="TAX_CHALLAN_DECL",
            label_en="No tax demand or challan is pending on this vehicle",
            label_hi="इस वाहन पर कोई कर मांग या चालान बकाया नहीं है",
            help_en=(
                "This is your declaration. The prototype does not query any tax "
                "or enforcement system."
            ),
            help_hi=(
                "यह आपकी घोषणा है। यह प्रोटोटाइप किसी कर या प्रवर्तन प्रणाली से "
                "जानकारी नहीं लेता।"
            ),
            source_type=SourceType.USER_DECLARATION,
            responsible=ResponsibleActor.SELLER,
            source_id=_SOURCE_ID,
            source_locator="Form 29C, owner declaration on tax/challan",
            blocking_stage=BlockingStage.PREFLIGHT,
            evaluator=_declaration("TAX_CHALLAN_DECL"),
        ),
        PolicyItem(
            code="PERMIT_DECL",
            label_en="This vehicle has no permit, or the permit is surrendered",
            label_hi="इस वाहन का कोई परमिट नहीं है, या परमिट अभ्यर्पित कर दिया गया है",
            help_en="This is your declaration, as recorded in Form 29C.",
            help_hi="यह आपकी घोषणा है, जैसा फॉर्म 29C में दर्ज होता है।",
            source_type=SourceType.USER_DECLARATION,
            responsible=ResponsibleActor.SELLER,
            source_id=_SOURCE_ID,
            source_locator="Form 29C, permit declaration",
            blocking_stage=BlockingStage.PREFLIGHT,
            evaluator=_declaration("PERMIT_DECL"),
        ),
        PolicyItem(
            code="CASE_ACCIDENT_DECL",
            label_en=(
                "This vehicle is not involved in a pending criminal, "
                "prohibited-goods or accident case"
            ),
            label_hi=(
                "यह वाहन किसी लंबित आपराधिक, प्रतिबंधित-वस्तु या दुर्घटना मामले में "
                "शामिल नहीं है"
            ),
            help_en="This is your declaration, as recorded in Form 29C.",
            help_hi="यह आपकी घोषणा है, जैसा फॉर्म 29C में दर्ज होता है।",
            source_type=SourceType.USER_DECLARATION,
            responsible=ResponsibleActor.SELLER,
            source_id=_SOURCE_ID,
            source_locator="Form 29C, criminal/accident declaration",
            blocking_stage=BlockingStage.PREFLIGHT,
            evaluator=_declaration("CASE_ACCIDENT_DECL"),
        ),
        PolicyItem(
            code="FINANCE_DECL",
            label_en=(
                "This vehicle is not under hire-purchase, lease or hypothecation"
            ),
            label_hi="यह वाहन किराया-क्रय, पट्टा या दृष्टिबंधक के अधीन नहीं है",
            help_en="This is your declaration, as recorded in Form 29C.",
            help_hi="यह आपकी घोषणा है, जैसा फॉर्म 29C में दर्ज होता है।",
            source_type=SourceType.USER_DECLARATION,
            responsible=ResponsibleActor.SELLER,
            source_id=_SOURCE_ID,
            source_locator="Form 29C, finance declaration",
            blocking_stage=BlockingStage.PREFLIGHT,
            evaluator=_declaration("FINANCE_DECL"),
        ),
        PolicyItem(
            code="SUPERDARI_ENCUMBRANCE_DECL",
            label_en=(
                "To the best of my knowledge this vehicle is not under superdari "
                "and is free from encumbrances"
            ),
            label_hi=(
                "मेरी जानकारी के अनुसार यह वाहन सुपरदारी में नहीं है और सभी भार से "
                "मुक्त है"
            ),
            help_en="This is your declaration, as recorded in Form 29C.",
            help_hi="यह आपकी घोषणा है, जैसा फॉर्म 29C में दर्ज होता है।",
            source_type=SourceType.USER_DECLARATION,
            responsible=ResponsibleActor.SELLER,
            source_id=_SOURCE_ID,
            source_locator="Form 29C, superdari/encumbrance declaration",
            blocking_stage=BlockingStage.PREFLIGHT,
            evaluator=_declaration("SUPERDARI_ENCUMBRANCE_DECL"),
        ),
        PolicyItem(
            code="OWNER_ACCURACY_UNDERTAKING",
            label_en=(
                "I am responsible for any inaccuracy or suppression in these "
                "details"
            ),
            label_hi=(
                "इन विवरणों में किसी भी अशुद्धि या तथ्य छिपाने के लिए मैं ज़िम्मेदार हूँ"
            ),
            help_en=(
                "Form 29C places responsibility for inaccuracy or suppression of "
                "information on the registered owner."
            ),
            help_hi=(
                "फॉर्म 29C में अशुद्धि या जानकारी छिपाने की ज़िम्मेदारी पंजीकृत स्वामी "
                "पर होती है।"
            ),
            source_type=SourceType.USER_DECLARATION,
            responsible=ResponsibleActor.SELLER,
            source_id=_SOURCE_ID,
            source_locator="Form 29C, owner undertaking",
            blocking_stage=BlockingStage.PREFLIGHT,
            evaluator=_declaration("OWNER_ACCURACY_UNDERTAKING"),
        ),
        PolicyItem(
            code="DEALER_POSSESSION_CONFIRM",
            label_en=(
                "Dealer confirms taking possession of the listed vehicle and "
                "documents"
            ),
            label_hi=(
                "डीलर सूचीबद्ध वाहन और दस्तावेज़ों का कब्ज़ा लेने की पुष्टि करता है"
            ),
            help_en=(
                "Form 29C carries the dealer's acknowledgement of possession. "
                "The dealer makes this declaration after joining the shared "
                "review, so it is required before submission rather than before "
                "review."
            ),
            help_hi=(
                "फॉर्म 29C में डीलर द्वारा कब्ज़े की स्वीकृति होती है। डीलर यह घोषणा "
                "साझा समीक्षा में शामिल होने के बाद करता है, इसलिए यह समीक्षा से पहले "
                "नहीं, बल्कि जमा करने से पहले आवश्यक है।"
            ),
            source_type=SourceType.USER_DECLARATION,
            responsible=ResponsibleActor.DEALER,
            source_id=_SOURCE_ID,
            source_locator="Form 29C, dealer acknowledgement of possession",
            blocking_stage=BlockingStage.SUBMIT,
            evaluator=_dealer_declaration("DEALER_POSSESSION_CONFIRM"),
        ),
        PolicyItem(
            code="RULE_55C_EFFECT_INFO",
            label_en="What happens after Form 29C is submitted",
            label_hi="फॉर्म 29C जमा होने के बाद क्या होता है",
            help_en=(
                "Rule 55C provides that after submission of Form 29C the "
                "authorised dealer is deemed to be the owner and is solely "
                "responsible for the validity of the relevant documents and for "
                "incidents related to the vehicle. This prototype does not "
                "create a real Form 29C record."
            ),
            help_hi=(
                "नियम 55C के अनुसार फॉर्म 29C जमा होने के बाद प्राधिकृत डीलर को स्वामी "
                "माना जाता है और वह संबंधित दस्तावेज़ों की वैधता तथा वाहन से जुड़ी घटनाओं "
                "के लिए एकमात्र ज़िम्मेदार होता है। यह प्रोटोटाइप कोई वास्तविक फॉर्म 29C "
                "रिकॉर्ड नहीं बनाता।"
            ),
            source_type=SourceType.INFORMATIONAL,
            responsible=ResponsibleActor.SYSTEM,
            source_id=_SOURCE_ID,
            source_locator="Rule 55C(1)",
            blocking_stage=BlockingStage.NONE,
            evaluator=_informational,
        ),
    ),
)
