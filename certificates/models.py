from django.db import models


class Certificate(models.Model):
    registration = models.OneToOneField(
        'seminars.SeminarRegistration',
        on_delete=models.CASCADE
    )

    certificate_file = models.FileField(
        upload_to='certificates/'
    )

    generated_at = models.DateTimeField(
        auto_now_add=True
    )
