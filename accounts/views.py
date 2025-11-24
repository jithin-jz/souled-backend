import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .authentication import AUTH_COOKIE_KEY, REFRESH_COOKIE_KEY

User = get_user_model()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")


def set_jwt_cookies(response, refresh: RefreshToken):
    """
    Attach access & refresh JWT tokens as HttpOnly cookies.
    Uses COOKIE_SECURE / COOKIE_SAMESITE from settings.
    """
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    secure = getattr(settings, "COOKIE_SECURE", False)
    samesite = getattr(settings, "COOKIE_SAMESITE", "Lax")

    cookie_args = {
        "httponly": True,
        "secure": secure,
        "samesite": samesite,
        "path": "/",
    }

    # Access token, 1 hour
    response.set_cookie(
        AUTH_COOKIE_KEY,
        access_token,
        max_age=3600,
        **cookie_args,
    )

    # Refresh token, 7 days
    response.set_cookie(
        REFRESH_COOKIE_KEY,
        refresh_token,
        max_age=3600 * 24 * 7,
        **cookie_args,
    )


@method_decorator(csrf_exempt, name="dispatch")
class RegisterView(APIView):
    """
    User registration - CSRF exempt since unauthenticated users
    don't have CSRF tokens yet.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        refresh = RefreshToken.for_user(user)

        response = Response(
            {"user": UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )
        set_jwt_cookies(response, refresh)
        return response


@method_decorator(csrf_exempt, name="dispatch")
class LoginView(APIView):
    """
    User login - CSRF exempt since unauthenticated users
    don't have CSRF tokens yet.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        response = Response(
            {"user": UserSerializer(user).data},
            status=status.HTTP_200_OK,
        )
        set_jwt_cookies(response, refresh)
        return response


@method_decorator(csrf_exempt, name="dispatch")
class GoogleLoginView(APIView):
    """
    Google OAuth login - CSRF exempt since the id_token verification
    provides sufficient security.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get("id_token")
        if not token:
            return Response(
                {"detail": "Missing id_token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

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
                {"user": UserSerializer(user).data, "created": created},
                status=status.HTTP_200_OK,
            )
            set_jwt_cookies(response, refresh)
            return response

        except Exception:
            return Response(
                {"detail": "Invalid Google token"},
                status=status.HTTP_400_BAD_REQUEST,
            )


@method_decorator(csrf_exempt, name="dispatch")
class LogoutView(APIView):
    """
    Logout: clear cookies regardless of auth state.
    CSRF exempt so it never fails on 403.
    """
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        response = Response({"message": "Logged out"}, status=200)
        response.delete_cookie(AUTH_COOKIE_KEY, path="/")
        response.delete_cookie(REFRESH_COOKIE_KEY, path="/")
        return response


class RefreshView(APIView):
    """
    Reads refresh cookie and issues a new access cookie.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get(REFRESH_COOKIE_KEY)
        if not refresh_token:
            return Response({"detail": "No refresh cookie"}, status=401)

        try:
            refresh = RefreshToken(refresh_token)
            new_access = refresh.access_token

            secure = getattr(settings, "COOKIE_SECURE", False)
            samesite = getattr(settings, "COOKIE_SAMESITE", "Lax")

            response = Response({"detail": "Access refreshed"}, status=200)
            response.set_cookie(
                AUTH_COOKIE_KEY,
                str(new_access),
                max_age=3600,
                httponly=True,
                secure=secure,
                samesite=samesite,
                path="/",
            )
            return response

        except Exception:
            return Response({"detail": "Refresh invalid"}, status=401)


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(
            UserSerializer(request.user).data,
            status=status.HTTP_200_OK,
        )
