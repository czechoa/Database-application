from typing import List
from fastapi import APIRouter, Body, Depends, status, HTTPException
from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.courses import get_course_by_id_from_path, check_course_modification_permissions
from app.api.dependencies.database import get_repository
from app.models.course import CourseInDB, CoursePublic, CourseCreate, CourseCreateWithSkills
from app.db.repositories.courses import CoursesRepository
from app.models.payment import PaymentInDB
from app.models.user import UserInDB

router = APIRouter()


@router.get("/rating/{course_id}/",
            response_model=int,
            name="courses:get-course-rating")
async def get_course_rating(
        course: CourseInDB = Depends(get_course_by_id_from_path),
        courses_repo: CoursesRepository = Depends(get_repository(CoursesRepository)),
) -> int:
    return await courses_repo.get_course_mean_rating(course_id=course.id)



@router.get("/get_all_course/", response_model=List[CoursePublic], name="courses:get-all-course")
async def get_all_course(courses_repo: CoursesRepository = Depends(get_repository(CoursesRepository))) -> List[
    CoursePublic]:
    return await courses_repo.list_all_courses()





@router.get(
    "/get_all_user_buying_courses/",
    response_model=List[CourseCreateWithSkills],
    name="courses:get-my-buying_courses",
)
async def get_all_buy_course_by_user(
        current_user: UserInDB = Depends(get_current_active_user),
        courses_repo: CoursesRepository = Depends(get_repository(CoursesRepository)),
) -> List[CourseCreateWithSkills]:
    return await courses_repo.list_all_user_buying_courses(user=current_user)
    # return None

@router.get("/get_all_user_course/", response_model=List[CoursePublic], name="courses:get-all-user-course")
async def get_all_course(
        current_user: UserInDB = Depends(get_current_active_user),
        courses_repo: CoursesRepository = Depends(get_repository(CoursesRepository))) -> List[
    CoursePublic]:
    return await courses_repo.get_courses_by_author(name=current_user.username)



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




# @router.get("/{course_id}/", response_model=CoursePublic, name="course:get-course-by-id")
# async def get_course_by_id(course: CourseInDB = Depends(get_course_by_id_from_path)) -> CoursePublic:
#     return course


@router.post("/", response_model=CourseCreateWithSkills, name="courses:create-course-with-skills",
             status_code=status.HTTP_201_CREATED)
async def create_new_course(
        new_course: CourseCreateWithSkills = Body(..., embed=True),
        current_user: UserInDB = Depends(get_current_active_user),
        course_repo: CoursesRepository = Depends(get_repository(CoursesRepository)),

) -> CourseCreateWithSkills:
    # course = await course_repo.create_course(new_course=CourseCreate(**new_course.dict()), requesting_user=current_user)
    course = await course_repo.create_course_with_skills(new_course=new_course, requesting_user=current_user)

    return new_course


@router.delete(
    "/{course_id}/",
    response_model=int,
    name="courses:delete-course-by-id",
    dependencies=[Depends(check_course_modification_permissions)],
)
async def delete_course_by_id(
        course: CourseInDB = Depends(get_course_by_id_from_path),
        courses_repo: CoursesRepository = Depends(get_repository(CoursesRepository)),
) -> int:
    return await courses_repo.delete_course_by_id(course_id=course.id)
