from django.db import models
from django.contrib.auth.models import User

TIPOS_CATEGORIA = [
    ('ELETRONICO', 'Eletrônico'),
    ('ROUPA', 'Roupa'),
    ('ALIMENTO', 'Alimento'),
    ('LIMPEZA', 'Limpeza'),
    ('MOVEIS', 'Móveis'),
    ('ESCRITORIO', 'Escritório'),
    ('FERRAMENTA', 'Ferramenta'),
    ('DECORACAO', 'Decoração'),
    ('BRINQUEDO', 'Brinquedo'),
    ('OUTROS', 'Outros'),
]

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    tipo = models.CharField(max_length=20, choices=TIPOS_CATEGORIA)

    def __str__(self):
        return f"{self.nome} - {self.get_tipo_display()}"

class CriarCategoria(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    tipo = models.CharField(max_length=20, choices=TIPOS_CATEGORIA)

    def salvar_categoria(self):
        categoria = Categoria.objects.create(
            nome=self.nome,
            descricao=self.descricao,
            tipo=self.tipo
        )
        return categoria

    def __str__(self):
        return f"Criar: {self.nome} ({self.get_tipo_display()})"

class Produto(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    preco_custo = models.DecimalField(max_digits=10, decimal_places=2)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade_estoque = models.PositiveIntegerField()
    em_promocao = models.BooleanField(default=False)
    preco_promocional = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    unidade_medida = models.CharField(max_length=20, choices=[
        ('UN', 'Unidade'),
        ('KG', 'Quilograma'),
        ('LT', 'Litro'),
        ('MT', 'Metro'),
    ])
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)
    imagem = models.ImageField(upload_to='produtos/', blank=True, null=True)
    marca = models.CharField(max_length=100, blank=True)
    modelo = models.CharField(max_length=100, blank=True)
    validade = models.DateField(blank=True, null=True)
    peso = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    largura = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    altura = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    profundidade = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    def desconto_percentual(self):
        if self.em_promocao and self.preco_promocional and self.preco_venda > 0:
            desconto = 100 - (self.preco_promocional / self.preco_venda * 100)
            return round(desconto, 2)
        return 0.0

    def margem_lucro(self):
        return self.preco_venda - self.preco_custo

    def em_estoque(self):
        return self.quantidade_estoque > 0

class Pedido(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default="Pendente")
    data_criacao = models.DateTimeField(auto_now_add=True)
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)  # novo campo

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
