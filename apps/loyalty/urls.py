from django.urls import path
from . import views
from . import views_referral
from . import views_public
from . import views_templates

app_name = 'loyalty'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('card/<str:token>/', views.customer_card, name='customer_card'),
    path('stamp/<uuid:token>/', views.stamp_card, name='stamp_card'),
    path('scanner/', views.stamp_scanner, name='stamp_scanner'),
    path('new-card/', views.new_card, name='new_card'),
    path('program/', views.program_setup, name='program_setup'),
    path('reward/<int:reward_id>/redeem/', views.redeem_reward, name='redeem_reward'),
    path('program/<int:program_id>/join/', views.self_enroll, name='self_enroll'),
    path('program/<int:program_id>/qr/', views.program_qr, name='program_qr'),
    path('m/<slug:merchant_slug>/qr/', views.merchant_qr, name='merchant_qr'),
    path('card/qr/<uuid:token>/', views.customer_qr, name='customer_qr'),
    path('card/edit/<uuid:token>/', views.edit_card, name='edit_card'),
    path('program/<int:program_id>/delete/', views.delete_program, name='delete_program'),
    path('card/delete/<uuid:token>/', views.delete_card, name='delete_card'),
    path('join/<int:program_id>/', views.self_enroll),  # ancien lien, toujours supporté
    # Referral system
    path('referral/generate/<int:card_id>/', views_referral.generate_referral_code, name='generate_referral'),
    path('referral/apply/', views_referral.apply_referral_code, name='apply_referral'),
    path('referral/stats/', views_referral.referral_stats, name='referral_stats'),
    # Templates
    path('templates/', views_templates.get_templates, name='get_templates'),
    path('templates/<int:template_id>/apply/', views_templates.apply_template, name='apply_template'),
    # Public pages (SEO local)
    path('m/<slug:merchant_slug>/join/', views_public.merchant_self_enroll, name='merchant_enroll'),
    path('m/<slug:merchant_slug>/', views_public.merchant_public_page, name='public_merchant'),
    path('m/<slug:merchant_slug>/<slug:program_slug>/', views_public.program_public_page, name='public_program'),
]
