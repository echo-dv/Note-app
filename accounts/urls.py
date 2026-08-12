from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("login/", views.LoginView.as_view(), name="login"),
    path(
        "logout/",
        views.LogoutView.as_view(next_page="accounts:login"),
        name="logout",
    ),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("profile/<str:username>/", views.ProfileView.as_view(), name="profile"),
    path("edit/", views.ProfileUpdateView.as_view(), name="profile_update"),
]
