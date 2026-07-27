from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class RegisterViewTests(TestCase):
    def test_register_happy_path(self):
        url = reverse("accounts:register")

        data = {
            "username": "test123",
            "first_name": "test",
            "last_name": "testtest",
            "email": "test@test.com",
            "password1": "StrongPass123!!",
            "password2": "StrongPass123!!",
            "bio": "hello",
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="test123").exists())

    def test_register_missing_fields(self):
        url = reverse("accounts:register")

        data = {
            "username": "",
            "password1": "StrongPass123!!",
            "password2": "StrongPass123!!",
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.exists())
        self.assertContains(response, "required", status_code=200)


class LoginViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test123", password="StrongPass123!!"
        )

    def test_login_happy_path(self):
        url = reverse("accounts:login")

        response = self.client.post(
            url, {"username": "test123", "password": "StrongPass123!!"}
        )

        user_id = self.client.session.get("_auth_user_id")

        self.assertEqual(response.status_code, 302)
        self.assertIsNotNone(user_id)

    def test_login_missing_password(self):
        url = reverse("accounts:login")

        response = self.client.post(url, {"username": "test123", "password": ""})

        user_id = self.client.session.get("_auth_user_id")

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(user_id)


class HomeViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test123", password="StrongPass123!!"
        )

    def test_home_happy_path(self):
        url = reverse("accounts:home")

        self.client.login(username="test123", password="StrongPass123!!")

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_home_without_login(self):
        url = reverse("accounts:home")

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
