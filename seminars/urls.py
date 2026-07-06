from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                  path('create/', views.create_seminar, name='create_seminar'),
                  path('manager/', views.manager_seminars, name='manager_seminars'),
                  path('all/', views.user_seminars, name='user_seminars'),
                  path('register/<int:seminar_id>/', views.register_seminar, name='register_seminar'),
                  path('registrations/<int:seminar_id>/', views.seminar_registrations, name='seminar_registrations'),
                  path('my-registrations/', views.my_registrations, name='my_registrations'),
                  path(
                      'verify/idcard/<uuid:token>/',
                      views.verify_idcard,
                      name='verify_idcard'
                  ),
                  path(
                      'attendance/<uuid:token>/',
                      views.attendance_verify,
                      name='attendance_verify'
                  ),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
