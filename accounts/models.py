from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    bio = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="about you"
    )

    class Meta:
        verbose_name = "user"
        verbose_name_plural= "users"

    def __str__(self):
        return self.get_full_name() or self.username