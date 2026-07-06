from django.urls import path
from . import views

urlpatterns = [
    path(
        'generate-certificate/<int:reg_id>/',
        views.generate_certificate_view,
        name='generate_certificate'
    ),
]
