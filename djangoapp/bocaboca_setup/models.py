from django.db import models
from utils.images import resize_image
from utils.model_validators import validate_png 

class MenuLink(models.Model):
    class Meta:
        verbose_name = 'Menu Link'
        verbose_name_plural = 'Menu Links'

    text = models.CharField(max_length=50)
    url_or_path = models.CharField(max_length=2048)
    new_tab = models.BooleanField(default=False)
    bocaboca_setup = models.ForeignKey(
        'BocabocaSetup', on_delete=models.CASCADE, blank=True, null=True,
        default=None,
    )

    def __str__(self):
        return self.text

class BocabocaSetup(models.Model):
    class Meta:
        verbose_name = 'Setup'
        verbose_name_plural = 'Setup'

    title = models.CharField(max_length=65)
    description = models.CharField(max_length=255)
    span_1 = models.CharField(max_length=255,default='')
    span_2 = models.CharField(max_length=255,default='')
    span_3 = models.CharField(max_length=255,default='')
    show_header = models.BooleanField(default=True)
    show_search = models.BooleanField(default=True)
    show_menu = models.BooleanField(default=True)
    show_description = models.BooleanField(default=True)
    show_pagination = models.BooleanField(default=True)
    show_footer = models.BooleanField(default=True)
    favicon = models.ImageField(
        upload_to='assets/favicon/%Y/%m',
        blank=True, default='',
        validators=[validate_png],
    )

    def save(self, *args, **kwargs):
        current_favicon_name = str(self.favicon.name)
        super().save(*args, **kwargs)
        favicon_changed = False

        if self.favicon:
            favicon_changed = current_favicon_name != self.favicon.name

        if favicon_changed:
            resize_image(self.favicon, 32)

    def __str__(self):
        return self.title

