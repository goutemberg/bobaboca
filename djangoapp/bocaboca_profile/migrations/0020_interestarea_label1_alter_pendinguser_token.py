# Generated by Django 5.1.4 on 2025-01-13 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bocaboca_profile', '0019_alter_pendinguser_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='interestarea',
            name='label1',
            field=models.CharField(default='default_label', max_length=100),
        ),
        migrations.AlterField(
            model_name='pendinguser',
            name='token',
            field=models.CharField(default='LQ1HswE39PI5euK07nNLKzVj8DzaHb1sI2iQhjBZ5vyEwkkk86bhwZkpa1h9AhwP', max_length=64, unique=True),
        ),
    ]
