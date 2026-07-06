from django import forms
from .models import Seminar


class SeminarForm(forms.ModelForm):
    class Meta:
        model = Seminar
        fields = ['title', 'topic', 'description', 'date_time', 'location','certificate_logo_1', 'certificate_logo_2', 'certificate_logo_3', 'certificate_logo_4',
                  'certificate_signature']

        widgets = {
            "date_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class SeminarRegistrationForm(forms.Form):

    attendee_name = forms.CharField(
        max_length=255,

        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter Attendee Name'
            }
        )
    )

    attendee_email = forms.EmailField(

        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter Attendee Email'
            }
        )
    )

    attendee_phone = forms.CharField(
        max_length=20,

        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter Attendee Phone'
            }
        )
    )