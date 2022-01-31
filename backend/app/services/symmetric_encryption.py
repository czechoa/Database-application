from http.client import HTTPException

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from typing import Optional

from app.models.password import PasswordCreate, PasswordInDB, PasswordUpdate, PasswordDecrypted


class Crypt:

    def create_iv_salt_crypt_password(self, *, password: PasswordCreate) -> PasswordUpdate:
        iv = get_random_bytes(16)
        salt = get_random_bytes(16)
        password_crypt = self.crypt(key=password.key,salt= salt,iv= iv,password= password.password)
        passwordUpgrade = PasswordUpdate(
            **{'description': password.description, 'password': password_crypt, 'iv': iv, 'salt': salt})

        return passwordUpgrade

    def crypt(self, *, key: str, salt: bytes, iv: bytes, password: str) -> bytes:
        aes = AES.new(PBKDF2(key, salt), AES.MODE_CBC, iv)

        data = bytes(password, 'utf-8')
        n = 16 - len(data) % 16
        data_final = data + bytes(n)  # padding
        encd = aes.encrypt(data_final)

        return encd

    def decrypt(self, *, key:str,  password_db: PasswordInDB) -> PasswordDecrypted:
        aes = AES.new(PBKDF2(key, password_db.salt), AES.MODE_CBC, password_db.iv)
        decd = aes.decrypt(password_db.password)
        password_decrypt = decd.decode("utf-8")
        password_decrypt = password_decrypt[:password_decrypt.index("\u0000")] # delete padding
        return PasswordDecrypted(** {'id': password_db.id, 'description': password_db.description, 'password':password_decrypt})




