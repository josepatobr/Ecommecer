from django.core.management.base import BaseCommand
from painel_adm.utils import verificar_entregas

class Command(BaseCommand):
    help = "Verifica entregas e atualiza pedidos automaticamente"

    def handle(self, *args, **kwargs):
        verificar_entregas()
        self.stdout.write("Verificação de entregas concluída.")