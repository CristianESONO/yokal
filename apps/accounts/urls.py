from django.urls import path
from . import views
from . import views_whatsapp

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('join-team/<str:token>/', views.join_team, name='join_team'),
    path('invite-team/', views.invite_team, name='invite_team'),
    path('cancel-invitation/<int:member_id>/', views.cancel_invitation, name='cancel_invitation'),
    path('remove-member/<int:member_id>/', views.remove_team_member, name='remove_team_member'),
    # WhatsApp
    path('whatsapp/connect/', views_whatsapp.connect_whatsapp, name='whatsapp_connect'),
    path('whatsapp/pairing-code/', views_whatsapp.whatsapp_pairing_code, name='whatsapp_pairing_code'),
    path('whatsapp/qrcode/', views_whatsapp.whatsapp_qrcode, name='whatsapp_qrcode'),
    path('whatsapp/status/', views_whatsapp.whatsapp_status, name='whatsapp_status'),
    path('whatsapp/disconnect/', views_whatsapp.disconnect_whatsapp, name='whatsapp_disconnect'),
    path('whatsapp/toggle/', views_whatsapp.toggle_whatsapp_notifications, name='whatsapp_toggle'),
    path('whatsapp/bulk-notify/', views_whatsapp.bulk_whatsapp_notification, name='whatsapp_bulk_notify'),
    path('whatsapp/settings/update/', views_whatsapp.update_whatsapp_settings, name='update_whatsapp_settings'),
]
