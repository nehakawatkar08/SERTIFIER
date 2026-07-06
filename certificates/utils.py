# utils/certificate_generator.py

import os

import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors

from django.conf import settings
from Certified import settings


def generate_certificate(registration):

    seminar = registration.seminar
    user = registration.user

    file_name = f'certificate_{registration.id}.pdf'

    certificate_dir = os.path.join(
        settings.MEDIA_ROOT,
        'certificates'
    )

    os.makedirs(
        certificate_dir,
        exist_ok=True
    )

    file_path = os.path.join(
        certificate_dir,
        file_name
    )

    # =====================================================
    # FONT DIRECTORY
    # =====================================================

    assets_dir = os.path.join(
        settings.MEDIA_ROOT,
        'certificate_assets'
    )

    # =====================================================
    # REGISTER FONTS
    # =====================================================

    pdfmetrics.registerFont(
        TTFont(
            'GreatVibes',
            os.path.join(
                assets_dir,
                'GreatVibes-Regular.ttf'
            )
        )
    )

    pdfmetrics.registerFont(
        TTFont(
            'CinzelBold',
            os.path.join(
                assets_dir,
                'Cinzel-Bold.ttf'
            )
        )
    )

    # =====================================================
    # CANVAS
    # =====================================================

    c = canvas.Canvas(
        file_path,
        pagesize=landscape(A4)
    )

    width, height = landscape(A4)

    # =====================================================
    # BACKGROUND IMAGE
    # =====================================================

    background_path = os.path.join(
        assets_dir,
        'background.jpg'
    )

    c.drawImage(
        background_path,
        0,
        0,
        width=width,
        height=height
    )

    # =====================================================
    # LIGHT CONTENT OVERLAY
    # =====================================================

    c.setFillColorRGB(
        1,
        1,
        1,
        alpha=0.1
    )

    c.roundRect(
        60,
        50,
        width - 120,
        height - 140,
        15,
        fill=1,
        stroke=0
    )

    # =====================================================
    # ORGANIZATION NAME
    # =====================================================

    c.setFillColor(
        colors.HexColor("#0A2342")
    )

    c.setFont(
        "CinzelBold",
        18
    )

    c.drawCentredString(
        width / 2,
        height - 105,
        "Jadhav Industries"
    )

    # =====================================================
    # MAIN TITLE
    # =====================================================

    c.setFillColor(
        colors.HexColor("#111111")
    )

    c.setFont(
        "CinzelBold",
        30
    )

    c.drawCentredString(
        width / 2,
        height - 155,
        "CERTIFICATE OF PARTICIPATION"
    )

    # =====================================================
    # SUBTITLE
    # =====================================================

    c.setFillColor(
        colors.HexColor("#555555")
    )

    c.setFont(
        "Helvetica",
        13
    )

    c.drawCentredString(
        width / 2,
        height - 190,
        "THIS CERTIFICATE IS PROUDLY PRESENTED TO"
    )

    # =====================================================
    # USER NAME
    # =====================================================

    full_name = (
        f"{user.first_name} {user.last_name}"
    ).strip()

    if not full_name:
        full_name = user.username

    c.setFillColor(
        colors.HexColor("#9C6B00")
    )

    c.setFont(
        "GreatVibes",
        40
    )

    c.drawCentredString(
        width / 2,
        height - 255,
        full_name
    )

    # =====================================================
    # UNDERLINE BELOW NAME
    # =====================================================

    c.setStrokeColor(
        colors.HexColor("#C8A95B")
    )

    c.setLineWidth(1.2)

    c.line(
        width / 2 - 190,
        height - 268,
        width / 2 + 190,
        height - 268
    )

    # =====================================================
    # PARTICIPATION TEXT
    # =====================================================

    c.setFillColor(
        colors.HexColor("#444444")
    )

    c.setFont(
        "Helvetica",
        15
    )

    c.drawCentredString(
        width / 2,
        height - 310,
        "For successfully participating in"
    )

    # =====================================================
    # SEMINAR TITLE
    # =====================================================

    seminar_title = seminar.title

    seminar_font_size = 21

    if len(seminar_title) > 40:
        seminar_font_size = 17

    if len(seminar_title) > 60:
        seminar_font_size = 15

    c.setFillColor(
        colors.HexColor("#0A2342")
    )

    c.setFont(
        "CinzelBold",
        seminar_font_size
    )

    c.drawCentredString(
        width / 2,
        height - 355,
        f"{seminar_title} Seminar"
    )

    # =====================================================
    # CONDUCTED DATE
    # =====================================================

    if seminar.date_time:

        c.setFillColor(
            colors.HexColor("#555555")
        )

        c.setFont(
            "Helvetica",
            12
        )

        c.drawCentredString(
            width / 2,
            height - 380,
            f"Conducted on {seminar.date_time.date()}"
        )

    # =====================================================
    # SIGNATURE SECTION
    # =====================================================

    signature_y = 120

    c.setStrokeColor(
        colors.HexColor("#777777")
    )

    # Signature line

    c.line(
        width - 290,
        signature_y,
        width - 150,
        signature_y
    )

    # Signature image

    if seminar.certificate_signature:

        c.drawImage(
            seminar.certificate_signature.path,
            width - 250,
            signature_y + 5,
            width=90,
            height=40,
            preserveAspectRatio=True,
            mask='auto'
        )

    c.setFillColor(
        colors.HexColor("#333333")
    )

    c.setFont(
        "Helvetica",
        11
    )

    c.drawCentredString(
        width - 220,
        signature_y - 18,
        "Authorized Signature"
    )

    # =====================================================
    # BOTTOM LEFT LOGOS
    # =====================================================

    logos = []

    possible_logos = [
        seminar.certificate_logo_1,
        seminar.certificate_logo_2,
        seminar.certificate_logo_3,
        seminar.certificate_logo_4,
    ]

    for logo in possible_logos:

        if logo:
            logos.append(logo.path)

    # only available logos shown

    logo_x = 85
    logo_y = 82

    logo_spacing = 90

    for index, logo_path in enumerate(logos):

        c.drawImage(
            logo_path,
            logo_x + (index * logo_spacing),
            logo_y,
            width=80,
            height=80,
            preserveAspectRatio=True,
            mask='auto'
        )

    # =====================================================
    # CERTIFICATE ID
    # =====================================================

    c.setFillColor(
        colors.HexColor("#666666")
    )

    c.setFont(
        "Helvetica",
        9
    )

    c.drawString(
        40,
        35,
        f"Certificate ID: CERT-{registration.id}"
    )

    # =====================================================
    # QR CODE
    # =====================================================

    qr_path = os.path.join(
        f"{settings.MEDIA_ROOT}/qrcodes",
        f'qr_{registration.id}.png'
    )

    c.drawImage(
        qr_path,
        width - 810,
        43,
        width=50,
        height=50,
        preserveAspectRatio=True,
        mask='auto'
    )


    # =====================================================
    # SAVE PDF
    # =====================================================

    c.save()

    return file_name