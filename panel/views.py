from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, DestroyAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.contrib.auth import get_user_model

from orders.models import Order
from products.models import Product

from .serializers import (
    AdminUserListSerializer,
    AdminUserDetailSerializer,
    OrderDashboardSerializer,
    ProductMiniSerializer
)

User = get_user_model()


# ================================
# USER LIST
# Lightweight, optimized for speed
# ================================
class AdminUserList(ListAPIView):
    queryset = User.objects.all().order_by("-id")
    serializer_class = AdminUserListSerializer
    permission_classes = [IsAdminUser]


# ================================
# USER DETAIL
# Heavy, includes order history
# ================================
class AdminUserDetail(RetrieveAPIView):
    queryset = User.objects.select_related().all()
    serializer_class = AdminUserDetailSerializer
    lookup_field = "id"
    permission_classes = [IsAdminUser]


# ================================
# TOGGLE USER BLOCK
# Simple boolean flip action
# ================================
class AdminToggleBlockUser(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, id):
        user = get_object_or_404(User, id=id)
        user.is_block = not user.is_block
        user.save(update_fields=["is_block"])
        return Response({"status": "success", "isBlock": user.is_block})


# ================================
# DELETE USER
# Uses DRF Delete mixin
# ================================
class AdminDeleteUser(DestroyAPIView):
    queryset = User.objects.all()
    lookup_field = "id"
    permission_classes = [IsAdminUser]

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)
        return Response({"status": "deleted"})


# ================================
# DASHBOARD STATS
# Counts + revenue + recent orders
# ================================
class DashboardStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_users = User.objects.count()
        total_products = Product.objects.count()
        total_orders = Order.objects.count()

        total_revenue = (
            Order.objects.filter(payment_status="paid")
            .aggregate(total=Sum("total_amount"))["total"] or 0
        )

        recent_orders = (
            Order.objects.select_related("user")
            .order_by("-created_at")[:5]
        )
        recent_orders_data = OrderDashboardSerializer(recent_orders, many=True).data

        # Group products by category
        category_stats = (
            Product.objects.values("category")
            .annotate(count=Count("id"))
        )
        category_data = [
            {"name": item["category"], "count": item["count"]}
            for item in category_stats
        ]

        low_stock = Product.objects.order_by("stock")[:5]
        low_stock_data = ProductMiniSerializer(low_stock, many=True).data

        return Response({
            "total_users": total_users,
            "total_products": total_products,
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "recent_orders": recent_orders_data,
            "category_data": category_data,
            "low_stock_products": low_stock_data,
        })


# ================================
# REPORTS
# Revenue timeline, statuses, methods
# ================================
class AdminReportsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        paid = Order.objects.filter(payment_status="paid")

        total_orders = Order.objects.count()
        total_revenue = paid.aggregate(total=Sum("total_amount"))["total"] or 0

        # Revenue grouped by date
        timeline = (
            paid.annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(total=Sum("total_amount"))
            .order_by("date")
        )
        revenue_timeline = [
            {"name": item["date"].isoformat(), "total": item["total"]}
            for item in timeline
        ]

        payment_dist = [
            {
                "name": (item["payment_method"] or "Unknown").upper(),
                "count": item["count"],
            }
            for item in Order.objects.values("payment_method")
            .annotate(count=Count("id"))
        ]

        status_dist = [
            {
                "name": (item["order_status"] or "").title(),
                "count": item["count"],
            }
            for item in Order.objects.values("order_status")
            .annotate(count=Count("id"))
        ]

        return Response({
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "revenue_timeline": revenue_timeline,
            "payment_distribution": payment_dist,
            "status_distribution": status_dist,
        })
