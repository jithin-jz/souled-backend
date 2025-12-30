from django.urls import path
from .views import (
    CreateOrderAPIView,
    StripeWebhookAPIView,
    VerifyPaymentAPIView,
    UserOrderListAPIView,
    AdminOrderListAPIView,
    UpdateOrderStatusAPIView,
    CancelOrderAPIView,
)
from .address_views import (
    UserAddressListCreateView,
    UserAddressDetailView,
)

urlpatterns = [
    path("create/", CreateOrderAPIView.as_view(), name="order-create"),
    path("webhook/", StripeWebhookAPIView.as_view(), name="stripe-webhook"),
    path("verify-payment/", VerifyPaymentAPIView.as_view(), name="verify-payment"),
    path("my/", UserOrderListAPIView.as_view(), name="user-orders"),
    
    # Admin endpoints
    path("admin/all/", AdminOrderListAPIView.as_view(), name="admin-orders-list"),
    path("<int:order_id>/status/", UpdateOrderStatusAPIView.as_view(), name="update-order-status"),
    
    # User order management
    path("<int:order_id>/cancel/", CancelOrderAPIView.as_view(), name="cancel-order"),
    
    # Address management
    path("addresses/", UserAddressListCreateView.as_view(), name="address-list-create"),
    path("addresses/<int:address_id>/", UserAddressDetailView.as_view(), name="address-detail"),
]