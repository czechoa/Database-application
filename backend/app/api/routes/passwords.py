from fastapi import Depends, HTTPException, status, APIRouter, Body, Path
from typing import List

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.database import get_repository
from app.models.password import PasswordPublic, PasswordCreate, PasswordDecrypted
from app.models.passwordDecrypt import PasswordToDecrypt

from app.models.password_group import PasswordGroupCreate, PasswordGroupPublic

from app.db.repositories.passwords import PasswordsRepository

from app.models.user import UserInDB

router = APIRouter()


@router.post("/", response_model=PasswordPublic, name="password:create_password")
async def create_password(
        current_user: UserInDB = Depends(get_current_active_user),
        passwords_repo: PasswordsRepository = Depends(get_repository(PasswordsRepository)),
        new_password: PasswordCreate = Body(..., embed=True),
) -> PasswordPublic:
    password_pub = await passwords_repo.create_password(password_post=new_password, user_id=current_user.id)
    return password_pub




@router.get("/get_passwords_description/", response_model=List[PasswordPublic],
            name="password:get_passwords_description")
async def get_passwords_description(
        current_user: UserInDB = Depends(get_current_active_user),
        passwords_repo: PasswordsRepository = Depends(get_repository(PasswordsRepository)),
) -> List[PasswordPublic]:
    return await passwords_repo.get_passwords_description(user_id=current_user.id)


@router.post("/share_password/", response_model=None, name="password:share_password")
async def share_password(
        passwords_repo: PasswordsRepository = Depends(get_repository(PasswordsRepository)),
        current_user: UserInDB = Depends(get_current_active_user),
        new_PasswordGroup: PasswordGroupCreate = Body(..., embed=True),

) -> None:
    if current_user.username == new_PasswordGroup.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Action forbidden. The user cannot share the password with himself",
        )

    return await passwords_repo.share_password(password_group=new_PasswordGroup, user_id=current_user.id)

@router.post("/decrypt_password/", response_model=PasswordDecrypted, name="password:decrypt_password")
async def decrypt_password(
        current_user: UserInDB = Depends(get_current_active_user),
        passwords_repo: PasswordsRepository = Depends(get_repository(PasswordsRepository)),
        password_to_decrypt: PasswordToDecrypt = Body(..., embed=True),
) -> PasswordDecrypted:
    return await passwords_repo.get_decrypt_Password(passwordToDecrypt=password_to_decrypt,user_id=current_user.id)






@router.delete("/delete_password/", response_model=None, name="password:delete_password")
async def delete_password(
        # Passwords_repo: PasswordsRepository = Depends(get_repository(PasswordsRepository)),
        # id_course: int = 1,
        # new_Passwords: PasswordsPublic = Body(..., embed=True),
) -> None:
    pass
    # return await Passwords_repo.create_Passwords(Passwords_post = new_Passwords,id_course = id_course)
