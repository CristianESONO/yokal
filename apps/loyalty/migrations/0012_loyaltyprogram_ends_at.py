from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loyalty', '0011_loyaltyprogram_custom_html_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='loyaltyprogram',
            name='ends_at',
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name='Date de fin du programme',
                help_text='À cette date le programme est désactivé. Les cartes clients sont conservées.',
            ),
        ),
    ]
