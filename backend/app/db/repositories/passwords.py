from fastapi import HTTPException, status
from fastapi.logger import logger
from starlette.status import HTTP_400_BAD_REQUEST
from databases import Database

from typing import List
from app.db.repositories.base import BaseRepository
from app.db.repositories.users import GET_USER_BY_USERNAME_QUERY
from app.models.password import PasswordPublic, PasswordCreate, PasswordInDB
from app.models.passwordDecrypt import PasswordToDecrypt

from app.models.password_group import PasswordGroupPublic, PasswordGroupCreate
from app.models.user import UserInDB
from app.services.symmetric_encryption import Crypt

CREATE_PASSWORD_QUERY = """
    insert into passwords (description,password, salt,iv)
    values (:description,:password,:salt,:iv)
    RETURNING id,description;
"""

CREATE_PASSWORD_GROUP = """
    insert into password_groups (user_id, password_id)
    values (:user_id,:password_id)
"""
GET_PASSWORD_BY_USER_ID_QUERY = """
    select id, description
    from passwords
    join password_groups pg on passwords.id = pg.password_id
    where user_id =:user_id;
"""
GET_PASSWORD_BY_USER_AND_PASSWORD_ID_ID_QUERY = """
    select   id,description,password,salt,iv
    from passwords
    join password_groups pg on passwords.id = pg.password_id
    where user_id =:user_id and password_id=:password_id;
"""


CREATE_NEW_PASSWORD_GROUP = """
    insert into password_groups (user_id, password_id)
    values (:user_id,:password_id);
"""

GET_PASSWORD_GROUP_BY_USER_NAME_PASSWORD_ID = """
    select user_id, password_id
    from password_groups
    join users u on u.id = password_groups.user_id
    where  username = :username and
          password_id= :password_id;
"""

class PasswordsRepository(BaseRepository):

    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.Crypt = Crypt()

    async def create_password(self, *, password_post: PasswordCreate, user_id: int) -> PasswordPublic:

        passwordUpgrade = self.Crypt.create_iv_salt_crypt_password(password=password_post)

        password_record = await self.db.fetch_one(query=CREATE_PASSWORD_QUERY, values=passwordUpgrade.dict())

        created_password = PasswordPublic(**password_record)

        await self.db.fetch_one(query=CREATE_PASSWORD_GROUP,
                                values={'user_id': user_id, 'password_id': created_password.id})

        return created_password

    async def get_passwords_description(self, *, user_id: int) -> List[PasswordPublic]:
        password_records = await self.db.fetch_all(query=GET_PASSWORD_BY_USER_ID_QUERY, values={"user_id": user_id})
        if not password_records:
            return None

        return [PasswordPublic(**l) for l in password_records]

    async def share_password(self, *, password_group: PasswordGroupCreate, user_id:int) -> PasswordPublic:

        if not await self.db.fetch_one(query=GET_PASSWORD_BY_USER_AND_PASSWORD_ID_ID_QUERY, values= {'user_id':user_id, "password_id":password_group.password_id}):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="User can shearing only own password."
            )

        user_record = await self.db.fetch_one(query=GET_USER_BY_USERNAME_QUERY, values={"username": password_group.username})

        if not user_record:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="That user don't exits."
            )

        user = UserInDB(**user_record)


        if await self.db.fetch_one(query=GET_PASSWORD_GROUP_BY_USER_NAME_PASSWORD_ID, values=password_group.dict()):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="That password has already been shared."
            )

        await self.db.fetch_one(query=CREATE_NEW_PASSWORD_GROUP, values={"user_id":user.id, "password_id": password_group.password_id})

        return PasswordGroupPublic(**password_group.dict())

    async def get_decrypt_Password(self, *,passwordToDecrypt :PasswordToDecrypt, user_id:int) -> PasswordPublic:
        password_record = await self.db.fetch_one(query=GET_PASSWORD_BY_USER_AND_PASSWORD_ID_ID_QUERY, values= {'user_id':user_id, "password_id":passwordToDecrypt.password_id})
        if not password_record:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="User cannot decrypt not own password."
            )

        password_db = PasswordInDB(**password_record)
        try:
            password_decrypt = self.Crypt.decrypt(key=passwordToDecrypt.key, password_db=password_db)
        except UnicodeError:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="Probably key ist wrong, algorytm can't decrypt password."
            )

        return password_decrypt


