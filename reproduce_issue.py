import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'store.settings')
django.setup()

from rest_framework.test import APIRequestFactory, force_authenticate
from orders.views import UserOrderListAPIView
from django.contrib.auth import get_user_model

User = get_user_model()

def test_orders():
    try:
        # Get the user with orders
        user = User.objects.get(email="exkiraaa@gmail.com")
        print(f"Testing with user: {user.email}")

        factory = APIRequestFactory()
        request = factory.get('/api/orders/my/')
        force_authenticate(request, user=user)

        view = UserOrderListAPIView.as_view()
        response = view(request)

        print(f"Status Code: {response.status_code}")
        if response.status_code != 200:
            print("Error Response:", response.data)
        else:
            print("Success! Orders found:", len(response.data))
            
    except Exception as e:
        print("Exception occurred:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_orders()
