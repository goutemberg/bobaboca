# Generated by Django 5.1.4 on 2025-01-10 22:52

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bocaboca_profile', '0004_alter_pendinguser_token'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pendinguser',
            name='email',
        ),
        migrations.RemoveField(
            model_name='pendinguser',
            name='name',
        ),
        migrations.RemoveField(
            model_name='pendinguser',
            name='password',
        ),
        migrations.AddField(
            model_name='pendinguser',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='pendinguser',
            name='token',
            field=models.CharField(default='qycjpZ9h9LAqqrC7ijEQ1uQUisey26xOjRfk8uTQwAYkLMBryZOTZV4RWEQlHBWN', max_length=64, unique=True),
        ),
    ]
