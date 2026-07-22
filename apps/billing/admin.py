from django.contrib import admin
from django.utils.html import format_html

from .models import MerchantSubscription, SubscriptionPayment, SubscriptionPlan


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'currency', 'is_active', 'is_trial', 'is_popular', 'sort_order')
    list_filter = ('is_active', 'is_trial', 'is_popular')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'slug', 'description', 'is_active', 'is_popular', 'sort_order')
        }),
        ('Tarification', {
            'fields': ('price', 'currency', 'billing_period_days', 'is_trial')
        }),
        ('Limites', {
            'fields': ('max_cards', 'max_programs')
        }),
        ('Fonctionnalités incluses', {
            'fields': ('includes_api', 'includes_whatsapp_unlimited', 'includes_google_wallet', 'features')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('subscriptions')


@admin.register(MerchantSubscription)
class MerchantSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('merchant', 'plan', 'status', 'current_period_end', 'trial_ends_at', 'is_compliant')
    list_filter = ('status', 'plan')
    search_fields = ('merchant__business_name', 'merchant__user__email')
    readonly_fields = ('created_at', 'updated_at', 'is_compliant', 'days_until_renewal')
    
    fieldsets = (
        ('Informations', {
            'fields': ('merchant', 'plan', 'status', 'auto_renew')
        }),
        ('Période', {
            'fields': ('trial_ends_at', 'current_period_start', 'current_period_end')
        }),
        ('Notifications', {
            'fields': ('renewal_notified_at',)
        }),
        ('Informations système', {
            'fields': ('is_compliant', 'days_until_renewal', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_compliant(self, obj):
        return format_html('<span style="color: {}">{}</span>', 
                          'green' if obj.is_compliant else 'red',
                          '✓' if obj.is_compliant else '✗')
    is_compliant.short_description = 'Conforme'
    is_compliant.boolean = True


@admin.register(SubscriptionPayment)
class SubscriptionPaymentAdmin(admin.ModelAdmin):
    list_display = ('ref_command', 'merchant', 'plan', 'amount', 'status', 'payment_type', 'paid_at')
    list_filter = ('status', 'payment_type')
    search_fields = ('ref_command', 'merchant__business_name')
    readonly_fields = ('created_at', 'paid_at', 'paytech_payload')
    
    fieldsets = (
        ('Informations', {
            'fields': ('merchant', 'plan', 'amount', 'currency', 'status', 'payment_type')
        }),
        ('Références', {
            'fields': ('ref_command', 'paytech_token', 'payment_method')
        }),
        ('Période', {
            'fields': ('period_start', 'period_end')
        }),
        ('Informations système', {
            'fields': ('paid_at', 'created_at', 'paytech_payload'),
            'classes': ('collapse',)
        }),
    )
