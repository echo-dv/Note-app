from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path(
        "logout/",
        views.CustomLogoutview.as_view(next_page="accounts:login"),
        name="logout",
    ),
    path("register/", views.CustomRegisterView.as_view(), name="register"),
]
