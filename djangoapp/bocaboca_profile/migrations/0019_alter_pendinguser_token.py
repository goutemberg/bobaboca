# Generated by Django 5.1.4 on 2025-01-13 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bocaboca_profile', '0018_alter_pendinguser_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pendinguser',
            name='token',
            field=models.CharField(default='sJqZ6YiYApxnMG3E8W41sZmNNPV0K9jCCGIJpil1PPdFGWdJyjCG4NdX5RhPET9q', max_length=64, unique=True),
        ),
    ]
