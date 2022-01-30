# import string
from typing import Optional

from pydantic import EmailStr, constr

from app.models.core import DateTimeModelMixin, IDModelMixin, CoreModel
from app.models.token import AccessToken
from app.models.profile import ProfilePublic


class UserBase(CoreModel):
    """
    Leaving off password and salt from base model
    """

    email: Optional[EmailStr]
    username: Optional[str]
    email_verified: bool = False
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(CoreModel):
    """
    Email, username, and password are required for registering a new user
    """

    email: EmailStr
    password: constr(min_length=7, max_length=100,regex = "(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W)")
    super_password: constr(min_length=7, max_length=100,regex = "(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W)")

    username: constr(min_length=3, max_length=100, regex="[a-zA-Z0-9_-]+$")


class UserCreateNewPassword(CoreModel):
    """
    Email, username, and password are required for registering a new user
    """

    email: EmailStr
    username: constr(min_length=3, regex="[a-zA-Z0-9_-]+$")
    super_password: constr(min_length=7, max_length=100,regex = "(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W)")
    new_password: constr(min_length=7, max_length=100,regex = "(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W)")

class UserUpdate(CoreModel):
    """
    Users are allowed to update their email and username
    """

    email: Optional[EmailStr]
    username: Optional[constr(min_length=3, regex="[a-zA-Z0-9_-]+$")] # allow


class UserPasswordUpdate(CoreModel):
    """
    Users can change their password
    """

    password: constr(min_length=7, max_length=100)
    salt: str

class UserSuperPasswordUpdate(CoreModel):
    """
    Users can change their password
    """

    super_password: constr(min_length=7, max_length=100)
    super_salt: str

class UserInDB(IDModelMixin, DateTimeModelMixin, UserBase):
    """
    Add in user's password and salt
    """

    password: constr(min_length=7)
    super_password: constr(min_length=7)

    salt: str
    super_salt: str


class UserPublic(IDModelMixin, DateTimeModelMixin, UserBase):
    access_token: Optional[AccessToken]
    profile: Optional[ProfilePublic]
# super password to loss password
