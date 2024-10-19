from django.contrib import admin

# Register your models here.
from .models import Discount,Margin,Payment

admin.site.register(Discount)
admin.site.register(Margin)
admin.site.register(Payment)
