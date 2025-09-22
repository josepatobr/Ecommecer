from django.urls import path
import views

urlpatterns = [
    path('', views.painel_administrador, name="painel_administrador"),
]
