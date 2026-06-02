from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.overview, name='overview'),
    path('customers/', views.customers, name='customers'),
    path('scanner/', lambda r: redirect('loyalty:stamp_scanner'), name='stamp_scanner'),
    path('yokal-admin/', views.super_admin_overview, name='super_admin_overview'),
]
