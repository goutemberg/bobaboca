# Generated by Django 5.1.4 on 2025-01-11 04:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bocaboca_profile', '0011_alter_pendinguser_token_newuser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pendinguser',
            name='token',
            field=models.CharField(default='DbLecXa6oiSDGT0ZG8ambAhvvptBCDKFKxQq1DPrf4G3sksHU15oQ6hz81lBgmYp', max_length=64, unique=True),
        ),
    ]
