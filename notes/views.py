from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, UpdateView, DeleteView, CreateView, DetailView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import Note, Like
from .forms import NoteForm, CommentForm


class NoteListView(LoginRequiredMixin, ListView):
    model = Note
    template_name = "notes/note_list.html"
    context_object_name = 'notes'
    
    def get_queryset(self):
        return Note.objects.filter(owner=self.request.user)
    
    
class PublicFeedView(ListView):
    model = Note
    template_name = 'notes/public_feed.html'
    context_object_name = 'notes'

    def get_queryset(self):
        return Note.objects.filter(is_public=True).order_by('-created_at')
    
    
class NoteCreateView(LoginRequiredMixin, CreateView):
    model = Note
    template_name = "notes/note_form.html"
    form_class = NoteForm
    success_url = reverse_lazy('notes:list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)
    
    
class NoteUpdateView(LoginRequiredMixin, UpdateView):
    def get_queryset(self):
        return Note.objects.filter(owner=self.request.user)
    
    model = Note
    template_name = 'notes/note_form.html'
    form_class = NoteForm
    success_url = reverse_lazy('notes:list')
    

class NoteDeleteView(LoginRequiredMixin, DeleteView):
    def get_queryset(self):
        return Note.objects.filter(owner=self.request.user)
    
    model = Note
    template_name = 'notes/note_confirm_delete.html'
    success_url = reverse_lazy('notes:list')



class NoteDetailView(LoginRequiredMixin, DetailView):
    model = Note
    template_name = 'notes/note_detail.html'
    context_object_name = 'note'

    def get_queryset(self):
        user = self.request.user

        return Note.objects.filter(
            Q(owner=user) | Q(is_public=True)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        context['comments'] = self.object.comments.all()
        context['user_liked'] = self.object.likes.filter(user=self.request.user).exists()
        context['like_count'] = self.object.likes.count()
        
        return context
    

@login_required
def add_comment(request, pk):
    note = get_object_or_404(
        Note.objects.filter(is_public=True),
        pk=pk
    )

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.note = note
            comment.save()
    return redirect('notes:detail', pk=pk)


@login_required
def toggle_like(request, pk):
    note = get_object_or_404(Note, pk=pk)

    if note.owner == request.user:
        return JsonResponse({'error': "you can't like your note"})

    like, created = Like.objects.get_or_create(note=note, user=request.user)

    if not created:
        like.delete()
    
    return JsonResponse({'like_count': note.likes.count()})