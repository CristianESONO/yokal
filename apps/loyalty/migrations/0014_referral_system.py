# Generated migration for referral system

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('loyalty', '0013_loyaltycard_apple_wallet_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReferralCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(editable=False, max_length=12, unique=True, verbose_name='Code de parrainage')),
                ('uses_count', models.PositiveIntegerField(default=0, verbose_name="Nombre d'utilisations")),
                ('max_uses', models.PositiveIntegerField(default=10, verbose_name='Utilisations maximales')),
                ('bonus_amount', models.DecimalField(decimal_places=2, default=1.0, max_digits=10, verbose_name='Bonus par parrainage')),
                ('active', models.BooleanField(default=True, verbose_name='Actif')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True, verbose_name='Date d\'expiration')),
                ('card', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='referral_code', to='loyalty.loyaltycard', verbose_name='Carte du parrain')),
            ],
            options={
                'verbose_name': 'Code de parrainage',
                'verbose_name_plural': 'Codes de parrainage',
            },
        ),
        migrations.CreateModel(
            name='Referral',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bonus_given', models.BooleanField(default=False, verbose_name='Bonus accordé')),
                ('bonus_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Montant du bonus')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('referral_code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='referrals', to='loyalty.referralcode', verbose_name='Code de parrainage utilisé')),
                ('referred_card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='referrals_received', to='loyalty.loyaltycard', verbose_name='Carte du filleul')),
            ],
            options={
                'verbose_name': 'Parrainage',
                'verbose_name_plural': 'Parrainages',
            },
        ),
        migrations.AlterUniqueTogether(
            name='referral',
            unique_together={('referral_code', 'referred_card')},
        ),
    ]
