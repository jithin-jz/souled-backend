from rest_framework import serializers
from django.contrib.auth import get_user_model
from orders.serializers import OrderSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    isBlock = serializers.BooleanField(source="is_block")
    orders = OrderSerializer(many=True, read_only=True, source="order_set")

    class Meta:
        model = User
        fields = ["id", "email", "name", "role", "isBlock", "orders"]

    def get_name(self, obj):
        full = f"{obj.first_name} {obj.last_name}".strip()
        return full if full else obj.email.split("@")[0]

    def get_role(self, obj):
        return "admin" if obj.is_staff else "user"

