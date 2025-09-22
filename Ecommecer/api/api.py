from ninja import Router
from Ecommecer.models import Produto, Pedido, ItemPedido, CarrinhoItem
from django.shortcuts import get_object_or_404
from .schema import CompraRequest
from django.contrib.auth.models import User
import json
from core.tasks import enviar_email_async
from core import settings
import stripe
from datetime import timezone


Ecommecer_router = Router()



@Ecommecer_router.get('/home')
def home(request):
    if not request.auth:
        return {"erro": "Usuário não autenticado"}

    produtos_destaque = Produto.objects.filter(ativo=True).order_by('-quantidade_estoque')[:5]
    produtos_promocionais = Produto.objects.filter(em_promocao=True, ativo=True)

    return {
        "mensagem": "Confira nossos destaques e promoções!",
        "produtos_destaque": [
            {
                "nome": p.nome,
                "preco": float(p.preco_venda),
                "estoque": p.quantidade_estoque,
                "categoria": p.categoria.nome if p.categoria else "Sem categoria"
            }
            for p in produtos_destaque
        ],
        "promocoes": [
            {
                "nome": p.nome,
                "preco_original": float(p.preco_venda),
                "preco_promocional": float(p.preco_promocional),
                "desconto": round(100 - (p.preco_promocional / p.preco_venda * 100), 2),
                "categoria": p.categoria.nome if p.categoria else "Sem categoria"
            }
            for p in produtos_promocionais
        ]
    }

@Ecommecer_router.get("/produto/{produto_id}")
def get_produto(request, produto_id: int):
    produto = get_object_or_404(Produto, id=produto_id)
    return {
        "id": produto.id,
        "nome": produto.nome,
        "preco_venda": float(produto.preco_venda),
        "categoria": produto.categoria.nome if produto.categoria else "Sem categoria",
        "estoque": produto.quantidade_estoque,
        "em_promocao": produto.em_promocao,
        "preco_promocional": float(produto.preco_promocional) if produto.preco_promocional else None,
        "desconto": produto.desconto_percentual if hasattr(produto, "desconto_percentual") else None,
    }

@Ecommecer_router.post("/comprar")
def realizar_compra(request, dados: CompraRequest):
    if not request.auth:
        return {"erro": "Usuário não autenticado"}

    itens_validos = []
    itens_invalidos = []
    total = 0

    for item in dados.itens:
        try:
            produto = Produto.objects.get(id=item.produto_id, ativo=True)

            if produto.quantidade_estoque < item.quantidade:
                itens_invalidos.append({
                    "produto_id": item.produto_id,
                    "motivo": "Estoque insuficiente"
                })
                continue

            preco = produto.preco_promocional or produto.preco_venda
            subtotal = preco * item.quantidade
            total += subtotal

            itens_validos.append({
                "produto_id": produto.id,
                "nome": produto.nome,
                "quantidade": item.quantidade,
                "preco_unitario": float(preco),
                "subtotal": float(subtotal)
            })

        except Produto.DoesNotExist:
            itens_invalidos.append({
                "produto_id": item.produto_id,
                "motivo": "Produto não encontrado ou inativo"
            })

    return {
        "itens_validos": itens_validos,
        "itens_invalidos": itens_invalidos,
        "total_estimado": round(total, 2),
        "status": "validação concluída"
    }

@Ecommecer_router.post("/checkout")
def iniciar_checkout(request, dados: CompraRequest):
    line_items = []

    for item in dados.itens:
        produto = Produto.objects.get(id=item.produto_id)
        preco = produto.preco_promocional or produto.preco_venda

        line_items.append({
            "price_data": {
                "currency": "brl",
                "product_data": {
                    "name": produto.nome,
                },
                "unit_amount": int(preco * 100), 
            },
            "quantity": item.quantidade,
        })

 
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url="https://ecommecer.com/sucesso",
            cancel_url="https://ecommecer.com/cancelado",
            client_reference_id=str(request.user.id),
            metadata={
                "itens": json.dumps(dados.itens)
            }
        )

    return {"checkout_url": session.url}

@Ecommecer_router.post("/webhook")
def stripe_webhook(request):
    payload = request.body.decode("utf-8")
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        return 400, {"error": "Assinatura inválida"}

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        cliente_id = session.get("client_reference_id")

    try:
        usuario = User.objects.get(id=cliente_id)
    except User.DoesNotExist:
        return {"error": "Usuário não encontrado"}

    itens_json = session.get("metadata", {}).get("itens")
    itens_compra = json.loads(itens_json)

   
    total = 0
    pedido = Pedido.objects.create(
    usuario=usuario,
    total=0,
    status="pago",
    stripe_session_id=session.get("id"))

    for item in itens_compra:
        produto = Produto.objects.get(id=item["produto_id"])
        preco = produto.preco_promocional or produto.preco_venda
        subtotal = preco * item["quantidade"]
        total += subtotal

    ItemPedido.objects.create(
        pedido=pedido,
        produto=produto,
        quantidade=item["quantidade"],
        preco_unitario=preco
    )

    produto.quantidade_estoque -= item["quantidade"]
    produto.save()

    pedido.total = total
    pedido.save()

    assunto = "Compra confirmada"
    mensagem = f"Olá, {usuario.username}! Seu pedido foi confirmado com sucesso. Em breve você receberá os detalhes no seu e-mail."
    enviar_email_async.delay(assunto, mensagem, usuario.email)

    return 200, {"status": "Pedido registrado com sucesso"}


@Ecommecer_router.get("/painel_pedidos")
def listar_pedidos(request):
    if not request.auth:
        return {"erro": "Usuário não autenticado"}

    pedidos = Pedido.objects.filter(usuario=request.user).order_by("-data_criacao")
  
    return {
        "pedidos": [
            {
                "id": pedido.id,
                "data": pedido.data_criacao.strftime("%d/%m/%Y %H:%M"),
                "status": pedido.status,
                "total": float(pedido.total),
                "stripe_session_id": pedido.stripe_session_id,
                "itens": [
                    {
                        "produto": item.produto.nome,
                        "quantidade": item.quantidade,
                        "preco_unitario": float(item.preco_unitario),
                        "subtotal": float(item.preco_unitario * item.quantidade)
                    }
                    for item in pedido.itens.all()
                ]
            }
            for pedido in pedidos
        ]
        
    }

@Ecommecer_router.post("/carrinho/adicionar")
def adicionar_carrinho(request):
    if not request.auth:
        return {"erro": "Usuário não autenticado"}

    produto_id = request.data.get("produto_id")
    quantidade = int(request.data.get("quantidade", 1))

    produto = Produto.objects.get(id=produto_id)

    item, criado = CarrinhoItem.objects.get_or_create(
        usuario=request.user,
        produto=produto,
        defaults={"quantidade": quantidade}
    )
    if not criado:
        item.quantidade += quantidade
        item.save()

    return {"mensagem": "Produto adicionado ao carrinho"}

@Ecommecer_router.post("/carrinho/remover")
def remover_do_carrinho(request):
    if not request.auth:
        return {"erro": "Usuário não autenticado"}

    produto_id = request.data.get("produto_id")

    if not produto_id:
        return {"erro": "ID do produto não informado"}

    CarrinhoItem.objects.filter(usuario=request.user, produto_id=produto_id).delete()

    return {"mensagem": "Produto removido do carrinho"}


@Ecommecer_router.post("/finalizar-carrinho")
def finalizar_carrinho(request):
    if not request.auth:
        return {"erro": "Usuário não autenticado"}

    carrinho = CarrinhoItem.objects.filter(usuario=request.user)

    if not carrinho.exists():
        return {"erro": "Carrinho vazio"}

    pedido = Pedido.objects.create(
        usuario=request.user,
        data_criacao=timezone.now(),
        status="Pendente",
        total=sum(item.subtotal() for item in carrinho)
    )

    for item in carrinho:
        ItemPedido.objects.create(
            pedido=pedido,
            produto=item.produto,
            quantidade=item.quantidade,
            preco_unitario=item.produto.preco
        )

    carrinho.delete()

    return {
        "mensagem": "Pedido criado com sucesso",
        "pedido_id": pedido.id
    }

@Ecommecer_router.post("/pedido/rastreio")
def ver_rastreio(request):
    if not request.auth:
        return {"erro": "Usuário não autenticado"}

    pedido_id = request.data.get("pedido_id")
    rastreio = request.data.get("numero_rastreio")

    if pedido.status == "pago":
        pedido.status = "enviando"
        pedido.save()

    pedido = Pedido.objects.filter(id=pedido_id, usuario=request.user).first()
    if not pedido:
        return {"erro": "Pedido não encontrado"}

    pedido.numero_rastreio = rastreio
    pedido.save()

    return {"mensagem": "Número de rastreio atualizado com sucesso"}