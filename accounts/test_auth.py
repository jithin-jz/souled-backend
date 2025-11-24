from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class AuthenticationTestCase(TestCase):
    """Test authentication endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.register_url = "/api/register/"
        self.login_url = "/api/login/"
        self.me_url = "/api/me/"
        self.logout_url = "/api/logout/"

        self.user_data = {
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }

    def test_register_creates_user(self):
        """Test user registration endpoint"""
        response = self.client.post(self.register_url, self.user_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["email"], self.user_data["email"])

        # Check that cookies are set
        self.assertIn("access", response.cookies)
        self.assertIn("refresh", response.cookies)

        # Verify user exists in database
        self.assertTrue(User.objects.filter(email=self.user_data["email"]).exists())

    def test_login_authenticates_user(self):
        """Test user login endpoint"""
        # First create a user
        User.objects.create_user(
            email=self.user_data["email"],
            password=self.user_data["password"],
            first_name=self.user_data["first_name"],
            last_name=self.user_data["last_name"],
        )

        # Now try to login
        login_data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"],
        }
        response = self.client.post(self.login_url, login_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["email"], self.user_data["email"])

        # Check that cookies are set
        self.assertIn("access", response.cookies)
        self.assertIn("refresh", response.cookies)

    def test_me_endpoint_with_authentication(self):
        """Test /me/ endpoint returns user data when authenticated"""
        # Register a user (this sets cookies)
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Get the access cookie
        access_cookie = response.cookies.get("access")
        self.assertIsNotNone(access_cookie)

        # Make request to /me/ endpoint with cookie
        self.client.cookies["access"] = access_cookie.value
        me_response = self.client.get(self.me_url)

        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response.data["email"], self.user_data["email"])

    def test_login_with_invalid_credentials(self):
        """Test login fails with invalid credentials"""
        User.objects.create_user(
            email=self.user_data["email"],
            password=self.user_data["password"],
        )

        # Try to login with wrong password
        login_data = {
            "email": self.user_data["email"],
            "password": "wrongpassword",
        }
        response = self.client.post(self.login_url, login_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_clears_cookies(self):
        """Test logout endpoint clears cookies"""
        # First login
        User.objects.create_user(
            email=self.user_data["email"],
            password=self.user_data["password"],
        )

        login_data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"],
        }
        login_response = self.client.post(self.login_url, login_data)
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        # Now logout
        logout_response = self.client.post(self.logout_url)
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)

        # Check that cookies have max_age=0 (which deletes them)
        access_cookie = logout_response.cookies.get("access")
        refresh_cookie = logout_response.cookies.get("refresh")

        # Cookies should be present in response but with deletion instructions
        self.assertIsNotNone(access_cookie)
        self.assertIsNotNone(refresh_cookie)
