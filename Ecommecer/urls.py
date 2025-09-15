from django.urls import path
from Ecommecer import views

urlpatterns = [
    path('home', views.home, name='home'),
    path('painel_pedidos', views.painel_pedidos, name='painel_pedidos')

]