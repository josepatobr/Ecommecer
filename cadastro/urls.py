from django.urls import path
from . import views


urlpatterns = [
    path('cadastro/', views.mostrar_formulario, name='mostrar_formulario'),
    path('verificar-codigo/', views.mostrar_formulario_codigo, name='mostrar_formulario_codigo'),

]