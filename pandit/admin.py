from django.contrib import admin
from pandit.models import pandit_profile,pandit_service,services,booking,services_type

# Register your models here.
admin.site.register(pandit_profile)
admin.site.register(pandit_service)

admin.site.register(services_type)

admin.site.register(services)
admin.site.register(booking)


