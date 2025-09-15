from django.shortcuts import render
from .models import Produto, Categoria, Pedido
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def home(request):
    categoria_id = request.GET.get("categoria")
    categorias = Categoria.objects.all()

    if categoria_id:
        produtos = Produto.objects.filter(categoria_id=categoria_id, ativo=True)
    else:
        produtos = Produto.objects.filter(ativo=True)

    promocoes = Produto.objects.filter(em_promocao=True, ativo=True)

    context = {
        "usuario": request.user,
        "categorias": categorias,
        "produtos": produtos,
        "promocoes": promocoes,
    }

    return render(request, "ecommecer.html", context)

@login_required
def painel_pedidos(request):
    pedidos = Pedido.objects.filter(usuario=request.user).order_by("-data_criacao")

    return render(request, "painel_pedidos.html", {
        "pedidos": pedidos
    })