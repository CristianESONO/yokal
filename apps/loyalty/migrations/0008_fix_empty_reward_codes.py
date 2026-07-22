import secrets

from django.db import migrations


def fix_empty_reward_codes(apps, schema_editor):
    Reward = apps.get_model('loyalty', 'Reward')
    for reward in Reward.objects.filter(code=''):
        for _ in range(10):
            candidate = secrets.token_hex(6).upper()
            if not Reward.objects.filter(code=candidate).exists():
                reward.code = candidate
                reward.save(update_fields=['code'])
                break


class Migration(migrations.Migration):

    dependencies = [
        ('loyalty', '0007_alter_loyaltyprogram_merchant'),
    ]

    operations = [
        migrations.RunPython(fix_empty_reward_codes, migrations.RunPython.noop),
    ]
