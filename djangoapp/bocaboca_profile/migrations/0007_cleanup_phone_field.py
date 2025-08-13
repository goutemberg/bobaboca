# bocaboca_profile/migrations/0007_cleanup_phone_field.py
from django.db import migrations, models

def cleanup_phone(apps, schema_editor):
    NewUser = apps.get_model('bocaboca_profile', 'NewUser')
    # 1) '' -> NULL
    NewUser.objects.filter(phone='').update(phone=None)
    # 2) remover duplicatas, mantendo o 1º
    seen = set()
    for nu in NewUser.objects.exclude(phone__isnull=True).order_by('id'):
        if nu.phone in seen:
            nu.phone = None
            nu.save(update_fields=['phone'])
        else:
            seen.add(nu.phone)

class Migration(migrations.Migration):

    dependencies = [
        ('bocaboca_profile', '0006_alter_pendinguser_token'),
    ]

    operations = [
        # Primeiro: permitir NULL na coluna
        migrations.AlterField(
            model_name='newuser',
            name='phone',
            field=models.CharField(
                max_length=16,
                unique=True,
                null=True,        # <-- essencial
                blank=True,       # <-- opcional, mas ajuda no admin/forms
                db_index=True,
            ),
        ),
        # Depois: rodar a limpeza que usa NULL
        migrations.RunPython(cleanup_phone, reverse_code=migrations.RunPython.noop),
    ]
