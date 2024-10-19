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
class CreateOrderView(View):
    def post(self, request, booking_id):
        from pandit.models import booking  # Ensure the correct import for Booking
        
        # Fetch the booking object using the correct model
        booking = get_object_or_404(booking, id=booking_id)  # Use the correct model name
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

        # Initial values for calculation
        original_amount = Decimal(booking.name_of_pooja.rate)  # Convert to Decimal
        total_discount_amount = Decimal(0)  # Use Decimal for total discount
        margin_amount = Decimal(0)  # Use Decimal for margin

        # Log the original amount
        print(f"Original Pooja Rate: {original_amount}")

        # Fetch all available discounts and apply valid ones
        discounts = Discount.objects.filter(is_active=True)
        if not discounts.exists():
            print("No discounts available.")

        for discount in discounts:
            print(f"Checking discount {discount.percentage}%")
            if discount.is_valid():
                discount_amount = (original_amount * Decimal(discount.percentage)) / Decimal(100)
                total_discount_amount += discount_amount
                discount.apply_discount()  # Update the discount usage
                print(f"Discount applied: {discount.percentage}%, Amount: {discount_amount}")
            else:
                print(f"Discount {discount.percentage}% is not valid or already applied.")

        # Check and apply referral code benefits
        if 'referral_code' in request.POST:
            referral_code_value = request.POST.get('referral_code')
            referral_code = get_object_or_404(ReferralCode, code=referral_code_value, is_active=True)
            print(f"Referral code {referral_code_value} is valid.")
            referral_discount_percentage = Decimal(5)  # Example: 5% discount for referral code
            referral_discount_amount = (original_amount * referral_discount_percentage) / Decimal(100)
            total_discount_amount += referral_discount_amount  # Add referral discount to total discount
            print(f"Referral discount applied: {referral_discount_percentage}%, Amount: {referral_discount_amount}")
        else:
            print("No referral code provided.")

        # Apply margin (assuming a fixed percentage for pandit)
        margin_percentage = Decimal(10)  # Example: 10% margin
        margin_amount = (original_amount * margin_percentage) / Decimal(100)
        net_amount_for_pandit = original_amount - margin_amount - total_discount_amount

        print(f"Total discount: {total_discount_amount}, Margin: {margin_amount}, Net amount for pandit: {net_amount_for_pandit}")

        # Create the Razorpay order
        payment_data = {
            "amount": int((original_amount - total_discount_amount) * Decimal(100)),  # Convert to paise
            "currency": "INR",
            "receipt": f"booking_{booking.id}",
            "payment_capture": "1"
        }
        razorpay_order = client.order.create(data=payment_data)
        
        print(f"Razorpay order created with amount: {payment_data['amount']}")

        # Save the payment information in the Payment model
        payment = Payment.objects.create(
            booking=booking,
            amount=original_amount - total_discount_amount,
            discount_applied=total_discount_amount,
            margin=margin_amount,
            net_amount_for_pandit=net_amount_for_pandit,
            payment_status="received"  # To be updated upon payment confirmation
        )
        

        mail_sub = "payment payment initiated"
        mail_body = "payment  initiated check the payment status "+booking.name
            
            
        send_custom_email(to_email=booking.pandit_id.email, subject=mail_sub, body=mail_body)

        # Save the margin details
        Margin.objects.create(
            pandit_id=booking.pandit_id,
            booking=booking,
            margin_percentage=margin_percentage,
            margin_amount=margin_amount
        )

        # Return Razorpay order details
        return JsonResponse(razorpay_order)

    def confirm_payment(self, payment_id, booking):
        """Confirm the payment and update the booking status."""
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
        payment = client.payment.fetch(payment_id)

        if payment['status'] == 'captured':
            # Update payment status in the Payment model
            Payment.objects.filter(booking=booking).update(payment_status="received")

            # Update the booking's payment status
            booking.payment_status = "recieved"  # Ensure this matches the field in the booking model
            booking.save()
            print("Payment confirmed and booking status updated.")
        else:
            print("Payment not captured or failed.")
