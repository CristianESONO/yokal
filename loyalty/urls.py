from django.urls import path
from . import views

app_name = 'loyalty'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('card/<uuid:token>/', views.customer_card, name='customer_card'),
    path('stamp/<uuid:token>/', views.stamp_card, name='stamp_card'),
    path('scanner/', views.stamp_scanner, name='stamp_scanner'),
    path('new-card/', views.new_card, name='new_card'),
    path('program/', views.program_setup, name='program_setup'),
    path('reward/<int:reward_id>/redeem/', views.redeem_reward, name='redeem_reward'),
]
