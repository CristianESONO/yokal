from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loyalty', '0008_fix_empty_reward_codes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reward',
            name='code',
            field=models.CharField(default='', editable=False, max_length=20, unique=True),
        ),
    ]
