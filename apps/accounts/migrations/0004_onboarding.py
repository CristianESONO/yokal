# Generated migration for onboarding system

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_location'),
    ]

    operations = [
        migrations.CreateModel(
            name='OnboardingStep',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('step_type', models.CharField(choices=[('profile', 'Compléter le profil'), ('program', 'Créer un programme de fidélité'), ('card', 'Créer la première carte'), ('wallet', 'Configurer Google Wallet'), ('whatsapp', 'Connecter WhatsApp')], max_length=20, unique=True, verbose_name="Type d'étape")),
                ('completed', models.BooleanField(default=False, verbose_name='Complété')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='Date de complétion')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='onboarding_steps', to='accounts.merchantprofile', verbose_name='Marchand')),
            ],
            options={
                'verbose_name': "Étape d'onboarding",
                'verbose_name_plural': "Étapes d'onboarding",
            },
        ),
        migrations.CreateModel(
            name='OnboardingProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_step', models.CharField(choices=[('profile', 'Compléter le profil'), ('program', 'Créer un programme de fidélité'), ('card', 'Créer la première carte'), ('wallet', 'Configurer Google Wallet'), ('whatsapp', 'Connecter WhatsApp')], default='profile', max_length=20, verbose_name='Étape actuelle')),
                ('percentage', models.PositiveIntegerField(default=0, verbose_name='Pourcentage de complétion')),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('merchant', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='onboarding_progress', to='accounts.merchantprofile', verbose_name='Marchand')),
            ],
            options={
                'verbose_name': 'Progression d\'onboarding',
                'verbose_name_plural': 'Progressions d\'onboarding',
            },
        ),
        migrations.AlterUniqueTogether(
            name='onboardingstep',
            unique_together={('merchant', 'step_type')},
        ),
    ]
