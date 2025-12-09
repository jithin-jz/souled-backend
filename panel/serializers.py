from rest_framework import serializers
from django.contrib.auth import get_user_model
from orders.models import Order, OrderItem, Address
from products.models import Product

User = get_user_model()


# ================================
# Order (Mini Version)
# Used inside User Detail
# ================================
class OrderMiniSerializer(serializers.ModelSerializer):
    # Define nested serializers inline to avoid circular imports
    class AddressMiniSerializer(serializers.ModelSerializer):
        class Meta:
            model = Address
            fields = ["id", "full_name", "phone", "street", "city", "pincode"]
    
    class OrderItemMiniSerializer(serializers.ModelSerializer):
        product_name = serializers.SerializerMethodField()
        image = serializers.SerializerMethodField()
        
        class Meta:
            model = OrderItem
            fields = ["id", "product", "product_name", "image", "quantity", "price"]
        
        def get_product_name(self, obj):
            return obj.product.name if obj.product else "Product Unavailable"
        
        def get_image(self, obj):
            if obj.product and obj.product.image:
                return obj.product.image.url
            return None
    
    items = OrderItemMiniSerializer(many=True, read_only=True)
    address = AddressMiniSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = ["id", "total_amount", "order_status", "payment_method", "created_at", "items", "address"]


# ================================
# Light User Serializer (List)
# Fast, no heavy relations
# ================================
class AdminUserListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    isBlock = serializers.BooleanField(source="is_block")

    class Meta:
        model = User
        fields = ["id", "email", "name", "role", "isBlock"]

    def get_name(self, obj):
        full = f"{obj.first_name} {obj.last_name}".strip()
        return full or obj.email.split("@")[0]

    def get_role(self, obj):
        return "admin" if obj.is_staff else "user"


# ================================
# Heavy User Serializer (Detail)
# Includes user orders
# ================================
class AdminUserDetailSerializer(AdminUserListSerializer):
    orders = OrderMiniSerializer(many=True, read_only=True, source="order_set")

    class Meta(AdminUserListSerializer.Meta):
        fields = AdminUserListSerializer.Meta.fields + ["orders"]


# ================================
# Product Serializer (Dashboard)
# ================================
class ProductMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "stock", "price"]


# ================================
# Order Serializer (Dashboard)
# ================================
class OrderDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "total_amount", "payment_method", "order_status", "created_at"]
