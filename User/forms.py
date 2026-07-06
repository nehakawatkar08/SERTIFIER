from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


# Manager creates Distributor
class UserCreateForm(forms.ModelForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'phone']  # ❌ removed password fields

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'distributor'
        user.set_unusable_password()  # 🔐 important
        if commit:
            user.save()
        return user


# Admin creates Manager
class ManagerCreateForm(forms.ModelForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'phone']  # ❌ removed password fields

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'manager'
        user.set_unusable_password()  # 🔐 important
        if commit:
            user.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'phone']
