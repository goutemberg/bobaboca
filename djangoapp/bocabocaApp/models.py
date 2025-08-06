from django.db import models
from utils.rands import slugify_new


class Profissional(models.Model):
    class Meta:
        verbose_name = 'Profissional'
        verbose_name_plural = 'Profissionais'
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(
        unique=True, default=None,
        null=True, blank=True, max_length=255
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_new(self.name)
        return super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return self.name

class Category(models.Model):
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(
        unique=True, default=None,
        null=True, blank=True, max_length=255
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_new(self.name)
        return super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return self.name

class Page(models.Model):
    title = models.CharField(max_length=65,)
    slug = models.SlugField(
        unique=True, default="",
        null=False, blank=True, max_length=255
    )
    is_published = models.BooleanField(
        default=False,
        help_text=(
            'Este campo precisará estar marcado '
            'para a página ser exibida publicamente.'
        ),
    )
    content = models.TextField()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_new(self.title, 4)
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title

class Client(models.Model):
    user = models.OneToOneField('bocaboca_profile.CustomUser', on_delete=models.CASCADE)  # Relacionado ao modelo CustomUser
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    preferred_service = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.username



