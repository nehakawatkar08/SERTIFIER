from django.contrib import admin
from .models import Seminar, SeminarRegistration

# Register your models here.
admin.site.register(Seminar)
admin.site.register(SeminarRegistration)
