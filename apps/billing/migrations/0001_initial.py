# Generated manually for apps.billing

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0003_merchantprofile_api_key'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubscriptionPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
                ('description', models.TextField(blank=True)),
                ('price', models.DecimalField(decimal_places=0, default=0, max_digits=12)),
                ('currency', models.CharField(default='XOF', max_length=3)),
                ('billing_period_days', models.PositiveIntegerField(default=30)),
                ('max_cards', models.PositiveIntegerField(blank=True, help_text='Vide = illimité', null=True)),
                ('max_programs', models.PositiveIntegerField(blank=True, help_text='Vide = illimité', null=True)),
                ('includes_api', models.BooleanField(default=False)),
                ('includes_whatsapp_unlimited', models.BooleanField(default=False)),
                ('includes_google_wallet', models.BooleanField(default=False)),
                ('is_trial', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_popular', models.BooleanField(default=False)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('features', models.JSONField(blank=True, default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['sort_order', 'price'],
            },
        ),
        migrations.CreateModel(
            name='MerchantSubscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('trialing', 'Essai'), ('active', 'Actif'), ('past_due', 'En retard'), ('expired', 'Expiré'), ('canceled', 'Annulé')], default='trialing', max_length=20)),
                ('trial_ends_at', models.DateTimeField(blank=True, null=True)),
                ('current_period_start', models.DateTimeField(blank=True, null=True)),
                ('current_period_end', models.DateTimeField(blank=True, null=True)),
                ('auto_renew', models.BooleanField(default=True)),
                ('renewal_notified_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('merchant', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='subscription', to='accounts.merchantprofile')),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='subscriptions', to='billing.subscriptionplan')),
            ],
            options={
                'verbose_name': 'Abonnement marchand',
            },
        ),
        migrations.CreateModel(
            name='SubscriptionPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=0, max_digits=12)),
                ('currency', models.CharField(default='XOF', max_length=3)),
                ('status', models.CharField(choices=[('pending', 'En attente'), ('completed', 'Payé'), ('failed', 'Échoué'), ('canceled', 'Annulé')], default='pending', max_length=20)),
                ('payment_type', models.CharField(choices=[('subscription', 'Souscription'), ('renewal', 'Renouvellement')], default='subscription', max_length=20)),
                ('ref_command', models.CharField(max_length=100, unique=True)),
                ('paytech_token', models.CharField(blank=True, max_length=100)),
                ('payment_method', models.CharField(blank=True, max_length=100)),
                ('paytech_payload', models.JSONField(blank=True, default=dict)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('period_start', models.DateTimeField(blank=True, null=True)),
                ('period_end', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscription_payments', to='accounts.merchantprofile')),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='billing.subscriptionplan')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
