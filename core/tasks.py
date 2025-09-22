import smtplib
import base64
from celery import shared_task
from core.OAuth import credentials
from painel_adm.utils import verificar_entregas


@shared_task
def enviar_email_async(remetente, destinatario, assunto, corpo, access_token=credentials.token):
    auth_string = f'user={remetente}\1auth=Bearer {access_token}\1\1'
    auth_string = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.docmd('AUTH', 'XOAUTH2 ' + auth_string)

    mensagem = f"Subject: {assunto}\n\n{corpo}"
    server.sendmail(remetente, destinatario, mensagem)
    server.quit()

@shared_task
def tarefa_verificar_entregas():
    verificar_entregas()