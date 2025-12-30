import stripe
from django.conf import settings
from django.db import transaction
import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView

from .models import Order, OrderItem, Address
from .serializers import AddressSerializer, OrderSerializer
from products.models import Product

stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)


# ======================================================================
# CREATE ORDER (COD / STRIPE)
# ======================================================================
class CreateOrderAPIView(APIView):
    """
    Create order with COD or Stripe payment.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        cart = request.data.get("cart")
        address_data = request.data.get("address")
        address_id = request.data.get("address_id")
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
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Invalid cart format: {e}")
            return Response({"error": "Invalid cart format"}, status=400)

        # Use database transaction for data integrity
        try:
            with transaction.atomic():
                # Check stock availability for all items FIRST
                for item in cart:
                    try:
                        product = Product.objects.select_for_update().get(id=item["id"])
                    except Product.DoesNotExist:
                        return Response(
                            {"error": f"Product {item.get('name', 'unknown')} not found"},
                            status=404
                        )
                    
                    requested_qty = int(item["quantity"])
                    
                    if product.stock < requested_qty:
                        return Response(
                            {"error": f"Insufficient stock for {product.name}. Only {product.stock} available."},
                            status=400
                        )

                # Create Order
                order = Order.objects.create(
                    user=user,
                    address=address,
                    payment_method=payment_method,
                    total_amount=total_amount,
                    payment_status="unpaid",
                    order_status="processing",
                )

                logger.info(f"Order {order.id} created for user {user.email}")

                # Create Order Items and deduct stock
                for item in cart:
                    product = Product.objects.select_for_update().get(id=item["id"])
                    quantity = int(item["quantity"])
                    
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=float(item["price"]),
                    )
                    
                    # Deduct stock
                    product.stock -= quantity
                    product.save()
                    
                    logger.info(f"Stock deducted for {product.name}: {quantity} units")

                # Clear user's cart after order is created
                from cart.models import Cart
                try:
                    user_cart = Cart.objects.get(user=user)
                    user_cart.items.all().delete()
                except Cart.DoesNotExist:
                    pass

                # -------- COD LOGIC --------
                if payment_method == "cod":
                    # COD orders remain unpaid until delivery when payment is collected
                    # Admin will manually mark as paid after receiving payment
                    logger.info(f"COD order {order.id} confirmed")
                    return Response(
                        {
                            "message": "COD order placed",
                            "order_id": order.id,
                            "payment_method": "cod",
                            "payment_status": "unpaid",
                            "order_status": "processing"
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
                    
                    order.stripe_session_id = session.id
                    order.save()
                    logger.info(f"Stripe session {session.id} created for order {order.id}")
                    
                    return Response({"checkout_url": session.url}, status=200)
                    
                except Exception as e:
                    logger.error(f"Stripe error for order {order.id}: {str(e)}")
                    # No status change needed - order remains unpaid/processing
                    return Response({"error": str(e)}, status=500)

        except Exception as e:
            logger.error(f"Order creation error for user {user.email}: {str(e)}")
            return Response({"error": "Failed to create order"}, status=500)


# ======================================================================
# VERIFY PAYMENT (STRIPE + COD SUPPORT)
# ======================================================================
class VerifyPaymentAPIView(APIView):
    """
    Verify payment status.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        session_id = request.query_params.get("session_id")
        if not session_id:
            return Response({"error": "Missing session_id"}, status=400)

        # Retrieve Stripe session
        try:
            session = stripe.checkout.Session.retrieve(session_id)
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving session: {e}")
            return Response({"error": "Invalid session_id"}, status=400)
        except Exception as e:
            logger.exception(f"Unexpected error verifying payment: {e}")
            return Response({"error": "Payment verification failed"}, status=500)

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
                "payment_status": order.payment_status,
                "order_status": order.order_status,
                "payment_verified": True
            })

        # -------- STRIPE LOGIC --------
        if session.get("payment_status") == "paid" and order.payment_status == "unpaid":
            order.payment_status = "paid"
            order.save()
            logger.info(f"Payment verified for order {order.id}")

        return Response({
            "order_id": order.id,
            "payment_status": order.payment_status,
            "order_status": order.order_status,
            "payment_verified": session.get("payment_status") == "paid",
        })


# ======================================================================
# STRIPE WEBHOOK
# ======================================================================
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
        except Exception as e:
            logger.error(f"Webhook error: {str(e)}")
            return Response({"error": "Invalid signature or payload"}, status=400)

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            order_id = session["metadata"].get("order_id")

            if order_id:
                Order.objects.filter(id=order_id).update(payment_status="paid")
                logger.info(f"Webhook: Order {order_id} payment marked as paid")

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
        ).select_related('address').prefetch_related('items__product').order_by("-created_at")


# ======================================================================
# ADMIN: FETCH ALL ORDERS
# ======================================================================
class AdminOrderListAPIView(ListAPIView):
    """
    Admin-only endpoint to fetch all orders.
    """
    from rest_framework.permissions import IsAdminUser
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Order.objects.all().select_related(
            'address', 'user'
        ).prefetch_related('items__product').order_by("-created_at")


# ======================================================================
# ADMIN: UPDATE ORDER STATUS
# ======================================================================
class UpdateOrderStatusAPIView(APIView):
    """
    Admin-only endpoint to update order status.
    """
    from rest_framework.permissions import IsAdminUser
    permission_classes = [IsAdminUser]

    def patch(self, request, order_id):
        new_order_status = request.data.get("order_status", "").lower()
        new_payment_status = request.data.get("payment_status", "").lower()

        # Get order
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        # Validate and update order status if provided
        if new_order_status:
            valid_order_statuses = [choice[0] for choice in Order.ORDER_STATUS_CHOICES]
            if new_order_status not in valid_order_statuses:
                return Response(
                    {"error": f"Invalid order status. Must be one of: {', '.join(valid_order_statuses)}"},
                    status=400
                )
            order.order_status = new_order_status
            logger.info(f"Order {order.id} status updated to {new_order_status} by admin {request.user.email}")

        # Validate and update payment status if provided
        if new_payment_status:
            valid_payment_statuses = [choice[0] for choice in Order.PAYMENT_STATUS_CHOICES]
            if new_payment_status not in valid_payment_statuses:
                return Response(
                    {"error": f"Invalid payment status. Must be one of: {', '.join(valid_payment_statuses)}"},
                    status=400
                )
            order.payment_status = new_payment_status
            logger.info(f"Order {order.id} payment status updated to {new_payment_status} by admin {request.user.email}")

        order.save()

        # Return updated order
        serializer = OrderSerializer(order)
        return Response({
            "message": "Order updated successfully",
            "order": serializer.data
        }, status=200)


# ======================================================================
# CANCEL ORDER
# ======================================================================
class CancelOrderAPIView(APIView):
    """
    Allow user to cancel their order (only if status is 'processing')
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.select_related('user').prefetch_related('items__product').get(
                id=order_id, 
                user=request.user
            )
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        # Only allow cancellation if order is still processing
        if order.order_status != 'processing':
            return Response(
                {"error": f"Cannot cancel order with status '{order.order_status}'. Only 'processing' orders can be cancelled."},
                status=400
            )

        # Use transaction to ensure data integrity
        try:
            with transaction.atomic():
                # Restore stock for all items in the order
                for item in order.items.all():
                    if item.product:
                        product = Product.objects.select_for_update().get(id=item.product.id)
                        product.stock += item.quantity
                        product.save()
                        logger.info(f"Stock restored for {product.name}: +{item.quantity} units (Order #{order.id} cancelled)")

                # Update order status
                order.order_status = 'cancelled'
                order.save()

                logger.info(f"Order {order.id} cancelled by user {request.user.email}")

                return Response({
                    "message": "Order cancelled successfully",
                    "order_id": order.id,
                    "refund_info": "Your refund will be processed within 5-7 business days" if order.payment_status == 'paid' else None
                }, status=200)

        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {str(e)}")
            return Response({"error": "Failed to cancel order. Please try again."}, status=500)
