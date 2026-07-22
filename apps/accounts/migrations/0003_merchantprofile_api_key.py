from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_teammember'),
    ]

    operations = [
        migrations.AddField(
            model_name='merchantprofile',
            name='api_key',
            field=models.CharField(blank=True, max_length=64, null=True, unique=True, verbose_name='Clé API'),
        ),
        migrations.AddField(
            model_name='merchantprofile',
            name='api_key_active',
            field=models.BooleanField(default=False, verbose_name='Clé API active'),
        ),
        migrations.AddField(
            model_name='merchantprofile',
            name='api_key_last_used',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Dernière utilisation API'),
        ),
    ]
