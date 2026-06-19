from django.contrib import admin
from .models import Note, Comment, Like

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'owner', 'is_public')

    search_fields = ('title', 'owner')

    ordering = ('created_at',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('content', 'user')

    search_fields = ('owner',)

    ordering = ('created_at',)