from django.contrib import admin
from django.urls import path, include
from .api import api



urlpatterns = [
    path('api/', api.urls),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('Ecommecer/', include("cadastro.urls")),
    path('Ecommecer/', include("Ecommecer.urls")),
    path('painel_administrador/', include("painel_adm.urls")),

]
