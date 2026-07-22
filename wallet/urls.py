from django.urls import path
from . import views

app_name = 'wallet'

urlpatterns = [
    path('add/<uuid:token>/', views.add_to_wallet, name='add_to_wallet'),
]
