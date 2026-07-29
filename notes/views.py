from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Count, Exists, OuterRef, Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from django_smart_ratelimit.decorator import rate_limit

from common.ratelimit_key import rate_key

from .forms import CommentForm, NoteForm
from .models import Comment, Like, Note


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
    paginate_by = 15

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
    paginate_by = 15

    def get_queryset(self):
        return Note.objects.public().select_related("owner").order_by("-created_at")


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

        return (
            Note.objects.filter(Q(owner=user) | Q(is_public=True))
            .select_related("owner")
            .prefetch_related(
                Prefetch("comments", queryset=Comment.objects.select_related("owner"))
            )
            .annotate(
                like_count=Count("likes", distinct=True),
                user_liked=Exists(Like.objects.filter(note=OuterRef("pk"), owner=user)),
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment_form"] = CommentForm()
        context["comments"] = self.object.comments.all()
        context["user_liked"] = self.object.user_liked
        context["like_count"] = self.object.like_count

        return context


@rate_limit(
    key=rate_key,
    rate="300/h",
    algorithm="token_bucket",
    algorithm_config={"bucket_size": 15, "refill": 300 / 3600},
)
@login_required
@require_POST
def add_comment(request, pk):
    note = get_object_or_404(Note.objects.public(), pk=pk)

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.owner = request.user
        comment.note = note
        comment.save()

    return redirect("notes:detail", pk=pk)


@rate_limit(
    key=rate_key,
    rate="600/h",
    algorithm="token_bucket",
    algorithm_config={"bucket_size": 30, "refill": 600 / 3600},
)
@login_required
@require_POST
def toggle_like(request, pk):
    note = get_object_or_404(Note.objects.public(), pk=pk)

    if note.owner == request.user:
        return JsonResponse({"error": "you can't like your note"})

    with transaction.atomic():
        like = (
            Like.objects.select_for_update()
            .filter(note=note, owner=request.user)
            .first()
        )

        if like:
            like.delete()
            liked = False
        else:
            Like.objects.create(note=note, owner=request.user)
            liked = True

        like_count = note.likes.count()

    return JsonResponse({"like_count": like_count, "liked": liked})
