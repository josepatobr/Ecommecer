from django.db import models
from django.utils import timezone
from datetime import timedelta

class CodigoCadastro(models.Model):
    email = models.EmailField()
    codigo = models.CharField(max_length=6)
    validade = models.DateTimeField(default=timezone.now() + timedelta(hours=1))
    tentativas = models.IntegerField(default=0)

    def expirado(self):
        return timezone.now() > self.validade