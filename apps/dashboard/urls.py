from django.urls import path
from . import views
from . import views_export
from . import views_onboarding
from . import views_locations

app_name = 'dashboard'

urlpatterns = [
    path('', views.overview, name='overview'),
    path('customers/', views.customers, name='customers'),
    path('customers/<uuid:token>/approve/', views.approve_membership_view, name='approve_membership'),
    path('customers/<uuid:token>/reject/', views.reject_membership_view, name='reject_membership'),
    path('customers/<uuid:token>/revoke/', views.revoke_membership_view, name='revoke_membership'),
    path('scanner/', views.scanner, name='scanner'),
    path('stats/', views.stats, name='stats'),
    path('transactions/', views.transactions, name='transactions'),
    path('notifications/', views.notifications, name='notifications'),
    # Settings & Account
    path('programs/', views.programs, name='programs'),
    path('programs/switch/', views.switch_program, name='switch_program'),
    path('settings/', views.merchant_settings, name='settings'),
    path('settings/locations/', views_locations.locations_list, name='locations'),
    path('settings/locations/create/', views_locations.location_create, name='location_create'),
    path('settings/locations/<int:location_id>/edit/', views_locations.location_edit, name='location_edit'),
    path('settings/locations/<int:location_id>/delete/', views_locations.location_delete, name='location_delete'),
    path('account/', views.account, name='account'),
    path('billing/', views.billing, name='billing'),
    path('billing/checkout/<int:plan_id>/', views.billing_checkout, name='billing_checkout'),
    path('billing/success/', views.billing_success, name='billing_success'),
    path('billing/cancel/', views.billing_cancel, name='billing_cancel'),
    path('help/', views.help_page, name='help'),
    # Other
    path('customers/<uuid:card_id>/detail/', views.customer_detail_ajax, name='customer_detail_ajax'),
    # Exports
    path('export/customers/', views_export.export_customers_csv, name='export_customers'),
    path('export/transactions/', views_export.export_transactions_csv, name='export_transactions'),
    path('export/rewards/', views_export.export_rewards_csv, name='export_rewards'),
    # Onboarding
    path('onboarding/', views_onboarding.onboarding_checklist, name='onboarding'),
    path('onboarding/complete/<str:step_type>/', views_onboarding.mark_step_complete, name='onboarding_complete'),
    path('onboarding/status/', views_onboarding.get_onboarding_status, name='onboarding_status'),
]