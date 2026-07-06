import random
import string

from seminars.models import SeminarRegistration


def generate_unique_attendance_code():

    while True:

        code = ''.join(
            random.choices(
                string.ascii_uppercase + string.digits,
                k=6
            )
        )

        exists = SeminarRegistration.objects.filter(
            attendance_code=code
        ).exists()

        if not exists:
            return code