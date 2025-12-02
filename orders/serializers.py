from rest_framework import serializers
from .models import Address, Order, OrderItem
from utils import phone_validator, pincode_validator


class AddressSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(
        max_length=10,
        min_length=10,
        validators=[phone_validator],
        error_messages={
            'required': 'Phone number is required.',
            'min_length': 'Phone number must be exactly 10 digits.',
            'max_length': 'Phone number must be exactly 10 digits.',
        }
    )
    
    pincode = serializers.CharField(
        max_length=6,
        min_length=6,
        validators=[pincode_validator],
        error_messages={
            'required': 'Pincode is required.',
            'min_length': 'Pincode must be exactly 6 digits.',
            'max_length': 'Pincode must be exactly 6 digits.',
        }
    )
    
    full_name = serializers.CharField(
        max_length=100,
        min_length=2,
        error_messages={
            'required': 'Full name is required.',
            'min_length': 'Full name must be at least 2 characters.',
            'max_length': 'Full name cannot exceed 100 characters.',
        }
    )
    
    street = serializers.CharField(
        max_length=255,
        min_length=5,
        error_messages={
            'required': 'Street address is required.',
            'min_length': 'Street address must be at least 5 characters.',
        }
    )
    
    city = serializers.CharField(
        max_length=100,
        min_length=2,
        error_messages={
            'required': 'City is required.',
            'min_length': 'City must be at least 2 characters.',
        }
    )
    
    class Meta:
        model = Address
        fields = ["id", "full_name", "phone", "street", "city", "pincode"]
        read_only_fields = []

    def create(self, validated_data):
        # NOTE: This create method relies on the 'request' context
        user = self.context["request"].user
        return Address.objects.create(user=user, **validated_data)


class OrderItemSerializer(serializers.ModelSerializer):
    # Use SerializerMethodField to handle cases where product is None (deleted)
    product_name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    stock = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "image", "quantity", "price", "category", "stock"]
        read_only_fields = ["product"]

    def get_product_name(self, obj):
        return obj.product.name if obj.product else "Product Unavailable"

    def get_image(self, obj):
        if obj.product and obj.product.image:
            return obj.product.image.url
        return None

    def get_category(self, obj):
        return obj.product.category if obj.product else "N/A"

    def get_stock(self, obj):
        return obj.product.stock if obj.product else 0


class OrderSerializer(serializers.ModelSerializer):
    # This ensures items are read correctly from the related_name (items)
    items = OrderItemSerializer(many=True, read_only=True)
    address = AddressSerializer(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)  # Format for frontend

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "address",
            "items",
            "total_amount",
            "payment_method",
            "payment_status",
            "order_status",
            "stripe_session_id",
            "created_at",
        ]
        read_only_fields = [
            "user",
            "address",
            "items",
            "payment_status",
            "order_status",
            "stripe_session_id",
            "created_at",
            "total_amount",  # Total amount should generally be calculated, not writable via API
        ]

    def create(self, validated_data):
        user = self.context["request"].user
        return Order.objects.create(user=user, **validated_data)