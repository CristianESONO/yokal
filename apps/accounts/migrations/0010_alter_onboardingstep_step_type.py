# Migration to remove unique=True from OnboardingStep.step_type
# The per-merchant uniqueness is already handled by unique_together = ['merchant', 'step_type']

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_alter_merchantprofile_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='onboardingstep',
            name='step_type',
            field=models.CharField(
                choices=[
                    ('profile', 'Compléter le profil'),
                    ('program', 'Créer un programme de fidélité'),
                    ('card', 'Créer la première carte'),
                    ('wallet', 'Configurer Google Wallet'),
                    ('whatsapp', 'Connecter WhatsApp'),
                ],
                max_length=20,
                verbose_name="Type d'étape",
            ),
        ),
    ]
