from django.urls import path
from .views import (
    CartDetailView, AddToCartView, RemoveFromCartView, UpdateCartQuantityView,
    WishlistDetailView, AddToWishlistView, RemoveFromWishlistView
)

urlpatterns = [
    # Cart
    path("", CartDetailView.as_view()),
    path("add/", AddToCartView.as_view()),
    path("remove/<int:item_id>/", RemoveFromCartView.as_view()),
    path("update/<int:item_id>/", UpdateCartQuantityView.as_view()),

    # Wishlist
    path("wishlist/", WishlistDetailView.as_view()),
    path("wishlist/add/", AddToWishlistView.as_view()),
    path("wishlist/remove/<int:item_id>/", RemoveFromWishlistView.as_view()),
]
