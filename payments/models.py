from django.db import models
from pandit.models import booking
from django.contrib.auth.models import User

# Create your models here.

class Discount(models.Model):
    percentage = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 10 for 10% discount
    max_orders = models.PositiveIntegerField(default=1)  # Number of orders the discount is applicable for
    applied_orders = models.PositiveIntegerField(default=0)  # Track number of times the discount has been used
    is_active = models.BooleanField(default=True)  # Activate or deactivate the discount

    def is_valid(self):
        """Check if the discount is still applicable based on the max number of orders and if it's active."""
        return self.applied_orders < self.max_orders and self.is_active

    def apply_discount(self):
        """Increment the applied_orders count when the discount is used."""
        if self.is_valid():
            self.applied_orders += 1
            self.save()
            return True
        return False

    def __str__(self):
        return f"{self.percentage}% discount"


class Payment(models.Model):
    booking = models.ForeignKey(booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2)
    margin = models.DecimalField(max_digits=10, decimal_places=2)
    net_amount_for_pandit = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20)  # Adjust as needed
    # Add other fields as necessary
    
    
class Margin(models.Model):
    pandit_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pandit_margin")
    booking = models.ForeignKey(booking, on_delete=models.CASCADE)
    margin_percentage = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 10 for 10% margin
    margin_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount of margin

    def __str__(self):
        return f"Margin for Pandit: {self.pandit_id.username} - Booking: {self.booking.id}"
