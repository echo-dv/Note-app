from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django_smart_ratelimit import rate_limit

from common.ratelimit_key import rate_key


@method_decorator(
    rate_limit(
        key=rate_key,
        rate="1800/h",
        algorithm="token_bucket",
        algorithm_config={"bucket_size": 40, "refill": 1800 / 3600},
    ),
    name="dispatch",
)
class LandingView(TemplateView):
    template_name = "landing/landing_page.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("accounts:home")
        return super().dispatch(request, *args, **kwargs)
