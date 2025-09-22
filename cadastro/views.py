from django.shortcuts import render


def mostrar_formulario(request): 
    return render(request, "cadastro.html")

def mostrar_formulario_codigo(request):
    return render(request, "codigo.html")


