from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
# Create your models here.


class pandit_profile(models.Model):
    pandit_id = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    mobile = models.CharField(validators=[phone_regex], max_length=17, blank=True)  # Validator ensures format
    

    alternative_mobile = models.CharField(blank=True,null=True, max_length=255) 
    email = models.EmailField(max_length=254)
    name = models.CharField(max_length=255, blank=True,null=True)
    last_name = models.CharField(max_length=255, blank=True,null=True)
    
    Exp =models.IntegerField()
    education=models.CharField(max_length=255,blank=True,null=True)
    collage=models.CharField(max_length=255,blank=True,null=True)
    address = models.TextField()
    latitude = models.CharField(max_length=50, blank=True , null=True)
    longitude = models.CharField(max_length=50, blank=True , null=True)
    dob = models.DateField(auto_now=False, auto_now_add=False,blank=True, null=True)
    
    profile_picture = models.ImageField(upload_to='pandit/profile_pic', blank=True, null=True)
    
    is_approved = models.BooleanField(default=False)
    
    availability_choices = [
        ('online', 'online'),
        ('busy', 'busy'),
        ('not_said', 'not_said'),
    ]
    availability = models.CharField(choices=availability_choices,default='not_said' ,max_length=50)
    
    
    
    def __str__(self):
        return f"{self.pandit_id.username} - {self.name}  - {self.availability} "
    
    
class services_type(models.Model):
    thumbnails = models.ImageField(upload_to="service_type_thumbnails")
    services_type = models.CharField(max_length=255, blank=True,null=True,default="")
    
    def __str__(self):
        return f"{self.services_type} "
    
class services(models.Model):
    services_type = models.ForeignKey(services_type, on_delete=models.CASCADE)
    service_name = models.CharField(max_length=255, blank=True,null=True,default="")
    
    def __str__(self):
        return f"{self.service_name} "
    
    
class pandit_service(models.Model):
    pandit_id = models.ForeignKey(User, on_delete=models.CASCADE)
    
    type_of_pooja = models.ForeignKey(services_type, on_delete=models.CASCADE)
    service = models.ForeignKey(services, on_delete=models.CASCADE, null=True, blank=True)
    
    rate_types = [
        ('perhour', 'perhour'),
        ('package', 'package'),
    ]
    rate_type = models.CharField(choices=rate_types, max_length=50)
    rate = models.IntegerField()
    
    def __str__(self):
        return f"{self.pandit_id.username} - {self.service.service_name} - {self.rate} - {self.get_rate_type_display()}"
    



class booking(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    time = models.TimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    locattion = models.TextField()
    name_of_pooja_category = models.ForeignKey(services_type,on_delete=models.CASCADE)
    name_of_pooja= models.ForeignKey(pandit_service, on_delete=models.CASCADE, blank=True, null=True)
    
    yajman_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='yajman_bookings')
    pandit_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pandit_id')

    book_status = [
        ('conformed', 'conformed'),
        ('rejected', 'rejected'),
        ('on_hold', 'on_hold'),
        ('requested', 'requested'),
    ]
    status = models.CharField(choices=book_status, max_length=50)
    conform_date = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    conform_time = models.TimeField(auto_now=False, auto_now_add=False, blank=True, null=True)

    pay_status = [
        ('received', 'received'),
        ('not_received', 'not_received'),
        ('failed', 'failed'),
    ]
    payment_status = models.CharField(choices=pay_status, max_length=50, default="not_received")

    def __str__(self):
        return f"{self.yajman_id.username} - {self.pandit_id.username} - {self.status}  - {self.payment_status}"
