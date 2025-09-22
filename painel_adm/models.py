from django.db import models
from django.contrib.auth.models import User

class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    cpf = models.CharField(max_length=14)
    telefone = models.CharField(max_length=20)
    endereco = models.TextField()
    data_nascimento = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.usuario.username} - Perfil"

class AdministradorPainel(models.Model):
    usuario = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE)
    cargo = models.CharField(max_length=50, choices=[
        ("geral", "Administrador Geral"),
        ("envios", "Gestor de Envios"),
        ("suporte", "Suporte ao Cliente"),
    ])
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.usuario.username} ({self.cargo})"