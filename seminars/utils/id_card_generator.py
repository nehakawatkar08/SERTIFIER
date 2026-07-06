import os
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from django.conf import settings
from Certified import settings


def generate_id_card(user, seminar, registration):
    file_name = f"id_card_{registration.id}.pdf"
    file_path = os.path.join(settings.MEDIA_ROOT, 'id_cards', file_name)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    c = canvas.Canvas(file_path, pagesize=(350, 500))

    # 🔷 Header Background
    c.setFillColorRGB(0.2, 0.4, 0.8)
    c.rect(0, 450, 350, 50, fill=1)

    # Title
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(90, 465, "SEMINAR ID CARD")

    # Reset color
    c.setFillColorRGB(0, 0, 0)

    # Divider line
    c.line(20, 440, 330, 440)

    # User Info
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, 400, "Name:")
    c.drawString(30, 370, "Seminar:")
    c.drawString(30, 340, "Date:")
    c.drawString(30, 310, "Reg ID:")

    c.setFont("Helvetica", 12)
    c.drawString(120, 400, registration.attendee_name)
    c.drawString(120, 370, seminar.title)
    c.drawString(120, 340, str(seminar.date_time))  # adjust field name
    c.drawString(120, 310, str(registration.id))

    # QR Code (with verification URL)
    qr_data = (
        f"{settings.Base_Url}/seminars/verify/idcard/{registration.verification_token}/"
    )
    qr = qrcode.make(qr_data)

    qr_path = os.path.join(f"{settings.MEDIA_ROOT}/qrcodes", f"qr_{registration.id}.png")
    qr.save(qr_path)

    c.drawImage(qr_path, 100, 150, width=150, height=150)

    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(80, 100, "Scan for Attendance Verification")

    c.save()

    return file_path
