from django.urls import path
from . import views
urlpatterns = [
    path('', views.painel_administrador, name="painel_administrador"),
]
