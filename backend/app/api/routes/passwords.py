from fastapi import Depends, HTTPException, status, APIRouter, Body, Path

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.database import get_repository
from app.models.password import PasswordPublic,PasswordCreate
from app.models.password_group import PasswordGroupCreate,PasswordGroupPublic

from app.db.repositories.passwords import PasswordsRepository

from app.models.user import UserInDB

router = APIRouter()

@router.post("/", response_model= PasswordPublic, name="password:create_password")
async def create_password(
        current_user: UserInDB = Depends(get_current_active_user),
        passwords_repo: PasswordsRepository = Depends(get_repository(PasswordsRepository)),
        new_password: PasswordCreate = Body(..., embed=True),
) -> PasswordPublic:
    password_pub = await passwords_repo.create_password(password_post=new_password,user_id=current_user.id)
    return password_pub


@router.post("/share_password/", response_model= None, name="password:share_password")
async def share_password(
        passwords_repo: PasswordsRepository = Depends(get_repository(PasswordsRepository)),
        current_user: UserInDB = Depends(get_current_active_user),
        new_Password:PasswordGroupCreate  = Body(..., embed=True),

) -> None:
    pass
    # return await Passwords_repo.create_Password_and_connect_to_course(Password_post = new_Password)

@router.get("/get_password/", response_model= PasswordPublic, name="password:get_password")
async def get_password(
        Passwords_repo: PasswordsRepository = Depends(get_repository(PasswordsRepository)),

) -> PasswordPublic:
    pass

@router.post("/decrypt_password/", response_model= None, name="password:decrypt_password")
async def decrypt_password(
        # Passwords_repo: PasswordsRepository = Depends(get_repository(PasswordsRepository)),
        # new_Password: PasswordConnection = Body(..., embed=True),

) -> None:
    pass

@router.delete("/delete_password/", response_model= None, name="password:delete_password")
async def delete_password(
        # Passwords_repo: PasswordsRepository = Depends(get_repository(PasswordsRepository)),
        # id_course: int = 1,
    # new_Passwords: PasswordsPublic = Body(..., embed=True),
) -> None:
    pass
    # return await Passwords_repo.create_Passwords(Passwords_post = new_Passwords,id_course = id_course)


