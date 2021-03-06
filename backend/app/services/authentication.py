import jwt
import bcrypt
from datetime import datetime, timedelta
from passlib.context import CryptContext

from typing import Optional
from fastapi import HTTPException, status
from pydantic import ValidationError

from app.core.config import SECRET_KEY, JWT_ALGORITHM, JWT_AUDIENCE, JWT_TOKEN_PREFIX, ACCESS_TOKEN_EXPIRE_MINUTES
from app.models.token import JWTMeta, JWTCreds, JWTPayload
from app.models.user import UserBase, UserPasswordUpdate, UserSuperPasswordUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthException(BaseException):
    pass


class AuthService:
    pepper = 'this_is_rando+papper_#_234'
    def create_salt_and_hashed_password(self, *, plaintext_password: str) -> UserPasswordUpdate:
        salt = self.generate_salt()
        hashed_password = self.hash_password(password=plaintext_password, salt=salt, pepper= self.pepper)

        return UserPasswordUpdate(salt=salt, password=hashed_password)

    def create_super_salt_and_hashed_password(self, *, plaintext_password: str) -> UserPasswordUpdate:
        salt = self.generate_salt()
        hashed_password = self.hash_password(password=plaintext_password, salt=salt, pepper= self.pepper)

        return UserSuperPasswordUpdate(super_salt=salt, super_password=hashed_password)

    def generate_salt(self) -> str:
        return bcrypt.gensalt().decode()

    def hash_password(self, *, password: str, salt: str, pepper: str) -> str:
        return pwd_context.hash(pepper + password + salt)

    def verify_password(self, *, password: str, salt: str, hashed_pw: str) -> bool:
        return pwd_context.verify(self.pepper + password + salt, hashed_pw)

    def verify_super_password(self, *, super_password: str, super_salt: str, hashed_pw: str) -> bool:
        return pwd_context.verify(self.pepper + super_password + super_salt, hashed_pw)

    def create_access_token_for_user(
        self,
        *,
        user: UserBase,
        secret_key: str = str(SECRET_KEY),
        audience: str = JWT_AUDIENCE,
        expires_in: int = ACCESS_TOKEN_EXPIRE_MINUTES,
    ) -> str:
        if not user or not isinstance(user, UserBase):
            return None

        jwt_meta = JWTMeta(
            aud=audience,
            iat=datetime.timestamp(datetime.utcnow()),
            exp=datetime.timestamp(datetime.utcnow() + timedelta(minutes=expires_in)),
        )
        jwt_creds = JWTCreds(sub=user.email, username=user.username)
        token_payload = JWTPayload(**jwt_meta.dict(), **jwt_creds.dict(),)
        # access_token = jwt.encode(token_payload.dict(), secret_key, algorithm=JWT_ALGORITHM).decode("utf-8")
        access_token = jwt.encode(token_payload.dict(), secret_key, algorithm=JWT_ALGORITHM)
        return access_token

    def get_username_from_token(self, *, token: str, secret_key: str) -> Optional[str]:
        try:
            decoded_token = jwt.decode(token, str(secret_key), audience=JWT_AUDIENCE, algorithms=[JWT_ALGORITHM])
            payload = JWTPayload(**decoded_token)
        except (jwt.PyJWTError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate token credentials.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return payload.username
