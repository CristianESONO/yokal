from django.urls import path

from . import views

app_name = 'billing'

urlpatterns = [
    path('paytech/ipn/', views.paytech_ipn, name='paytech_ipn'),
]
