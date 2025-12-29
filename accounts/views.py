import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django_ratelimit.decorators import ratelimit

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer

User = get_user_model()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(ratelimit(key='ip', rate='3/h', method='POST'), name='dispatch')
class RegisterView(APIView):
    """
    User registration - returns JWT tokens in response body
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(ratelimit(key='ip', rate='5/15m', method='POST'), name='dispatch')
class LoginView(APIView):
    """
    User login - returns JWT tokens in response body
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(ratelimit(key='ip', rate='5/15m', method='POST'), name='dispatch')
class GoogleLoginView(APIView):
    """
    Google OAuth login - returns JWT tokens in response body
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
                clock_skew_in_seconds=10,
            )

            email = info["email"]
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": info.get("given_name", ""),
                    "last_name": info.get("family_name", ""),
                    "picture": info.get("picture", ""),
                },
            )

            # Update picture if it's new or changed
            if not created and info.get("picture") and user.picture != info.get("picture"):
                user.picture = info.get("picture")
                user.save()

            # Check if user is blocked
            if user.is_block:
                return Response(
                    {"detail": "Your account has been blocked. Please contact support."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "user": UserSerializer(user).data,
                    "created": created,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                status=status.HTTP_200_OK,
            )

        except Exception:
            return Response(
                {"detail": "Invalid Google token"},
                status=status.HTTP_400_BAD_REQUEST,
            )


@method_decorator(csrf_exempt, name="dispatch")
class LogoutView(APIView):
    """
    Logout: client-side should clear localStorage tokens
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        return Response({"message": "Logged out successfully"}, status=200)


@method_decorator(csrf_exempt, name="dispatch")
class RefreshView(APIView):
    """
    Accepts refresh token in request body and returns new access token
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "No refresh token provided"}, status=401)

        try:
            refresh = RefreshToken(refresh_token)
            # Get the user from the refresh token to check if blocked
            user_id = refresh.get('user_id')
            try:
                user = User.objects.get(id=user_id)
                if user.is_block:
                    return Response(
                        {"detail": "Your account has been blocked"},
                        status=403
                    )
            except User.DoesNotExist:
                return Response({"detail": "User not found"}, status=401)
            
            new_access = str(refresh.access_token)

            return Response(
                {"access": new_access},
                status=200
            )

        except Exception:
            return Response({"detail": "Refresh token invalid"}, status=401)


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(
            UserSerializer(request.user).data,
            status=status.HTTP_200_OK,
        )
