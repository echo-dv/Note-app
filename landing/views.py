from django.shortcuts import redirect
from django.views.generic import TemplateView


class LandingView(TemplateView):
    template_name = "landing/landing_page.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("accounts:home")
        return super().dispatch(request, *args, **kwargs)
