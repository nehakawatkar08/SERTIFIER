from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, FileResponse
from django.shortcuts import render, get_object_or_404, redirect
from User.decorators import role_required
from certificates.utils import generate_certificate
from seminars.models import SeminarRegistration
from .models import Certificate
import os


# Create your views here.
@login_required
def generate_certificate_view(request, reg_id):
    registration = get_object_or_404(
        SeminarRegistration,
        id=reg_id,
        user=request.user
    )

    if not registration.attended:
        return HttpResponse(
            "Certificate available after attendance only."
        )

    certificate, created = Certificate.objects.get_or_create(
        registration=registration
    )

    file_missing = (
            not certificate.certificate_file or
            not os.path.exists(
                certificate.certificate_file.path
            )
    )

    if created or file_missing:
        file_name = generate_certificate(
            registration
        )

        certificate.certificate_file = (
            f'certificates/{file_name}'
        )

        certificate.save()

    return FileResponse(
        certificate.certificate_file.open('rb'),
        as_attachment=True,
        filename='certificate.pdf'
    )