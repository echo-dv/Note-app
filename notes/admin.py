from django.contrib import admin

from .models import Comment, Like, Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):

    list_display = ('title', 'created_at', 'owner__username', 'is_public')

    search_fields = ('title', 'owner__username')

    ordering = ("-created_at",)

    readonly_fields = ("created_at", "updated_at")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):

    list_display = ('owner__username', 'note__title', 'created_at')

    search_fields = ('owner__username', 'note__title')

    ordering = ("-created_at",)

    readonly_fields = ("created_at",)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):

    list_display = ('owner__username', 'note__title', 'created_at')

    search_fields = ('owner__username', 'note__title')

    ordering = ("-created_at",)

    readonly_fields = ("created_at",)
