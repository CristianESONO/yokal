from django.contrib import admin
from .models import MerchantProfile, TeamMember


@admin.register(MerchantProfile)
class MerchantProfileAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'user', 'country', 'created_at')
    search_fields = ('business_name', 'user__email')
    list_filter = ('country', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('email', 'merchant', 'role', 'status', 'invitation_sent_at')
    list_filter = ('status', 'role', 'merchant')
    search_fields = ('email', 'merchant__business_name')
    readonly_fields = ('invitation_token', 'invitation_sent_at', 'created_at', 'updated_at')
    fieldsets = (
        ('Informations', {
            'fields': ('merchant', 'user', 'email', 'role', 'status')
        }),
        ('Invitation', {
            'fields': ('invitation_token', 'invitation_sent_at', 'joined_at')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )