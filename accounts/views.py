from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView as DjangoLogoutView
from .forms import CustomUserCreationForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, TemplateView
from django_smart_ratelimit.decorator import rate_limit
from django.utils.decorators import method_decorator
from common.ratelimit_key import rate_key


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
