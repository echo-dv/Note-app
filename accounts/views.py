from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView, TemplateView, UpdateView
from django_smart_ratelimit.decorator import rate_limit

from common.ratelimit_key import rate_key

from .forms import CustomUserCreationForm, ProfileUpdateForm

User = get_user_model()


@method_decorator(
    rate_limit(
        key=rate_key,
        rate="30/h",
        algorithm="token_bucket",
        algorithm_config={"bucket_size": 5, "refill": 30 / 3600},
    ),
    name="post",
)
class LoginView(DjangoLoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


@method_decorator(
    rate_limit(
        key=rate_key,
        rate="30/h",
        algorithm="token_bucket",
        algorithm_config={"bucket_size": 5, "refill": 30 / 3600},
    ),
    name="post",
)
class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:login")


@method_decorator(
    rate_limit(
        key=rate_key,
        rate="60/m",
        algorithm="token_bucket",
        algorithm_config={"bucket_size": 40, "refill": 60 / 60},
    ),
    name="dispatch",
)
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/home.html"


@method_decorator(
    rate_limit(
        key=rate_key,
        rate="30/m",
        algorithm="token_bucket",
        algorithm_config={"bucket_size": 10, "refill": 30 / 60},
    ),
    name="dispatch",
)
class LogoutView(DjangoLogoutView):
    pass


@method_decorator(
    rate_limit(
        key=rate_key,
        rate="60/m",
        algorithm="token_bucket",
        algorithm_config={"bucket_size": 40, "refill": 1},
    ),
    name="dispatch",
)
class ProfileView(DetailView):
    model = User
    template_name = "accounts/profile.html"
    context_object_name = "profile"
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_queryset(self):
        return User.objects.annotate(
            note_count=Count("notes", distinct=True),
            given_like_count=Count("like", distinct=True),
            given_comment_count=Count("comment", distinct=True),
            received_like_count=Count("notes__likes", distinct=True),
            received_comment_count=Count("notes__comments", distinct=True),
        )


@method_decorator(
    rate_limit(
        key=rate_key,
        rate="20/m",
        algorithm="token_bucket",
        algorithm_config={"bucket_size": 30, "refill": 20 / 60},
    ),
    name="dispatch",
)
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileUpdateForm
    template_name = "accounts/profile_update.html"
    success_url = reverse_lazy("accounts:home")

    def get_object(self):
        return self.request.user
