from django.db import models
from django.core.validators import MaxLengthValidator
from django.conf import settings


class NoteQuerySet(models.QuerySet):
    def public(self):
        return self.filter(is_public=True)


class Note(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notes"
    )

    title = models.CharField(max_length=150)
    content = models.TextField(validators=[MaxLengthValidator(4000)])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_public = models.BooleanField(default=False)

    objects = NoteQuerySet.as_manager()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-updated_at"]


class Comment(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name="comments")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(validators=[MaxLengthValidator(1200)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Like(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name="likes")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["owner", "note"], name="uniq_like_user_note")
        ]
