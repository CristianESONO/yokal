# Generated migration for Apple Wallet fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loyalty', '0012_loyaltyprogram_ends_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='loyaltycard',
            name='apple_wallet_serial_number',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='loyaltycard',
            name='apple_wallet_linked',
            field=models.BooleanField(default=False),
        ),
    ]
