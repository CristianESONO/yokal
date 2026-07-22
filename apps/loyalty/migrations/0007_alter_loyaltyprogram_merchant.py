from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_teammember'),
        ('loyalty', '0006_alter_currency_options_alter_loyaltycard_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loyaltyprogram',
            name='merchant',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='programs',
                to='accounts.merchantprofile',
                verbose_name='Commerçant',
            ),
        ),
    ]
