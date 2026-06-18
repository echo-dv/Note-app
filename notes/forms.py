from django import forms
from .models import Note, Comment

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'content', 'is_public']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widget = {
            'content': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Write a comment...'}),
        }