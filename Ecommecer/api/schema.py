from ninja import Schema
from typing import List, Optional

class ItemCompra(Schema):
    produto_id: int
    quantidade: int

class CompraRequest(Schema):
    itens: List[ItemCompra]

