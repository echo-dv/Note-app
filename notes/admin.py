from django.contrib import admin

from .models import Comment, Like, Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at", "owner", "is_public")

    search_fields = ("title", "owner")

    ordering = ("-created_at",)

    readonly_fields = ("created_at", "updated_at")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("owner", "note", "created_at")

    search_fields = ("owner", "note")

    ordering = ("-created_at",)

    readonly_fields = ("created_at",)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("owner", "note", "created_at")

    search_fields = ("owner", "note")

    ordering = ("-created_at",)

    readonly_fields = ("created_at",)
