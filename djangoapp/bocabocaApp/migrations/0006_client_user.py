# Generated by Django 5.1.4 on 2025-04-03 23:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bocabocaApp', '0005_client'),
        ('bocaboca_profile', '0025_customuser_review_delete_interestarea_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='bocaboca_profile.customuser'),
        ),
    ]
