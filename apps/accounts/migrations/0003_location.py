# Generated migration for Location model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_teammember'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Nom du point de vente')),
                ('address', models.TextField(blank=True, verbose_name='Adresse')),
                ('city', models.CharField(blank=True, max_length=100, verbose_name='Ville')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='Téléphone')),
                ('email', models.EmailField(blank=True, verbose_name='Email')),
                ('is_active', models.BooleanField(default=True, verbose_name='Actif')),
                ('is_main', models.BooleanField(default=False, verbose_name='Siège principal')),
                ('slug', models.SlugField(blank=True, max_length=255, unique=True, verbose_name='Slug')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='locations', to='accounts.merchantprofile', verbose_name='Marchand')),
            ],
            options={
                'verbose_name': 'Point de vente',
                'verbose_name_plural': 'Points de vente',
                'ordering': ['-is_main', 'name'],
            },
        ),
    ]
