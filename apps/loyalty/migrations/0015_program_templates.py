# Generated migration for program templates

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loyalty', '0014_referral_system'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProgramTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('business_type', models.CharField(choices=[('bakery', 'Boulangerie'), ('hair_salon', 'Coiffure'), ('cafe', 'Café'), ('restaurant', 'Restaurant'), ('retail', 'Commerce de détail'), ('gym', 'Salle de sport'), ('car_wash', 'Lavage auto')], max_length=20, unique=True, verbose_name='Type de commerce')),
                ('name', models.CharField(max_length=200, verbose_name='Nom du template')),
                ('description', models.TextField(verbose_name='Description')),
                ('program_type', models.CharField(choices=[('visits', 'Visites'), ('points', 'Points')], default='visits', max_length=20, verbose_name='Type de programme')),
                ('reward_threshold', models.PositiveIntegerField(default=10, verbose_name='Seuil pour récompense')),
                ('reward_description', models.CharField(default='1 article offert', max_length=255, verbose_name='Description de la récompense')),
                ('reward_value', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Valeur de la récompense')),
                ('unit_label', models.CharField(default='Tampon', max_length=20, verbose_name='Libellé de l\'unité')),
                ('color_primary', models.CharField(default='#0E0F0D', max_length=7, verbose_name='Couleur principale')),
                ('color_secondary', models.CharField(default='#D4FF4E', max_length=7, verbose_name='Couleur secondaire')),
                ('card_template', models.CharField(choices=[('classic', 'Classique'), ('glass', 'Verre'), ('bold', 'Bold'), ('luxury', 'Luxe')], default='classic', max_length=20, verbose_name='Modèle de carte')),
                ('is_active', models.BooleanField(default=True, verbose_name='Actif')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Template de programme',
                'verbose_name_plural': 'Templates de programmes',
            },
        ),
    ]
