from django.urls import path
from . import views
from . import views_apple

app_name = 'wallet'

urlpatterns = [
    path('add/<uuid:token>/', views.add_to_wallet, name='add_to_wallet'),
    # Apple Wallet routes
    path('apple-pass/<int:card_id>/', views_apple.download_apple_pass, name='apple_pass_download'),
    path('apple-settings/', views_apple.apple_wallet_settings, name='apple_settings'),
]
