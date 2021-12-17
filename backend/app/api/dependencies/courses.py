from fastapi import HTTPException, Depends, Path, status
from app.models.user import UserInDB
from app.models.course import CourseInDB
from app.db.repositories.courses import CoursesRepository
from app.api.dependencies.database import get_repository
from app.api.dependencies.auth import get_current_active_user

async def get_course_by_id_from_path(
    course_id: int = Path(..., ge=1),
    current_user: UserInDB = Depends(get_current_active_user),
    courses_repo: CoursesRepository = Depends(get_repository(CoursesRepository)),
) -> CourseInDB:
    print(course_id)
    course = await courses_repo.get_course_by_id(id=course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No course found with that id.",
        )

    return course

def check_course_modification_permissions(
    current_user: UserInDB = Depends(get_current_active_user),
    course: CourseInDB = Depends(get_course_by_id_from_path),
) -> None:
    if course.owner != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Action forbidden. Users are only able to modify courses they own.",
        )
