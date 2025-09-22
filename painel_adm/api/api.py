from painel_adm.utils import cargos_requeridos
from Ecommecer.models import Pedido
from painel_adm.api.schema import RastreioSchema
from ninja import Router

import json

administrador_router = Router()

@cargos_requeridos(["envios", "geral"])
@administrador_router.post("/atualizar-rastreio")
def atualizar_rastreio(request, data: RastreioSchema):
    try:
        pedido = Pedido.objects.get(id=data.pedido_id)
        pedido.numero_rastreio = data.numero_rastreio
        pedido.save()
        return {"mensagem": "Número de rastreio atualizado com sucesso"}
    except Pedido.DoesNotExist:
        return {"erro": "Pedido não encontrado"}
    
@cargos_requeridos(["envios", "geral"])
@administrador_router.post("/webhook/entrega")
def webhook_entrega(request):
    payload = request.body.decode("utf-8")
    data = json.loads(payload)

    rastreio = data.get("numero_rastreio")
    status_entrega = data.get("status")

    if not rastreio or not status_entrega:
        return 400, {"erro": "Dados incompletos"}

    if "entregue" in status_entrega.lower():
        pedido = Pedido.objects.filter(numero_rastreio=rastreio).first()
        if pedido and pedido.status != "entregue":
            pedido.status = "entregue"
            pedido.save()
            return {"mensagem": "Pedido marcado como entregue via webhook"}

    return {"mensagem": "Status não indica entrega"}


