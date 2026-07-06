import threading

from django.conf import settings
from django.core.mail import EmailMessage
from Certified import settings


def send_registration_email_async(
        registration,
        seminar,
        file_path
):

    try:

        attendance_link = (
            f"{settings.Base_Url}/seminars/"
            f"attendance/"
            f"{seminar.attendance_link_token}/"
        )

        subject = "Seminar Registration Successful"

        message = f"""
Hello {registration.attendee_name},

You have successfully registered for:

Seminar: {seminar.title}

Date: {seminar.date_time}

==================================================

Attendance Code:
{registration.attendance_code}

Attendance Link:
{attendance_link}

IMPORTANT:
- Attendance starts automatically at seminar start time
- Attendance closes automatically after 2 hours
- Keep your attendance code safe

==================================================

Your ID card is attached with this email.

Thank you.
"""

        email = EmailMessage(
            subject=subject,

            body=message,

            from_email=settings.EMAIL_HOST_USER,

            to=[registration.attendee_email]
        )

        # =================================================
        # ATTACH ID CARD
        # =================================================

        email.attach_file(file_path)

        # =================================================
        # SEND EMAIL
        # =================================================

        email.send()

    except Exception as e:

        print("Email failed:", e)


def send_registration_email(
        registration,
        seminar,
        file_path
):

    thread = threading.Thread(

        target=send_registration_email_async,

        args=(
            registration,
            seminar,
            file_path
        )
    )

    thread.start()