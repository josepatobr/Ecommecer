from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('painel_pedidos/', views.painel_pedidos, name='painel_pedidos'),
    path('carrinho/', views.carrinho, name='carrinho'),

]