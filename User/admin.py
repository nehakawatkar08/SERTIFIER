from django.contrib import admin
from .models import CustomUser, UserRelation
from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = ('username', 'email', 'role', 'is_staff')

    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'phone')}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role', 'phone')}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserRelation)
