from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError
from django.utils import timezone
from django.utils.crypto import get_random_string


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='Usuário')
    street = models.CharField(max_length=100, verbose_name='Rua')
    number = models.CharField(max_length=10, verbose_name='Número')
    complement = models.CharField(max_length=50, blank=True, null=True, verbose_name='Complemento')
    neighborhood = models.CharField(max_length=50, verbose_name='Bairro')
    zip_code = models.CharField(max_length=8, verbose_name='CEP')
    city = models.CharField(max_length=50, verbose_name='Cidade')
    state = models.CharField(
        max_length=2,
        default='SP',
        verbose_name='Estado',
        choices=[
            ('AC', 'Acre'),
            ('AL', 'Alagoas'),
            ('AP', 'Amapá'),
            ('AM', 'Amazonas'),
            ('BA', 'Bahia'),
            ('CE', 'Ceará'),
            ('DF', 'Distrito Federal'),
            ('ES', 'Espírito Santo'),
            ('GO', 'Goiás'),
            ('MA', 'Maranhão'),
            ('MT', 'Mato Grosso'),
            ('MS', 'Mato Grosso do Sul'),
            ('MG', 'Minas Gerais'),
            ('PA', 'Pará'),
            ('PB', 'Paraíba'),
            ('PR', 'Paraná'),
            ('PE', 'Pernambuco'),
            ('PI', 'Piauí'),
            ('RJ', 'Rio de Janeiro'),
            ('RN', 'Rio Grande do Norte'),
            ('RS', 'Rio Grande do Sul'),
            ('RO', 'Rondônia'),
            ('RR', 'Roraima'),
            ('SC', 'Santa Catarina'),
            ('SP', 'São Paulo'),
            ('SE', 'Sergipe'),
            ('TO', 'Tocantins'),
        ]
    )

    def __str__(self):
        return f"{self.street}, {self.number}, {self.city} - {self.state}" 

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Usuário')
    birth = models.DateField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    cpf = models.CharField(max_length=11, unique=False)

    def __str__(self):
        return f"{self.user.username} - {self.cpf}"
    
    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
    
    def clean(self):
        raise ValidationError({
            'age': "testes"
        })

# initial user
class InterestArea(models.Model):
    label = models.CharField(max_length=100, default='default_label')

    def __str__(self):
        return self.label

class NewUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='new_user_profile')
    name = models.CharField(max_length=100)
    nickname = models.CharField(max_length=100)
    professional_title = models.CharField(max_length=100)
    about = models.TextField()
    professional_experience = models.TextField()
    #interest_areas = models.ManyToManyField(InterestArea, blank=True)
    interest_areas = models.TextField(blank=True)
    ability = models.TextField()

    def __str__(self):
        return self.user.username

    
class PendingUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)  # Adicione uma relação com User
    token = models.CharField(max_length=64, unique=True, default=get_random_string(64))
    created_at = models.DateTimeField(auto_now_add=True)
    nickname = models.CharField(max_length=100, blank=True)

    def token_expired(self):
        """ Retorna True se o token expirou, caso contrário False """
        expiration_date = self.created_at + timezone.timedelta(hours=24)  # 24 horas para expiração
        return expiration_date <= timezone.now()
