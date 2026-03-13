from django.test import TestCase

# Create your test here.
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from unittest.mock import patch

from .serializers import UserSerializer

User = get_user_model()


class UserModelTest(TestCase):

    def test_create_user(self):
        user = User.objects.create_user(
            username="testuser",
            password="password123",
            role="student"
        )

        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.role, "student")
        self.assertTrue(user.check_password("password123"))


class UserSerializerTest(TestCase):

    def test_user_serializer(self):
        user = User.objects.create_user(
            username="serializeruser",
            password="pass123",
            role="teacher"
        )

        serializer = UserSerializer(user)
        data = serializer.data

        self.assertEqual(data["username"], "serializeruser")
        self.assertEqual(data["role"], "teacher")


class UserListAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="apiuser",
            password="pass123",
            role="student"
        )

    def test_user_list_requires_auth(self):
        url = reverse("api-users")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_user_list_authenticated(self):
        url = reverse("api-users")

        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

class LoginViewTest(TestCase):

    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            username="loginuser",
            password="pass123",
            role="student"
        )

    def test_login_success(self):
        response = self.client.post(
            reverse("login"),
            {"username": "loginuser", "password": "pass123"}
        )

        self.assertEqual(response.status_code, 302)  # redirect


    def test_login_fail(self):
        response = self.client.post(
            reverse("login"),
            {"username": "loginuser", "password": "wrong"}
        )

        self.assertEqual(response.status_code, 200)


class GradesViewTest(TestCase):

    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            username="gradeuser",
            password="pass123",
            role="student"
        )

    @patch("users.views.requests.get")
    def test_grades_view(self, mock_get):

        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = []

        self.client.login(username="gradeuser", password="pass123")

        response = self.client.get(reverse("grades"))

        self.assertEqual(response.status_code, 200)