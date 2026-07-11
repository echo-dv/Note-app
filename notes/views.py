from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.generic import (
    ListView,
    UpdateView,
    DeleteView,
    CreateView,
    DetailView,
)
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import Note, Like
from .forms import NoteForm, CommentForm
from django_smart_ratelimit.decorator import rate_limit
from django.utils.decorators import method_decorator
from common.ratelimit_key import rate_key


@method_decorator(
    rate_limit(
        key=rate_key,
        rate="900/h",
        algorithm="token_bucket",
        algorithm_config={"bucket_size": 30, "refill": 900 / 3600},
    ),
    name="dispatch",
)
class NoteListView(LoginRequiredMixin, ListView):
    model = Note
    template_name = "notes/note_list.html"
    context_object_name = "notes"

    def get_queryset(self):
        return Note.objects.filter(owner=self.request.user)


@method_decorator(
    rate_limit(
        key=rate_key,
        rate="900/h",
        algorithm="token_bucket",
        algorithm_config={"bucket_size": 30, "refill": 900 / 3600},
    ),
    name="dispatch",
)
class PublicFeedView(ListView):
    model = Note
    template_name = "notes/public_feed.html"
    context_object_name = "notes"

    def get_queryset(self):
        return Note.objects.public().order_by("-created_at")


@method_decorator(
    rate_limit(
        key=rate_key,
        rate="300/h",
        algorithm="token_bucket",
        algorithm_config={"bucket_size": 20, "refill": 300 / 3600},
    ),
    name="dispatch",
)
class NoteCreateView(LoginRequiredMixin, CreateView):
    model = Note
    template_name = "notes/note_form.html"
    form_class = NoteForm
    success_url = reverse_lazy("notes:list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


@method_decorator(
    rate_limit(
        key=rate_key,
        rate="600/h",
        algorithm="token_bucket",
        algorithm_config={"bucket_size": 30, "refill": 600 / 3600},
    ),
    name="dispatch",
)
class NoteUpdateView(LoginRequiredMixin, UpdateView):
    def get_queryset(self):
        return Note.objects.filter(owner=self.request.user)

    model = Note
    template_name = "notes/note_form.html"
    form_class = NoteForm
    success_url = reverse_lazy("notes:list")


@method_decorator(
    rate_limit(
        key=rate_key,
        rate="120/h",
        algorithm="token_bucket",
        algorithm_config={"bucket_size": 15, "refill": 120 / 3600},
    ),
    name="dispatch",
)
class NoteDeleteView(LoginRequiredMixin, DeleteView):
    def get_queryset(self):
        return Note.objects.filter(owner=self.request.user)

    model = Note
    template_name = "notes/note_confirm_delete.html"
    success_url = reverse_lazy("notes:list")


@method_decorator(
    rate_limit(
        key=rate_key,
        rate="2000/h",
        algorithm="token_bucket",
        algorithm_config={"bucket_size": 40, "refill": 2000 / 3600},
    ),
    name="dispatch",
)
class NoteDetailView(LoginRequiredMixin, DetailView):
    model = Note
    template_name = "notes/note_detail.html"
    context_object_name = "note"

    def get_queryset(self):
        user = self.request.user

        return Note.objects.filter(Q(owner=user) | Q(is_public=True))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment_form"] = CommentForm()
        context["comments"] = self.object.comments.all()
        context["user_liked"] = self.object.likes.filter(
            user=self.request.user
        ).exists()
        context["like_count"] = self.object.likes.count()

        return context


@rate_limit(
    key=rate_key,
    rate="300/h",
    algorithm="token_bucket",
    algorithm_config={"bucket_size": 15, "refill": 300 / 3600},
)
@login_required
def add_comment(request, pk):
    note = get_object_or_404(Note.objects.public(), pk=pk)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.note = note
            comment.save()
    return redirect("notes:detail", pk=pk)


@rate_limit(
    key=rate_key,
    rate="600/h",
    algorithm="token_bucket",
    algorithm_config={"bucket_size": 30, "refill": 300 / 3600},
)
@login_required
@require_POST
def toggle_like(request, pk):
    note = get_object_or_404(Note.objects.public(), pk=pk)

    if note.owner == request.user:
        return JsonResponse({"error": "you can't like your note"})

    like, created = Like.objects.get_or_create(note=note, user=request.user)

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    return JsonResponse({"like_count": note.likes.count(), "liked": liked})
