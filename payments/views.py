from django.http import JsonResponse
from django.views import View
from django.shortcuts import get_object_or_404
from decimal import Decimal
from django.conf import settings
import razorpay
from payments.models import Margin, Payment, Discount
from pandit.models import booking  # Ensure the correct import for Booking
from yajman.models import ReferralCode
from pandit.mail import send_custom_email
import json

class CreateOrderView(View):
    def post(self, request, booking_id):
        # Fetch the booking object using the correct model
        booking_obj = get_object_or_404(booking, id=booking_id)  # Use the correct model name
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

        # Initial values for calculation
        original_amount = Decimal(booking_obj.name_of_pooja.rate)  # Convert to Decimal
        total_discount_amount = Decimal(0)  # Use Decimal for total discount
        margin_amount = Decimal(0)  # Use Decimal for margin

        # Log the original amount
        print(f"Original Pooja Rate: {original_amount}")

        # Fetch and apply discounts
        discounts = Discount.objects.filter(is_active=True)
        for discount in discounts:
            if discount.is_valid():
                discount_amount = (original_amount * Decimal(discount.percentage)) / Decimal(100)
                total_discount_amount += discount_amount
                discount.apply_discount()  # Update the discount usage

        # Apply referral code benefits (if provided)
        if 'referral_code' in request.POST:
            referral_code_value = request.POST.get('referral_code')
            referral_code = get_object_or_404(ReferralCode, code=referral_code_value, is_active=True)
            referral_discount_percentage = Decimal(5)  # Example: 5% discount for referral code
            referral_discount_amount = (original_amount * referral_discount_percentage) / Decimal(100)
            total_discount_amount += referral_discount_amount

        # Apply margin
        margin_percentage = Decimal(10)  # Example: 10% margin
        margin_amount = (original_amount * margin_percentage) / Decimal(100)
        net_amount_for_pandit = original_amount - margin_amount - total_discount_amount

        # Create the Razorpay order
        payment_data = {
            "amount": int((original_amount - total_discount_amount) * Decimal(100)),  # Convert to paise
            "currency": "INR",
            "receipt": f"booking_{booking_obj.id}",
            "payment_capture": "1"
        }
        razorpay_order = client.order.create(data=payment_data)

        # Save the payment information in the Payment model
        payment = Payment.objects.create(
            booking=booking_obj,
            amount=original_amount - total_discount_amount,
            discount_applied=total_discount_amount,
            margin=margin_amount,
            net_amount_for_pandit=net_amount_for_pandit,
            payment_status="pending"  # Initially mark it as pending
        )

        # Send an email to the pandit
        mail_sub = "Payment Initiated"
        mail_body = f"Payment initiated for the booking of {booking_obj.name}"
        send_custom_email(to_email=booking_obj.pandit_id.email, subject=mail_sub, body=mail_body)

        # Save the margin details
        Margin.objects.create(
            pandit_id=booking_obj.pandit_id,
            booking=booking_obj,
            margin_percentage=margin_percentage,
            margin_amount=margin_amount
        )

        # Return Razorpay order details
        return JsonResponse(razorpay_order)

    def confirm_payment(self, payment_id, booking_id):
        """Confirm the payment and update the booking status."""
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
        payment = client.payment.fetch(payment_id)

        # Fetch the booking object
        booking_obj = get_object_or_404(booking, id=booking_id)

        if payment['status'] == 'captured':
            # Update payment status in the Payment model
            Payment.objects.filter(booking=booking_obj).update(payment_status="received")

            # Update the booking's payment status
            booking_obj.payment_status = "received"  # Correct spelling of 'received'
            print("rc obj")
            booking_obj.save()
            print("Payment confirmed and booking status updated.")
        else:
            print("Payment not captured or failed.")


class ConfirmPaymentView(View):
    def post(self, request):
        data = json.loads(request.body)
        payment_id = data.get('payment_id')
        booking_id = data.get('booking_id')

        if not payment_id or not booking_id:
            return JsonResponse({'error': 'Invalid payment or booking ID'}, status=400)

        # Fetch booking and verify payment
        booking_obj = get_object_or_404(booking, id=booking_id)
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
        payment = client.payment.fetch(payment_id)

        if payment['status'] == 'captured':
            # Update the Payment model
            Payment.objects.filter(booking=booking_obj).update(payment_status="received")

            # Update the booking's payment status
            booking_obj.payment_status = "received"  # Ensure the correct field spelling
            booking_obj.save()

            return JsonResponse({'status': 'success', 'message': 'Payment confirmed'})
        else:
            return JsonResponse({'status': 'failed', 'message': 'Payment not captured'}, status=400)