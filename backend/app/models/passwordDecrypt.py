from typing import Optional, Union, List
from app.models.core import IDModelMixin, DateTimeModelMixin, CoreModel
from pydantic import constr,StrictInt


class PasswordDecryptBase(CoreModel):
    """
    All common characteristics of our Course resource
    """
    # description: Optional[str]
    password_id:Optional[int]
    key:Optional[str]



class PasswordToDecrypt(PasswordDecryptBase):
    password_id: StrictInt
    key: constr(min_length=7, max_length=100, regex="[a-zA-Z0-9_-]+$")

