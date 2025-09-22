from cadastro.api.api import cadastro_router
from Ecommecer.api.api import Ecommecer_router
from painel_adm.api.api import administrador_router
from ninja_jwt.controller import NinjaJWTDefaultController 
from ninja import NinjaAPI

api = NinjaAPI()

api.add_router('', cadastro_router)
api.add_router('/ecommecer', Ecommecer_router)
api.add_router('/painel_adm', administrador_router)



