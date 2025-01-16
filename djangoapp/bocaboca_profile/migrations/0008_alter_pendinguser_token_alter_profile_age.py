# Generated by Django 5.1.4 on 2025-01-11 01:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bocaboca_profile', '0007_alter_pendinguser_token_alter_profile_birth'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pendinguser',
            name='token',
            field=models.CharField(default='pxh80OdBlW2WAQ16cEqo27XrgAIvJiBLnswRCUwl2uQt3JC0CDHQv2oJzePw5QVq', max_length=64, unique=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='age',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
