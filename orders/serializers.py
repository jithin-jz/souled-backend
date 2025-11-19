from rest_framework import serializers
from .models import Address, Order, OrderItem


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        # Removed 'user' from fields list if it is handled via .create()
        fields = ["id", "full_name", "phone", "street", "city", "pincode"]
        read_only_fields = []

    def create(self, validated_data):
        # NOTE: This create method relies on the 'request' context
        user = self.context["request"].user
        return Address.objects.create(user=user, **validated_data)


class OrderItemSerializer(serializers.ModelSerializer):
    # These fields correctly fetch product data for read-only display
    product_name = serializers.CharField(source="product.name", read_only=True)
    image = serializers.CharField(source="product.image", read_only=True)
    
    class Meta:
        model = OrderItem
        # Keep 'product' for internal use, but read-only for display
        fields = ["id", "product", "product_name", "image", "quantity", "price"]
        read_only_fields = ["product"]


class OrderSerializer(serializers.ModelSerializer):
    # This ensures items are read correctly from the related_name (orderitem_set)
    items = OrderItemSerializer(many=True, read_only=True, source='orderitem_set')
    address = AddressSerializer(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True) # Format for frontend

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "address",
            "items",
            "total_amount",
            "payment_method",
            "status",
            "stripe_session_id",
            "created_at",
        ]
        read_only_fields = [
            "user",
            "address",
            "items",
            "status",
            "stripe_session_id",
            "created_at",
            "total_amount", # Total amount should generally be calculated, not writable via API
        ]

    def create(self, validated_data):
        user = self.context["request"].user
        return Order.objects.create(user=user, **validated_data)