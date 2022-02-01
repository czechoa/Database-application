from typing import Optional, Union, List
from app.models.core import IDModelMixin, DateTimeModelMixin, CoreModel
from pydantic import constr, StrictInt


class PasswordGroupBase(CoreModel):
    """
    All common characteristics of our Course resource
    """
    password_id: Optional[int]


class PasswordGroupCreate(PasswordGroupBase):
    username: constr(min_length=3, max_length=100, regex="[a-zA-Z0-9_-]+$")
    password_id: StrictInt

class PasswordGroupInDB(IDModelMixin, PasswordGroupBase):
    username: int
    password_id: str

class PasswordGroupPublic(PasswordGroupBase):
    username: str
    password_id: int
