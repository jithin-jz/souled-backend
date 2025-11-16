from rest_framework_simplejwt.authentication import JWTAuthentication

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get("access")

        if not token:
            return None

        try:
            validated = self.get_validated_token(token)
        except Exception:
            return None

        user = self.get_user(validated)
        return (user, validated)
