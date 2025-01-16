# Generated by Django 5.1.4 on 2025-01-09 19:16

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bocaboca_profile', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='city',
            field=models.CharField(max_length=50, verbose_name='Cidade'),
        ),
        migrations.AlterField(
            model_name='address',
            name='complement',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Complemento'),
        ),
        migrations.AlterField(
            model_name='address',
            name='neighborhood',
            field=models.CharField(max_length=50, verbose_name='Bairro'),
        ),
        migrations.AlterField(
            model_name='address',
            name='number',
            field=models.CharField(max_length=10, verbose_name='Número'),
        ),
        migrations.AlterField(
            model_name='address',
            name='state',
            field=models.CharField(choices=[('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'), ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'), ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'), ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'), ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'), ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins')], default='SP', max_length=2, verbose_name='Estado'),
        ),
        migrations.AlterField(
            model_name='address',
            name='street',
            field=models.CharField(max_length=100, verbose_name='Rua'),
        ),
        migrations.AlterField(
            model_name='address',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to=settings.AUTH_USER_MODEL, verbose_name='Usuário'),
        ),
        migrations.AlterField(
            model_name='address',
            name='zip_code',
            field=models.CharField(max_length=8, verbose_name='CEP'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='age',
            field=models.PositiveIntegerField(verbose_name='Idade'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='birth',
            field=models.DateField(verbose_name='Nascimento'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Usuário'),
        ),
    ]
