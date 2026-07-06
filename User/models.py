from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('distributor', 'Distributor'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


class UserRelation(models.Model):
    manager = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='managed_distributors'
    )

    distributor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_manager'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.manager} → {self.distributor}"
