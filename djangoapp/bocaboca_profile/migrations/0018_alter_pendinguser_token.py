# Generated by Django 5.1.4 on 2025-01-13 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bocaboca_profile', '0017_remove_interestarea_name_interestarea_label_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pendinguser',
            name='token',
            field=models.CharField(default='ItzQhNAednWYcON9ITXDjn33GohRUi6GwXiSEjpmyZj6B8bwiAzw54zgLGCcSBqj', max_length=64, unique=True),
        ),
    ]
