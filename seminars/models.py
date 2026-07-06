from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import uuid

User = settings.AUTH_USER_MODEL


class Seminar(models.Model):
    title = models.CharField(max_length=200)
    topic = models.CharField(max_length=200)
    description = models.TextField()
    date_time = models.DateTimeField(null=True)
    location = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    @property
    def status(self):
        now = timezone.now()

        if self.date_time.date() > now.date():
            return "Upcoming"

        elif self.date_time.date() == now.date():
            return "Ongoing"

        else:
            return "Completed"

    @property
    def registration_open(self):

        now = timezone.now()

        # registration open only BEFORE seminar starts
        return now < self.date_time

    @property
    def attendance_open(self):

        return self.status == "Upcoming" or self.status == "Ongoing"

    # Certificates
    certificate_enabled = models.BooleanField(default=True)

    certificate_title = models.CharField(
        max_length=200,
        default='Certificate of Participation'
    )

    certificate_logo_1 = models.ImageField(
        upload_to='certificate_logos/',
        blank=True,
        null=True
    )

    certificate_logo_2 = models.ImageField(
        upload_to='certificate_logos/',
        blank=True,
        null=True
    )

    certificate_logo_3 = models.ImageField(
        upload_to='certificate_logos/',
        blank=True,
        null=True
    )

    certificate_logo_4 = models.ImageField(
        upload_to='certificate_logos/',
        blank=True,
        null=True
    )

    certificate_signature = models.ImageField(
        upload_to='certificate_signatures/',
        blank=True,
        null=True
    )

    attendance_link_token = models.UUIDField(
        blank=True,
        unique=True,
        editable=False,
        null=True,
        default=uuid.uuid4,
    )

    def __str__(self):
        return self.title


class SeminarRegistration(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    seminar = models.ForeignKey(
        Seminar,
        on_delete=models.CASCADE,
        related_name='registrations'
    )

    # =====================================================
    # ATTENDEE DETAILS
    # =====================================================

    attendee_name = models.CharField(
        max_length=255
    )

    attendee_email = models.EmailField()

    attendee_phone = models.CharField(
        max_length=20
    )

    # =====================================================
    # UNIQUE ATTENDANCE CODE
    # =====================================================

    attendance_code = models.CharField(
        max_length=10,
        unique=True,
        blank=True
    )

    # =====================================================
    # REGISTRATION
    # =====================================================

    registered_at = models.DateTimeField(
        auto_now_add=True
    )

    id_card = models.FileField(
        upload_to='id_cards/',
        null=True,
        blank=True
    )

    # =====================================================
    # ATTENDANCE
    # =====================================================

    attended = models.BooleanField(
        default=False
    )

    attendance_marked_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # =====================================================
    # VERIFICATION TOKEN
    # =====================================================

    verification_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    class Meta:
        unique_together = ('user', 'seminar')

    def __str__(self):
        return f"{self.user} - {self.seminar}"