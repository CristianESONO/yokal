from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import Currency, LoyaltyProgram, LoyaltyCard, StampHistory, Reward


@admin.register(Currency)
class CurrencyAdmin(ModelAdmin):
    list_display = ['code', 'name', 'symbol', 'is_active', 'updated_at']
    list_filter = ['is_active']


@admin.register(LoyaltyProgram)
class LoyaltyProgramAdmin(ModelAdmin):
    list_display = ['name', 'merchant', 'program_type', 'currency', 'card_template', 'reward_threshold', 'active']
    search_fields = ['name', 'merchant__business_name']
    list_filter = ['currency', 'program_type', 'active']


@admin.register(LoyaltyCard)
class LoyaltyCardAdmin(ModelAdmin):
    list_display = ['customer_name', 'program', 'balance', 'google_wallet_linked', 'created_at']
    search_fields = ['customer_name', 'customer_phone']
    readonly_fields = ['qr_token', 'google_wallet_object_id']


@admin.register(StampHistory)
class StampHistoryAdmin(ModelAdmin):
    list_display = ['card', 'amount', 'stamped_by', 'stamped_at']
    list_filter = ['stamped_at']


@admin.register(Reward)
class RewardAdmin(ModelAdmin):
    list_display = ['card', 'unlocked_at', 'redeemed', 'redeemed_at']
    list_filter = ['redeemed']
