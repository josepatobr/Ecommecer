from django.conf import settings
from django.shortcuts import render
from dotenv import load_dotenv
import os
load_dotenv()

def mostrar_formulario(request): 
    return render(request, "cadastro.html")

def mostrar_formulario_codigo(request):
    return render(request, "codigo.html")


