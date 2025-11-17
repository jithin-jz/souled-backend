from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Cart, CartItem, Wishlist, WishlistItem
from .serializers import (
    CartSerializer, AddToCartSerializer,
    WishlistSerializer, AddToWishlistSerializer
)
from products.models import Product


# Helpers
def get_user_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart

def get_user_wishlist(user):
    wishlist, created = Wishlist.objects.get_or_create(user=user)
    return wishlist


# ============================
# CART
# ============================
class CartDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = get_user_cart(request.user)
        return Response(CartSerializer(cart).data)


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = get_user_cart(request.user)
        product = get_object_or_404(Product, id=serializer.validated_data["product_id"])
        quantity = serializer.validated_data["quantity"]

        item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity

        item.save()
        return Response({"message": "Added to cart"})


class RemoveFromCartView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        cart = get_user_cart(request.user)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        item.delete()
        return Response({"message": "Removed"})


class UpdateCartQuantityView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, item_id):
        quantity = request.data.get("quantity")
        if not quantity or quantity < 1:
            return Response({"error": "Invalid quantity"}, status=400)

        cart = get_user_cart(request.user)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        item.quantity = quantity
        item.save()

        return Response({"message": "Quantity updated"})


# ============================
# WISHLIST
# ============================
class WishlistDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wishlist = get_user_wishlist(request.user)
        return Response(WishlistSerializer(wishlist).data)


class AddToWishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddToWishlistSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        wishlist = get_user_wishlist(request.user)
        product = get_object_or_404(Product, id=serializer.validated_data["product_id"])

        item, created = WishlistItem.objects.get_or_create(wishlist=wishlist, product=product)

        if not created:
            return Response({"message": "Already in wishlist"})

        return Response({"message": "Added to wishlist"})


class RemoveFromWishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        wishlist = get_user_wishlist(request.user)
        item = get_object_or_404(WishlistItem, id=item_id, wishlist=wishlist)
        item.delete()
        return Response({"message": "Removed from wishlist"})
