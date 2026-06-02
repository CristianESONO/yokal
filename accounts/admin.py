from django.contrib import admin
from .models import MerchantProfile

@admin.register(MerchantProfile)
class MerchantProfileAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'user', 'phone', 'country', 'created_at']
    search_fields = ['business_name', 'user__email']
