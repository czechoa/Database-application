from typing import List

from fastapi import APIRouter, Body, Depends, status, HTTPException

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.course import get_course_by_id_from_path, check_course_modification_permissions
from app.api.dependencies.database import get_repository
from app.models.course import CourseInDB, CoursePublic, CourseCreate
from app.db.repositories.courses import CoursesRepository
from app.models.user import UserInDB

router = APIRouter()


@router.get("/course_all/", response_model=List[CoursePublic], name="courses:get-all-course")
async def get_all_course(courses_repo: CoursesRepository = Depends(get_repository(CoursesRepository))) -> List[
    CoursePublic]:
    return await courses_repo.list_all_courses()


@router.post("/", response_model=CoursePublic, name="courses:create-course", status_code=status.HTTP_201_CREATED)
async def create_new_course(
        new_course: CourseCreate = Body(..., embed=True),
        current_user: UserInDB = Depends(get_current_active_user),
        course_repo: CoursesRepository = Depends(get_repository(CoursesRepository)),
) -> CoursePublic:
    return await course_repo.create_course(new_course=new_course, requesting_user=current_user)


@router.get("/", response_model=List[CoursePublic], name="courses:list-all-user-courses")
async def get_list_all_user_courses(
        current_user: UserInDB = Depends(get_current_active_user),
        courses_repo: CoursesRepository = Depends(get_repository(CoursesRepository)),
) -> List[CoursePublic]:
    return await courses_repo.list_all_user_courses(requesting_user=current_user)


@router.get("/{course_author}/", response_model=List[CoursePublic], name="courses:get-courses-by-author")
async def get_courses_by_author(
        course_author: str = 'string',
        courses_repo: CoursesRepository = Depends(get_repository(CoursesRepository)),
) -> List[CoursePublic]:
    course = await courses_repo.get_courses_by_author(name=course_author)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No course found create by",
        )
    return course


@router.delete(
    "/{course_id}/",
    response_model=int,
    name="Courses:delete-Course-by-id",
    dependencies=[Depends(check_course_modification_permissions)],
)
async def delete_course_by_id(
        Course: CourseInDB = Depends(get_course_by_id_from_path),
        Courses_repo: CoursesRepository = Depends(get_repository(CoursesRepository)),
) -> int:
    return await Courses_repo.delete_course_by_id(Course=Course)
