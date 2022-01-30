from typing import Optional

from pydantic import EmailStr

from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST
from databases import Database

from app.db.repositories.base import BaseRepository
from app.models.user import UserCreate, UserUpdate, UserInDB, UserPublic, UserCreateNewPassword

from app.db.repositories.profiles import ProfilesRepository
from app.models.profile import ProfileCreate, ProfilePublic

from app.services import auth_service

GET_USER_BY_EMAIL_QUERY = """
    SELECT id, username, email, email_verified, password, salt, super_password, super_salt,  is_active, is_superuser, created_at, updated_at
    FROM users
    WHERE email = :email;
"""

GET_USER_BY_USERNAME_QUERY = """
    SELECT id, username, email, email_verified, password, salt,super_password, super_salt, is_active, is_superuser, created_at, updated_at
    FROM users
    WHERE username = :username;
"""

REGISTER_NEW_USER_QUERY = """
    INSERT INTO users (username, email, password, super_password, salt, super_salt)
    VALUES (:username, :email, :password,:super_password, :salt, :super_salt)
    RETURNING id, username, email, email_verified, password,super_password, salt, super_salt, is_active, is_superuser, created_at, updated_at;
"""
UPDATE_USER_PASSWORD_QUERY = """
    UPDATE users
    set  password=:password,
            salt=:salt
    where id=:id;
"""


class UsersRepository(BaseRepository):
    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.auth_service = auth_service
        self.profiles_repo = ProfilesRepository(db)

    async def get_user_by_email(self, *, email: EmailStr, populate: bool = True) -> UserInDB:
        user_record = await self.db.fetch_one(query=GET_USER_BY_EMAIL_QUERY, values={"email": email})

        if user_record:
            user = UserInDB(**user_record)

            if populate:
                return await self.populate_user(user=user)

            return user

    async def get_user_by_username(self, *, username: str, populate: bool = True) -> UserInDB:
        user_record = await self.db.fetch_one(query=GET_USER_BY_USERNAME_QUERY, values={"username": username})

        if user_record:
            user = UserInDB(**user_record)

            if populate:
                return await self.populate_user(user=user)

            return user

    async def change_password(self, *, user_change_password: UserCreateNewPassword):
        user_db = await self.get_user_by_email(email=user_change_password.email, populate=False)
        if not user_db:
            return None
        if not self.auth_service.verify_super_password(super_password=user_change_password.super_password,
                                                       super_salt=user_db.super_salt, hashed_pw=user_db.super_password):
            return None

        user_password_update = self.auth_service.create_salt_and_hashed_password(
            plaintext_password=user_change_password.new_password)

        user_params = user_password_update.copy(update={'id': user_db.id})


        await self.db.fetch_one(query=UPDATE_USER_PASSWORD_QUERY, values= user_params.dict())

        return UserPublic(**user_db.dict())

    async def register_new_user(self, *, new_user: UserCreate) -> UserInDB:
        # make sure email isn't already taken

        if await self.get_user_by_email(email=new_user.email):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="That email is already taken. Login with that email or register with another one.",
            )

        # make sure username isn't already taken
        if await self.get_user_by_username(username=new_user.username):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="That username is already taken. Please try another one."
            )

        user_password_update = self.auth_service.create_salt_and_hashed_password(plaintext_password=new_user.password)
        user_super_password_update = self.auth_service.create_super_salt_and_hashed_password(
            plaintext_password=new_user.super_password)

        new_user_params = new_user.copy(update=user_password_update.dict())
        new_user_params = new_user_params.copy(update=user_super_password_update.dict())
        print(type(new_user_params))
        print(new_user_params)
        created_user = await self.db.fetch_one(query=REGISTER_NEW_USER_QUERY, values=new_user_params.dict())

        await self.profiles_repo.create_profile_for_user(profile_create=ProfileCreate(user_id=created_user["id"]))

        return await self.populate_user(user=UserInDB(**created_user))

    async def authenticate_user(self, *, email: EmailStr, password: str) -> Optional[UserInDB]:
        # make user user exists in db
        user = await self.get_user_by_email(email=email, populate=False)
        if not user:
            return None
        # if submitted password doesn't match
        if not self.auth_service.verify_password(password=password, salt=user.salt, hashed_pw=user.password):
            return None

        return user

    async def populate_user(self, *, user: UserInDB) -> UserInDB:
        return UserPublic(
            # unpack the user in db instance,
            **user.dict(),
            # fetch the user's profile from the profiles_repo
            profile=await self.profiles_repo.get_profile_by_user_id(user_id=user.id),
        )
