from ninja import Router

Ecommecer_router = Router()



@Ecommecer_router.post('')
def home(request):
    return print("vc esta no home")