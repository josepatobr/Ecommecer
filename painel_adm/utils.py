from .models import AdministradorPainel, PerfilUsuario
from functools import wraps
from ninja.errors import HttpError
from Ecommecer.models import Pedido
from correios import Correios


#python manage.py migrate django_celery_beat (vou rodar ele dps q eu arrumar os bugs)
#painel_adm.tasks.tarefa_verificar_entregas (colocar isso no django admin)


def permissao_adm(request, cargo_esperado=None):
    try:
        perfil = request.user.perfilusuario
        admin = AdministradorPainel.objects.get(usuario=perfil)
        if not admin.ativo:
            return False
        if cargo_esperado and admin.cargo != cargo_esperado:
            return False
        return True
    except:
        return False
    
def cargos_requeridos(cargos):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            try:
                perfil = request.user.perfilusuario
                admin = AdministradorPainel.objects.get(usuario=perfil)
                if not admin.ativo or admin.cargo not in cargos:
                    raise HttpError(403, "Acesso negado")
                return func(request, *args, **kwargs)
            except:
                raise HttpError(403, "Acesso negado")
        return wrapper
    return decorator

def verificar_entregas():
    correios = Correios()
    pedidos = Pedido.objects.filter(status="enviando", numero_rastreio__isnull=False)

    for pedido in pedidos:
        try:
            objeto = correios.rastreio(cod=pedido.numero_rastreio)

            if objeto and objeto.eventos:
                for evento in objeto.eventos:
                    if "entregue" in evento.descricao.lower():
                        pedido.status = "entregue"
                        pedido.save()
                        print(f"Pedido {pedido.id} marcado como entregue.")
                        break

        except Exception as e:
            print(f"Erro ao rastrear pedido {pedido.id}: {e}")