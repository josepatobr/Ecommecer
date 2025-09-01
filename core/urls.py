from django.contrib import admin
from django.urls import path, include
from .api import api



urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', api.urls),
    path('', include("cadastro.urls")),

]
