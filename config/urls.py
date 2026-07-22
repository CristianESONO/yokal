from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from apps.dashboard.views import (
    super_admin_overview,
    admin_marchands,
    admin_marchand_detail,
    admin_abonnements,
    admin_devises,
    admin_integrations,
    admin_logs,
    admin_parametres
)

urlpatterns = [
    # Register the django admin namespace (required internally by django.contrib.admin)
    # This URL is intentionally obscured and not linked anywhere in the UI.
    path('_sys/django-admin/', admin.site.urls),

    # Custom Admin Dashboard routes (replacing the django admin site interface entirely)
    path('admin/', super_admin_overview, name='admin_overview'),
    path('admin/marchands/', admin_marchands, name='admin_marchands'),
    path('admin/marchands/<int:merchant_id>/', admin_marchand_detail, name='admin_marchand_detail'),
    path('admin/abonnements/', admin_abonnements, name='admin_abonnements'),
    path('admin/devises/', admin_devises, name='admin_devises'),
    path('admin/integrations/', admin_integrations, name='admin_integrations'),
    path('admin/logs/', admin_logs, name='admin_logs'),
    path('admin/parametres/', admin_parametres, name='admin_parametres'),

    path('manifest.json', TemplateView.as_view(template_name='pwa/manifest.json', content_type='application/json'), name='manifest_json'),
    path('sw.js', TemplateView.as_view(template_name='pwa/sw.js', content_type='application/javascript'), name='sw_js'),
    path('offline/', TemplateView.as_view(template_name='pwa/offline.html'), name='offline'),
    path('', include('apps.loyalty.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('wallet/', include('apps.wallet.urls')),
    path('api/', include('apps.api.urls')),
    path('billing/', include('apps.billing.urls')),
    path('legal/', include('apps.loyalty.legal_urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



