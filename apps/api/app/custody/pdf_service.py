"""Generate an extractable, clearly simulated Form 29C pre-fill worksheet."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas


@dataclass(frozen=True, slots=True)
class Form29CFields:
    case_id: str
    vehicle_no: str
    chassis_suffix: str
    seller_name: str
    seller_address: str
    vehicle_make: str
    chassis_no: str
    engine_or_motor_no: str
    rto_jurisdiction: str
    dealer_name: str
    dealer_gstin: str
    trade_certificate_no: str
    dealer_business_address: str
    authorisation_certificate_no: str
    authorisation_issued_by: str
    authorisation_valid_until: str
    odometer_reading: int
    delivery_timestamp: str


@dataclass(frozen=True, slots=True)
class GeneratedDocument:
    content: bytes
    sha256: str


def _wrapped_lines(text: str, *, font: str, size: float, max_width: float) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if not current or stringWidth(candidate, font, size) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]


def _draw_wrapped(
    canvas: Canvas,
    text: str,
    *,
    x: float,
    y: float,
    max_width: float,
    font: str = "Helvetica",
    size: float = 9,
    leading: float = 12,
) -> float:
    canvas.setFont(font, size)
    for line in _wrapped_lines(text, font=font, size=size, max_width=max_width):
        canvas.drawString(x, y, line)
        y -= leading
    return y


def _header(canvas: Canvas, *, page: int) -> float:
    width, height = A4
    canvas.setFillColorRGB(0.07, 0.18, 0.29)
    canvas.rect(0, height - 35 * mm, width, 35 * mm, stroke=0, fill=1)
    canvas.setFillColorRGB(1, 1, 1)
    canvas.setFont("Helvetica-Bold", 15)
    canvas.drawCentredString(
        width / 2,
        height - 15 * mm,
        "FORM 29C PRE-FILL WORKSHEET - PROTOTYPE",
    )
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawCentredString(
        width / 2,
        height - 23 * mm,
        "FICTIONAL DATA - NOT SUBMITTED TO GOVERNMENT - NO PORTAL ACKNOWLEDGEMENT",
    )
    canvas.setFont("Helvetica", 8)
    canvas.drawCentredString(
        width / 2,
        height - 29 * mm,
        f"Rule 55B(1) field-aligned preparation aid | Page {page} of 2",
    )
    canvas.setFillColorRGB(0, 0, 0)
    return height - 45 * mm


def _field_row(canvas: Canvas, label: str, value: str, y: float) -> float:
    width, _ = A4
    canvas.setFont("Helvetica-Bold", 8.5)
    canvas.drawString(20 * mm, y, f"{label}:")
    return (
        _draw_wrapped(
            canvas,
            value,
            x=67 * mm,
            y=y,
            max_width=width - 87 * mm,
            size=8.5,
            leading=10.5,
        )
        - 3 * mm
    )


def _footer(canvas: Canvas) -> None:
    width, _ = A4
    canvas.setStrokeColorRGB(0.65, 0.69, 0.72)
    canvas.line(20 * mm, 18 * mm, width - 20 * mm, 18 * mm)
    canvas.setFillColorRGB(0.25, 0.29, 0.33)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawCentredString(
        width / 2,
        12 * mm,
        "Independent hackathon prototype - verify all facts and complete the official portal process",
    )
    canvas.setFillColorRGB(0, 0, 0)


def generate_form29c(fields: Form29CFields) -> GeneratedDocument:
    """Return deterministic PDF bytes aligned to notified Form 29C fields.

    This is deliberately a preparation worksheet, not a substitute for the
    electronic, jointly signed portal submission or its generated acknowledgement.
    """

    buffer = BytesIO()
    canvas = Canvas(buffer, pagesize=A4, pageCompression=0, invariant=1)
    width, _ = A4
    canvas.setTitle(f"Handover29C pre-fill worksheet {fields.case_id}")

    y = _header(canvas, page=1)
    canvas.setFont("Helvetica-Bold", 11)
    canvas.drawString(20 * mm, y, "Intimation preparation fields")
    y -= 8 * mm
    rows = (
        (
            "Portal acknowledgement",
            "NOT GENERATED - available only after successful portal submission",
        ),
        ("Registering authority", fields.rto_jurisdiction),
        ("Registered owner", fields.seller_name),
        ("Owner address", fields.seller_address),
        ("Delivery date/time", fields.delivery_timestamp),
        ("Vehicle registration", fields.vehicle_no),
        ("Vehicle make/model", fields.vehicle_make),
        ("Full chassis number", fields.chassis_no),
        ("Engine or motor number", fields.engine_or_motor_no),
        ("Authorised dealer", fields.dealer_name),
        ("Dealer place of business", fields.dealer_business_address),
        ("Authorisation certificate", fields.authorisation_certificate_no),
        ("Authorisation issued by", fields.authorisation_issued_by),
        ("Authorisation valid until", fields.authorisation_valid_until),
    )
    for label, value in rows:
        y = _field_row(canvas, label, value, y)

    canvas.setStrokeColorRGB(0.78, 0.45, 0.05)
    canvas.rect(20 * mm, y - 29 * mm, width - 40 * mm, 25 * mm, stroke=1, fill=0)
    canvas.setFont("Helvetica-Bold", 8.5)
    canvas.drawString(
        24 * mm, y - 10 * mm, "Portal-required completion remains outstanding"
    )
    _draw_wrapped(
        canvas,
        "The official electronic form still requires review; neither party's portal signature is provided by this prototype. Successful portal submission and a portal-generated acknowledgement number also remain outstanding.",
        x=24 * mm,
        y=y - 16 * mm,
        max_width=width - 48 * mm,
        size=8,
        leading=10,
    )
    _footer(canvas)
    canvas.showPage()

    y = _header(canvas, page=2)
    canvas.setFont("Helvetica-Bold", 11)
    canvas.drawString(
        20 * mm, y, "Declarations and prototype verification metadata"
    )
    y -= 8 * mm
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(20 * mm, y, "Owner declaration for review before portal signing")
    y -= 5 * mm
    y = _draw_wrapped(
        canvas,
        "The registered owner must verify on the official portal that applicable tax and challan demands are clear; permit, criminal-case, accident, finance, superdari and encumbrance statements are accurate; the supplied information is true; and the authorised dealer may apply for the services allowed by the notified form.",
        x=20 * mm,
        y=y,
        max_width=width - 40 * mm,
        size=8.5,
        leading=11,
    )
    y -= 3 * mm
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(20 * mm, y, "Document and possession statement for review")
    y -= 5 * mm
    y = _draw_wrapped(
        canvas,
        "The parties must verify on the official portal whether the vehicle, registration certificate, PUCC and insurance certificate were handed over and received. The two prototype confirmations record physical custody only and do not constitute these portal declarations.",
        x=20 * mm,
        y=y,
        max_width=width - 40 * mm,
        size=8.5,
        leading=11,
    )
    y -= 5 * mm
    metadata = (
        ("Prototype case reference", fields.case_id),
        ("Dealer GSTIN", fields.dealer_gstin),
        ("Trade certificate", fields.trade_certificate_no),
        ("Chassis suffix used for lookup", fields.chassis_suffix),
        ("Odometer reading", f"{fields.odometer_reading} km"),
        ("Seller prototype confirmation", "RECORDED - not a signature"),
        ("Dealer prototype confirmation", "RECORDED - not a signature"),
    )
    for label, value in metadata:
        y = _field_row(canvas, label, value, y)

    y -= 3 * mm
    canvas.setFont("Helvetica-Bold", 8.5)
    canvas.drawString(
        20 * mm,
        y,
        "Registered owner: There is no e-signature captured by this prototype",
    )
    y -= 10 * mm
    canvas.drawString(
        20 * mm,
        y,
        "Authorised dealer: There is no e-signature captured by this prototype",
    )
    y -= 12 * mm
    canvas.setStrokeColorRGB(0.78, 0.29, 0.04)
    canvas.rect(20 * mm, y - 28 * mm, width - 40 * mm, 25 * mm, stroke=1, fill=0)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(24 * mm, y - 10 * mm, "Prototype boundary")
    _draw_wrapped(
        canvas,
        "NOT SUBMITTED TO GOVERNMENT. This worksheet has no legal effect, does not change ownership or liability, and is not a Form 29C portal acknowledgement.",
        x=24 * mm,
        y=y - 16 * mm,
        max_width=width - 48 * mm,
        size=8.5,
        leading=11,
    )
    _footer(canvas)
    canvas.save()
    content = buffer.getvalue()
    return GeneratedDocument(
        content=content,
        sha256=hashlib.sha256(content).hexdigest(),
    )


__all__ = ["Form29CFields", "GeneratedDocument", "generate_form29c"]
