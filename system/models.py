from django.db import models


# Create your models here.
class ConfigCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True)

    def __str__(self):
        return self.name


class ConfigChoice(models.Model):
    category = models.ForeignKey(ConfigCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='choice/', null=True, blank=True)
    status = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
