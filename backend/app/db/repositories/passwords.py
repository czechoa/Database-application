from fastapi import HTTPException, status
from fastapi.logger import logger
from typing import List
from app.db.repositories.base import BaseRepository
from app.models.password import PasswordPublic, PasswordCreate, PasswordInDB

CREATE_PASSWORD_QUERY = """
    insert into passwords (description,password)
    values (:description,:password)
    RETURNING id,description;
"""

CREATE_PASSWORD_GROUP = """
    insert into password_groups (user_id, password_id)
    values (:user_id,:password_id)
"""


class PasswordsRepository(BaseRepository):

    async def create_password(self, *, password_post: PasswordCreate, user_id: int) -> PasswordPublic:
        password_record = await self.db.fetch_one(query=CREATE_PASSWORD_QUERY, values=password_post.dict())

        print('\n '*2,PasswordPublic(**password_record))

        created_password = PasswordPublic(**password_record)

        await self.db.fetch_one(query=CREATE_PASSWORD_GROUP,
                                values={'user_id': user_id, 'password_id': created_password.id})

        return created_password

    async def get_passwords(self, *, password_post: PasswordCreate, user_id: int) -> PasswordPublic:

        pass

        # return created_password
