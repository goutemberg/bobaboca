# Generated by Django 5.1.4 on 2025-04-02 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bocaboca_profile', '0023_remove_newuser_interest_areas_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pendinguser',
            name='token',
            field=models.CharField(default='7Jmj9LEVERqvvqJCPlrecXRPhWQDiQC84jX1ZW8HdcfHKBGgztt2iz88s2JIJTZV', max_length=64, unique=True),
        ),
    ]
