from typing import List

from fastapi import APIRouter, Body, Depends, status

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.database import get_repository
from app.models.course import CourseInDB, CoursePublic,CourseCreate
from app.db.repositories.courses import CoursesRepository
from app.models.user import UserInDB

router = APIRouter()

@router.get("/{course_all}/", response_model=List[CoursePublic], name="courses:get-all-course")
async def get_all_course( courses_repo: CoursesRepository = Depends(get_repository(CoursesRepository))) -> List[CoursePublic]:
    return await courses_repo.list_all_course()

@router.post("/", response_model=CoursePublic, name="courses:create-course", status_code=status.HTTP_201_CREATED)
async def create_new_course(
    new_course: CourseCreate = Body(..., embed=True),
    current_user: UserInDB = Depends(get_current_active_user),
    course_repo: CoursesRepository = Depends(get_repository(CoursesRepository)),
) -> CoursePublic:
    return await course_repo.create_course(new_cleaning=new_course,requesting_user=current_user)
