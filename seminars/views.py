import base64
from datetime import timedelta
from io import BytesIO

import qrcode
from django.core.mail import send_mail

from Certified import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import SeminarForm, SeminarRegistrationForm
from User.decorators import role_required
from .models import Seminar, SeminarRegistration
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.db.models import Case, When, Value, IntegerField
from .utils.email_service import send_registration_email
from .utils.id_card_generator import generate_id_card
from django.utils import timezone
import random
import string

from .utils.unique_attendance_code import generate_unique_attendance_code


# 🔹 Manager creates seminar
@login_required
@role_required(['manager'])
def create_seminar(request):
    if request.method == 'POST':
        form = SeminarForm(request.POST, request.FILES)
        if form.is_valid():
            seminar = form.save(commit=False)
            seminar.created_by = request.user
            seminar.save()
            return redirect('manager_seminars')
    else:
        form = SeminarForm()

    return render(request, 'create_seminar.html', {'form': form})


# 🔹 Manager view own seminars
@login_required
@role_required(['manager', 'admin'])
def manager_seminars(request):
    seminars = Seminar.objects.filter(
        created_by=request.user
    ).order_by('-created_at')  # newest first

    return render(request, 'manager_seminars.html', {
        'seminars': seminars
    })


# 🔹 Users view all seminars
@login_required
def user_seminars(request):
    seminars = Seminar.objects.all()

    status = request.GET.get('status')

    registered_seminars = (
        SeminarRegistration.objects.filter(
            user=request.user
        ).values_list(
            'seminar_id',
            flat=True
        )
    )

    if status == 'upcoming':

        seminars = seminars.filter(
            date_time__date__gt=timezone.now().date()
        )

    elif status == 'completed':

        seminars = seminars.filter(
            date_time__date__lt=timezone.now().date()
        )

    return render(request, 'user_seminars.html', {
        'seminars': seminars,
        'registered_seminars':registered_seminars,
    })


@login_required
@role_required(['distributor'])
def register_seminar(request, seminar_id):

    seminar = get_object_or_404(
        Seminar,
        id=seminar_id
    )

    user = request.user

    # =====================================================
    # REGISTRATION CLOSED
    # =====================================================

    if not seminar.registration_open:

        messages.error(
            request,
            "Registration is closed."
        )

        return redirect(
            'seminar_detail',
            seminar_id=seminar.id
        )

    # =====================================================
    # ALREADY REGISTERED
    # =====================================================

    if SeminarRegistration.objects.filter(
        user=user,
        seminar=seminar
    ).exists():

        messages.warning(
            request,
            "You have already registered for this seminar."
        )

        return redirect('user_seminars')

    # =====================================================
    # POST
    # =====================================================

    if request.method == 'POST':

        form = SeminarRegistrationForm(
            request.POST
        )

        if form.is_valid():

            registration = SeminarRegistration.objects.create(

                user=user,

                seminar=seminar,

                attendee_name=form.cleaned_data[
                    'attendee_name'
                ],

                attendee_email=form.cleaned_data[
                    'attendee_email'
                ],

                attendee_phone=form.cleaned_data[
                    'attendee_phone'
                ],

                attendance_code=generate_unique_attendance_code()
            )

            # =============================================
            # GENERATE ID CARD
            # =============================================

            file_path = generate_id_card(
                user,
                seminar,
                registration
            )

            registration.id_card = (
                f"id_cards/id_card_{registration.id}.pdf"
            )

            registration.save()

            # =============================================
            # ATTENDANCE LINK
            # =============================================

            attendance_link = (
                f"{settings.Base_Url}/seminars/"
                f"attendance/"
                f"{seminar.attendance_link_token}/"
            )

            # =============================================
            # SEND EMAIL
            # =============================================

            send_registration_email(
                registration,
                seminar,
                file_path
            )

            messages.success(
                request,
                "Registration successful."
            )

            return redirect('dashboard')

    else:

        form = SeminarRegistrationForm()

    return render(
        request,
        'register_seminar.html',
        {
            'seminar': seminar,
            'form': form
        }
    )


@login_required
@role_required(['manager', 'admin'])
def seminar_registrations(request, seminar_id):
    seminar = get_object_or_404(Seminar, id=seminar_id)

    registrations = SeminarRegistration.objects.filter(seminar=seminar)

    return render(request, 'seminar_registrations.html', {
        'seminar': seminar,
        'registrations': registrations
    })


@login_required
@role_required(['distributor'])
def my_registrations(request):
    registrations = SeminarRegistration.objects.filter(user=request.user).order_by('-registered_at')

    return render(request, 'my_registrations.html', {
        'registrations': registrations
    })


def generate_attendance_code(length=6):
    return ''.join(
        random.choices(
            string.ascii_uppercase + string.digits,
            k=length
        )
    )


def attendance_verify(request, token):
    seminar = get_object_or_404(
        Seminar,
        attendance_link_token=token
    )

    now = timezone.now()

    seminar_time = seminar.date_time

    attendance_end = (
            seminar_time + timedelta(hours=2)
    )

    print("NOW:", now)
    print("SEMINAR:", seminar_time)
    print("END:", attendance_end)

    if now < seminar_time:

        return HttpResponse(
            "Attendance has not started yet ❌"
        )

    if now > attendance_end:

        return HttpResponse(
            "Attendance link expired ❌"
        )

    if request.method == 'POST':

        email = request.POST.get('email')

        code = request.POST.get('code')

        registration = SeminarRegistration.objects.filter(
            seminar=seminar,
            attendee_email=email,
            attendance_code=code
        ).first()

        if not registration:

            return HttpResponse(
                "Invalid attendance details ❌"
            )

        if registration.attended:

            return HttpResponse(
                "Attendance already marked ✅"
            )

        registration.attended = True

        registration.attendance_marked_at = now

        registration.save()

        return HttpResponse(
            "Attendance marked successfully ✅"
        )

    return render(
        request,
        'attendance_verify.html',
        {
            'seminar': seminar
        }
    )


def verify_idcard(request, token):

    registration = get_object_or_404(
        SeminarRegistration,
        verification_token=token
    )

    return render(
        request,
        'verify_idcard.html',
        {
            'registration': registration
        }
    )