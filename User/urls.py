from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/',  auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    path('create-manager/', views.create_manager, name='create_manager'),
    path('create-user/', views.create_user, name='create_user'),

    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.CustomPasswordChangeView.as_view(), name='change_password'),
    path(
        'managers/',
        views.managers_list,
        name='managers_list'
    ),
    path(
        'distributors/',
        views.distributors_list,
        name='distributors_list'
    ),
    path(
        'toggle-user/<int:user_id>/',
        views.toggle_user_status,
        name='toggle_user_status'
    ),
    path(
        'all-distributors/',
        views.all_distributors,
        name='all_distributors'
    ),
    path(
        'distributor/<int:user_id>/',
        views.distributor_profile,
        name='distributor_profile'
    ),
    path('set-password/<uidb64>/<token>/', views.set_password_view, name='set-password'),
]