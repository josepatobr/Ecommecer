import jwt
import random
import string
from django.conf import settings
import os
from dotenv import load_dotenv
load_dotenv()


SECRET_KEY_JWT=os.getenv("SECRET_KEY_JWT")

def gerar_token(tamanho=12):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=tamanho))
    
Token = {
    "token": gerar_token(),
    "tipo": settings.SIMPLE_JWT['AUTH_HEADER_TYPES'][0],            
}

token_jwt = jwt.encode(Token, SECRET_KEY_JWT, algorithm="HS256")

print("JWT gerado:")
print(token_jwt)

