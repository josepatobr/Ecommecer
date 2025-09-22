from ninja import Schema

class RastreioSchema(Schema):
    pedido_id: int
    numero_rastreio: str