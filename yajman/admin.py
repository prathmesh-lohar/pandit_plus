from django.contrib import admin

from yajman.models import yajman_profile,ReferralCode
# Register your models here.

admin.site.register(yajman_profile)


class ReferralCodeAdmin(admin.ModelAdmin):
    list_display = ('yajman', 'code', 'is_active', 'created_at')  # Fields to display in the list view
    search_fields = ('code',)  # Enable search by referral code
    list_filter = ('is_active',)  # Add a filter for active/inactive codes

    def has_add_permission(self, request):
        """Restrict adding new referral codes directly in admin."""
        return False  # Prevent adding via the admin, use the generate_code method instead

admin.site.register(ReferralCode, ReferralCodeAdmin)