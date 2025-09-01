from pydantic import BaseModel, EmailStr, model_validator, field_validator
from zxcvbn import zxcvbn
import re


class CadastroSchema(BaseModel):
    username: str
    password: str
    confirmed_password: str
    email: EmailStr

    
    @field_validator("password")
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Senha muito curta")
        if not re.search(r"[A-Z]", v):
            raise ValueError("A senha deve conter pelo menos uma letra maiúscula")
        if not re.search(r"[a-z]", v):
            raise ValueError("A senha deve conter pelo menos uma letra minúscula")
        if not re.search(r"\d", v):
            raise ValueError("A senha deve conter pelo menos um número")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("A senha deve conter pelo menos um caractere especial")
        return v

    @field_validator("password")
    def is_password_strong(cls, v):
        result = zxcvbn(v)
        if result["score"] < 3:
            raise ValueError("A senha é considerada fraca")
        return v
    
    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirmed_password:
            raise ValueError("As senhas não coincidem")
        return self



class EmailSchema(BaseModel):
    email: EmailStr     
    assunto:str      
    mensagem:str  


class CodigoVerificacaoSchema(BaseModel):
    email: EmailStr
    codigo: str
 
    @field_validator("codigo")
    def validar_codigo_formatado(cls, v):
        if not v.isdigit() or len(v) != 6:
            raise ValueError("O código deve ter 6 dígitos numéricos")
        return v
