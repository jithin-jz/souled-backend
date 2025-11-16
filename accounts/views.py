from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings

from .serializers import RegisterSerializer, UserSerializer, LoginSerializer
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

import os

User = get_user_model()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")


# ---------------------------------------------------------
# COOKIE SETTER (fixed lifetime, sameSite, httpOnly)
# ---------------------------------------------------------
def set_jwt_cookies(response, refresh: RefreshToken):
    access = str(refresh.access_token)
    refresh_token = str(refresh)

    # Access token (1 hour)
    response.set_cookie(
        "access",
        access,
        max_age=3600,
        httponly=True,
        secure=False,        # True in production (HTTPS only)
        samesite="Lax",
        path="/",
    )

    # Refresh token (7 days)
    response.set_cookie(
        "refresh",
        refresh_token,
        max_age=3600 * 24 * 7,
        httponly=True,
        secure=False,
        samesite="Lax",
        path="/",
    )


# ---------------------------------------------------------
# REGISTER
# ---------------------------------------------------------
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        user = serializer.save()
        refresh = RefreshToken.for_user(user)

        response = Response(
            {"user": UserSerializer(user).data},
            status=201
        )

        set_jwt_cookies(response, refresh)
        return response


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        response = Response(
            {"user": UserSerializer(user).data},
            status=200
        )

        set_jwt_cookies(response, refresh)
        return response


# ---------------------------------------------------------
# GOOGLE LOGIN
# ---------------------------------------------------------
class GoogleLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get("id_token")

        if not token:
            return Response({"detail": "Missing id_token"}, status=400)

        try:
            info = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                GOOGLE_CLIENT_ID,
            )

            email = info["email"]

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": info.get("given_name", ""),
                    "last_name": info.get("family_name", ""),
                },
            )

            refresh = RefreshToken.for_user(user)

            response = Response(
                {
                    "user": UserSerializer(user).data,
                    "created": created,
                },
                status=200,
            )

            set_jwt_cookies(response, refresh)
            return response

        except Exception:
            return Response({"detail": "Invalid Google token"}, status=400)


# ---------------------------------------------------------
# LOGOUT
# ---------------------------------------------------------
class LogoutView(APIView):
    def post(self, request):
        response = Response({"message": "Logged out"}, status=200)
        response.delete_cookie("access")
        response.delete_cookie("refresh")
        return response


# ---------------------------------------------------------
# ME
# ---------------------------------------------------------
class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
