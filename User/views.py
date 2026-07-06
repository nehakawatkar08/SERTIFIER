import threading
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.contrib.auth.decorators import login_required
from .forms import UserCreateForm, ProfileUpdateForm
from .forms import ManagerCreateForm
from .decorators import role_required
from django.template import loader
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from .models import CustomUser, UserRelation
from seminars.models import Seminar, SeminarRegistration
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.urls import reverse


def home(request):
    template = loader.get_template('home.html')
    return HttpResponse(template.render())


# 🔹 Login
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


# 🔹 Logout
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request):
    return render(request, 'profile.html', {
        'user': request.user
    })


@login_required
def edit_profile(request):
    form = ProfileUpdateForm(request.POST or None, instance=request.user)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Profile updated successfully")
        return redirect('profile')

    return render(request, 'edit_profile.html', {'form': form})


class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'change_password.html'
    success_url = reverse_lazy('profile')


@login_required
def dashboard_view(request):
    if request.user.role == 'admin':
        return render(request, 'admin_dashboard.html')

    elif request.user.role == 'manager':
        return render(request, 'manager_dashboard.html')

    else:
        return render(request, 'user_dashboard.html')


def send_set_password_email_async(request, user):
    try:
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        link = request.build_absolute_uri(
            reverse('set-password', kwargs={'uidb64': uid, 'token': token})
        )

        send_mail(
            subject='From Certifier: Set your password',
            message=f'Hi {user.first_name},\n\nYour Username is {user.username}\n\nClick the link to set your password:\n{link}',
            from_email='your_email@gmail.com',
            recipient_list=[user.email],
        )

    except Exception as e:
        print("Set password email failed:", e)


def send_set_password_email(request, user):
    thread = threading.Thread(
        target=send_set_password_email_async,
        args=(request, user)
    )
    thread.start()


@login_required
@role_required(['admin'])
def create_manager(request):
    if request.method == 'POST':
        form = ManagerCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_unusable_password()  # 🔐 no password yet
            user.save()

            send_set_password_email(request, user)

            return redirect('dashboard')
    else:
        form = ManagerCreateForm()

    return render(request, 'create_manager.html', {'form': form})


@login_required
@role_required(['manager'])
def create_user(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'distributor'
            user.set_unusable_password()  # 🔐 important
            user.save()

            UserRelation.objects.create(
                manager=request.user,
                distributor=user
            )

            send_set_password_email(request, user)

            return redirect('dashboard')
    else:
        form = UserCreateForm()

    return render(request, 'create_user.html', {'form': form})


User = get_user_model()


def set_password_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect('login')
        else:
            form = SetPasswordForm(user)

        return render(request, 'set_password.html', {'form': form})
    else:
        return render(request, 'invalid_link.html')


@login_required
def toggle_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)

    # ✅ ADMIN can manage managers
    if request.user.role == 'admin':

        if user.role != 'manager':
            return HttpResponse("You can only manage managers ❌")

        #  BEFORE deactivating → transfer seminars
        admin_user = request.user  # current admin

        Seminar.objects.filter(
            created_by=user
        ).update(created_by=admin_user)

    # ✅ MANAGER can manage distributors
    elif request.user.role == 'manager':

        if user.role != 'distributor':
            return HttpResponse("You can only manage distributors ❌")

        relation_exists = UserRelation.objects.filter(
            manager=request.user,
            distributor=user
        ).exists()

        if not relation_exists:
            return HttpResponse("Unauthorized ❌")

    else:
        return HttpResponse("Unauthorized ❌")

    # ✅ Toggle status
    user.is_active = not user.is_active
    user.save()

    # Redirect
    if request.user.role == 'manager':
        return redirect('distributors_list')
    else:
        return redirect('managers_list')


@login_required
@role_required(['admin'])
def managers_list(request):
    managers = CustomUser.objects.filter(role='manager')

    return render(
        request,
        'managers_list.html',
        {
            'managers': managers
        }
    )


@login_required
@role_required(['manager'])
def distributors_list(request):
    relations = UserRelation.objects.filter(manager=request.user)

    distributors = [r.distributor for r in relations]

    return render(
        request,
        'distributors_list.html',
        {
            'distributors': distributors
        }
    )


@login_required
@role_required(['admin', 'manager'])
def all_distributors(request):
    query = request.GET.get('q')

    distributors = User.objects.filter(role='distributor')

    if query:
        distributors = distributors.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query)
        )

    return render(
        request,
        'all_distributors.html',
        {
            'distributors': distributors,
            'query': query
        }
    )


@login_required
@role_required(['admin', 'manager'])
def distributor_profile(request, user_id):
    distributor = get_object_or_404(
        User,
        id=user_id,
        role='distributor'
    )

    registrations = SeminarRegistration.objects.filter(
        user=distributor
    )

    return render(
        request,
        'distributor_profile.html',
        {
            'distributor': distributor,
            'registrations': registrations
        }
    )
