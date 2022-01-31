from typing import Optional, Union, List
from app.models.core import IDModelMixin, DateTimeModelMixin, CoreModel
from pydantic import constr


class PasswordBase(CoreModel):
    """
    All common characteristics of our Course resource
    """
    description: Optional[str]

class PasswordCreate(PasswordBase):
    description: constr(min_length=1, max_length=300, regex="[a-zA-Z0-9_ -]+$")
    password: constr(min_length=7, max_length=100, regex="[a-zA-Z0-9_-]+$")
    key: constr(min_length=7, max_length=100, regex="[a-zA-Z0-9_-]+$")



class PasswordInDB(IDModelMixin, PasswordBase):
    id:int
    description: str
    password: bytes
    salt: bytes
    iv: bytes

class PasswordUpdate(PasswordBase):
    description: str
    password: bytes
    salt: bytes
    iv: bytes

class PasswordPublic(PasswordBase):
    id:int
    description: str

class PasswordDecrypted(PasswordPublic):
    password:str

# class PasswordToDecrypt(PasswordBase):
#     password_id: int
#     key: constr(min_length=7, max_length=100, regex="[a-zA-Z0-9_-]+$")

