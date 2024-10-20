
# urls.py
from django.urls import path
from .views import CreateOrderView, ConfirmPaymentView

urlpatterns = [
    path('/create-order/<int:booking_id>', CreateOrderView.as_view(), name='create_order'),
     path('/confirm-payment', ConfirmPaymentView.as_view(), name='confirm_payment'),
    
]
