from cadastro.api.api import cadastro_router
from Ecommecer.api.api import Ecommecer_router
from ninja_jwt.controller import NinjaJWTDefaultController 
from ninja_extra import NinjaExtraAPI  

api = NinjaExtraAPI(urls_namespace="api")


api.register_controllers(NinjaJWTDefaultController)
api.add_router('cadastro/', cadastro_router)
api.add_router('ecommecer/', Ecommecer_router)



