
# urls.py
from django.urls import path
from .views import CreateOrderView

urlpatterns = [
    path('/create-order/<int:booking_id>', CreateOrderView.as_view(), name='create_order'),
]
