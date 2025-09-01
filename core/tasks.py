from celery import shared_task
from django.core.mail import send_mail



@shared_task
def enviar_email_async(assunto, mensagem, destinatario):
    send_mail(
        subject=assunto,
        message=mensagem,
        from_email='josecarlosrodriguesrod.pinto@gmail.com',
        recipient_list=[destinatario],
        fail_silently=False
    )