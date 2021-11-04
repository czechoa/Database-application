from typing import List
from app.db.repositories.base import BaseRepository
from app.models.course import CourseCreate, CourseInDB, CoursePublic
from app.models.user import UserInDB
CREATE_COURSE_QUERY = """
    INSERT INTO Courses (name, description, price, owner)
    VALUES (:name, :description, :price, :owner)
    RETURNING id, name, description, price, owner, created_at, updated_at;
"""

# LIST_ALL_COURSE_QUERY = """
#     SELECT id, name, description, price, owner, created_at, updated_at
#     FROM Courses
# """

LIST_ALL_COURSE_QUERY = """
    SELECT c.id, c.name, c.description, c.price,  c.created_at, c.updated_at, u.username as owner
      FROM Courses c join users u on u.id = c.owner;
"""

class CoursesRepository(BaseRepository):
    """"
    All database actions associated with the Cleaning resource
    """
    async def create_course(self, *, new_cleaning: CourseCreate,  requesting_user: UserInDB) -> CourseInDB:
        course = await self.db.fetch_one(
            query=CREATE_COURSE_QUERY, values={**new_cleaning.dict(), "owner": requesting_user.id}
        )
        return CourseInDB(**course)

    async def list_all_course(self) -> List[CoursePublic]:
        course_records = await self.db.fetch_all(
            query=LIST_ALL_COURSE_QUERY, values = None
        )
        return [CoursePublic(**l) for l in course_records]


