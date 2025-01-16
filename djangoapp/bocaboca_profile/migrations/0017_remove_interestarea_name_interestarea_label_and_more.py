# Generated by Django 5.1.4 on 2025-01-13 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bocaboca_profile', '0016_pendinguser_nickname_alter_pendinguser_token'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='interestarea',
            name='name',
        ),
        migrations.AddField(
            model_name='interestarea',
            name='label',
            field=models.CharField(default='default_label', max_length=100),
        ),
        migrations.AlterField(
            model_name='pendinguser',
            name='token',
            field=models.CharField(default='HfnkNaf0bBI6jPFRUdg6mg7e9bJyMxG42jkCtvG72IIzrnrrQYfbMYd4JLmZLMAj', max_length=64, unique=True),
        ),
    ]
