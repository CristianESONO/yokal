from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('v1/programs/', views.list_programs, name='list_programs'),
    path('v1/customers/', views.list_customers, name='list_customers'),
    path('v1/customers/create/', views.create_customer, name='create_customer'),
    path('v1/customers/<uuid:token>/', views.get_customer, name='get_customer'),
    path('v1/customers/<uuid:token>/stamp/', views.stamp_customer, name='stamp_customer'),
    path('v1/rewards/<int:reward_id>/redeem/', views.redeem_reward, name='redeem_reward'),
]
