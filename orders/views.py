import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView

from .models import Order, OrderItem, Address
from .serializers import AddressSerializer, OrderSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY


# ======================================================================
# CREATE ORDER (COD / STRIPE)
# ======================================================================
@method_decorator(csrf_exempt, name="dispatch")
class CreateOrderAPIView(APIView):
    """
    Create order with COD or Stripe payment - CSRF exempt for authenticated users.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        cart = request.data.get("cart")
        address_data = request.data.get("address")
        address_id = request.data.get("address_id")  # NEW: Accept saved address ID
        payment_method = request.data.get("payment_method", "").lower()

        # Validate cart
        if not cart or not isinstance(cart, list):
            return Response({"error": "Cart is empty or invalid"}, status=400)
        if payment_method not in ("cod", "stripe"):
            return Response({"error": "Invalid payment method"}, status=400)

        # Handle Address - either use existing or create new
        if address_id:
            # Use existing saved address
            try:
                address = Address.objects.get(id=address_id, user=user)
            except Address.DoesNotExist:
                return Response({"error": "Address not found"}, status=404)
        elif address_data:
            # Create new address
            serializer = AddressSerializer(
                data=address_data,
                context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            address = serializer.save()
        else:
            return Response({"error": "Address is required"}, status=400)

        # Calculate total
        try:
            total_amount = sum(
                float(i["price"]) * int(i["quantity"]) for i in cart
            )
        except Exception:
            return Response({"error": "Invalid cart format"}, status=400)

        # Create Order
        order = Order.objects.create(
            user=user,
            address=address,
            payment_method=payment_method,
            total_amount=total_amount,
            status="pending",
        )

        # Create Order Items
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product_id=item["id"],
                quantity=int(item["quantity"]),
                price=float(item["price"]),
            )

        # Clear user's cart after order is created
        from cart.models import Cart
        try:
            user_cart = Cart.objects.get(user=user)
            user_cart.items.all().delete()  # Delete all cart items
        except Cart.DoesNotExist:
            pass  # No cart to clear

        # -------- COD LOGIC --------
        if payment_method == "cod":
            order.status = "processing"  # COD bypasses pending
            order.save()
            return Response(
                {
                    "message": "COD order placed",
                    "order_id": order.id,
                    "payment_method": "cod",
                    "status": "processing"
                },
                status=200,
            )

        # -------- STRIPE LOGIC --------
        try:
            session = stripe.checkout.Session.create(
                mode="payment",
                payment_method_types=["card"],
                metadata={"order_id": order.id},
                line_items=[
                    {
                        "price_data": {
                            "currency": "inr",
                            "product_data": {"name": item["name"]},
                            "unit_amount": int(float(item["price"]) * 100),
                        },
                        "quantity": int(item["quantity"]),
                    }
                    for item in cart
                ],
                success_url=f"{settings.FRONTEND_URL}/payment-success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.FRONTEND_URL}/payment",
            )
        except Exception as e:
            order.status = "failed"
            order.save()
            return Response({"error": str(e)}, status=500)

        order.stripe_session_id = session.id
        order.save()
        return Response({"checkout_url": session.url}, status=200)


# ======================================================================
# VERIFY PAYMENT (STRIPE + COD SUPPORT)
# ======================================================================
@method_decorator(csrf_exempt, name="dispatch")
class VerifyPaymentAPIView(APIView):
    """
    Verify payment status - CSRF exempt for authenticated users.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        session_id = request.query_params.get("session_id")
        if not session_id:
            return Response({"error": "Missing session_id"}, status=400)

        # Retrieve Stripe session
        try:
            session = stripe.checkout.Session.retrieve(session_id)
        except Exception:
            return Response({"error": "Invalid session_id"}, status=400)

        order_id = session.get("metadata", {}).get("order_id")
        if not order_id:
            return Response({"error": "Order metadata missing"}, status=400)

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        # -------- COD LOGIC --------
        if order.payment_method == "cod":
            return Response({
                "order_id": order.id,
                "status": order.status,
                "payment_verified": True
            })

        # -------- STRIPE LOGIC --------
        if session.get("payment_status") == "paid" and order.status == "pending":
            order.status = "paid"
            order.save()

        return Response({
            "order_id": order.id,
            "status": order.status,
            "payment_verified": session.get("payment_status") == "paid",
        })


# ======================================================================
# STRIPE WEBHOOK
# ======================================================================
@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookAPIView(APIView):

    def post(self, request):
        payload = request.body
        signature = request.headers.get("stripe-signature")

        try:
            event = stripe.Webhook.construct_event(
                payload,
                signature,
                settings.STRIPE_WEBHOOK_SECRET
            )
        except Exception:
            return Response({"error": "Invalid signature or payload"}, status=400)

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            order_id = session["metadata"].get("order_id")

            if order_id:
                Order.objects.filter(id=order_id).update(status="paid")

        return Response({"status": "success"}, status=200)


# ======================================================================
# FETCH ORDERS FOR USER
# ======================================================================
class UserOrderListAPIView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).order_by("-created_at")
