from django.urls import path
from . import legal_views

app_name = 'legal'

urlpatterns = [
    path('cgu/', legal_views.cgu, name='cgu'),
    path('confidentialite/', legal_views.privacy, name='privacy'),
    path('faq/', legal_views.faq, name='faq'),
]
