from django.db import migrations, models
from django.utils.text import slugify


def generate_slugs(apps, schema_editor):
    """Generate slugs for existing merchants."""
    MerchantProfile = apps.get_model('accounts', 'MerchantProfile')
    for merchant in MerchantProfile.objects.all():
        if not merchant.slug:
            base_slug = slugify(merchant.business_name)
            slug = base_slug
            counter = 1
            while MerchantProfile.objects.filter(slug=slug).exclude(pk=merchant.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            merchant.slug = slug
            merchant.save(update_fields=['slug'])


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0004_onboarding'),
    ]

    operations = [
        migrations.AddField(
            model_name='merchantprofile',
            name='slug',
            field=models.SlugField(max_length=200, unique=True, blank=True, null=True, verbose_name='Slug'),
        ),
        migrations.RunPython(generate_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='merchantprofile',
            name='slug',
            field=models.SlugField(max_length=200, unique=True, blank=True, null=True, verbose_name='Slug'),
        ),
    ]
