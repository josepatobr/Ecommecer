from ninja import Router
from .schemas import CadastroSchema
from django.contrib.auth.models import User
from core.tasks import enviar_email_async
from cadastro.api.schemas import CodigoVerificacaoSchema
from cadastro.models import CodigoCadastro
import random
from datetime import datetime, timedelta

cadastro_router = Router()

def gerar_codigo():
    codigo = ''.join(str(random.randint(0, 9)) for _ in range(6))
    validade = datetime.now() + timedelta(hours=1)
    return codigo, validade


@cadastro_router.post("/cadastro")
def cadastro(request, payload: CadastroSchema):
    user = User(username=payload.username, email=payload.email)
    user.set_password(payload.password)
    
    
    codigo, validade = gerar_codigo()
    mensagem = f"Seu código de verificação é: {codigo}\nVálido até: {validade.strftime('%H:%M:%S')}"
    assunto = "Código de Verificação"
    enviar_email_async.delay(assunto, mensagem, payload.email)

    return {"status": "Código enviado"}


@cadastro_router.post("/verificar-codigo")
def verificar_codigo(request, payload: CodigoVerificacaoSchema):
    registro = CodigoCadastro.objects.filter(email=payload.email).first()

    if not registro:
        return {"erro": "Código não encontrado"}

    if registro.expirado():
        return {"erro": "Código expirado"}

    if registro.tentativas >= 3:
        return {"erro": "Você excedeu o número de tentativas"}

    if registro.codigo != payload.codigo:
        registro.tentativas += 1
        registro.save()
        return {"erro": "Código incorreto"}

    User.objects.create_user(username=payload.email.split("@")[0], email=payload.email, password="senha_definida")
    registro.delete()
    return {"status": "Usuário cadastrado com sucesso"}