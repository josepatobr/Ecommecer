from cadastro.api.api import cadastro_router
from Ecommecer.api.api import Ecommecer_router
from ninja_jwt.controller import NinjaJWTDefaultController 
from ninja_extra import NinjaExtraAPI  

api = NinjaExtraAPI()

api.register_controllers(NinjaJWTDefaultController)
api.add_router('api/', cadastro_router)
api.add_router('api/', Ecommecer_router)



