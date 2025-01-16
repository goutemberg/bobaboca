# Generated by Django 5.1.4 on 2025-01-10 18:55

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bocaboca_profile', '0002_alter_address_city_alter_address_complement_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PendingUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=128)),
                ('token', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]