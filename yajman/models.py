from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils.crypto import get_random_string

# Create your models here.

class yajman_profile(models.Model):
    yajman_id = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    mobile = models.CharField(validators=[phone_regex], max_length=17, blank=True)  # Validator ensures format
    email = models.EmailField(max_length=254)
    name = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField()
    profile_picture = models.ImageField(upload_to='pandit/profile_pic', null=True, blank=True)
    latitude = models.CharField(max_length=50, blank=True, null=True)
    longitude = models.CharField(max_length=50, blank=True, null=True)
    


    def __str__(self):
        return f"{self.yajman_id.username} - {self.name}"

class ReferralCode(models.Model):
    yajman = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=10, unique=True)
    is_active = models.BooleanField(default=True)  # To deactivate if needed
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_code(self):
        """Generate a unique referral code."""
        self.code = get_random_string(8).upper()  # Generate 8-character code
        self.save()

    def __str__(self):
        return self.code

