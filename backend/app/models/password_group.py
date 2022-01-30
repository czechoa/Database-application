from typing import Optional, Union, List
from app.models.core import IDModelMixin, DateTimeModelMixin, CoreModel
from pydantic import constr, StrictInt


class PasswordGroupBase(CoreModel):
    """
    All common characteristics of our Course resource
    """
    id_password: Optional[int]


class PasswordGroupCreate(PasswordGroupBase):
    user_name: constr(min_length=3, max_length=300, regex="[a-zA-Z0-9_-]+$")
    id_password: StrictInt

class PasswordGroupInDB(IDModelMixin, PasswordGroupBase):
    id_user: int
    id_password: str

class PasswordGroupPublic(PasswordGroupBase):
    user_name: constr(min_length=3, max_length=100, regex="[a-zA-Z0-9_-]+$")
    id_password: int
