from typing import List
from app.db.repositories.base import BaseRepository
from app.db.repositories.skills import CREATE_SKILL_QUERY_IF_NOT_EXITS, CREATE_CONNECT_SKILL_TO_COURSE_QUERY
from app.models.course import CourseCreate, CourseInDB, CoursePublic, CourseCreateWithSkills
from app.models.skill import SkillInDB, SkillConnectionINDB
from app.models.user import UserInDB

CREATE_COURSE_QUERY = """
    INSERT INTO Courses (name, description, price, owner)
    VALUES (:name, :description, :price, :owner)
    RETURNING id, name, description, price, owner, created_at, updated_at;
"""
GET_COURSE_BY_ID_QUERY = """
    SELECT c.id, c.name, c.description, c.price,  c.created_at, c.updated_at, u.username as owner
    FROM Courses c join users u on u.id = c.owner
    WHERE id = :id;
"""

GET_COURSES_BY_AUTHOR_QUERY = """
    SELECT c.id, c.name, c.description, c.price,  c.created_at, c.updated_at, u.username as owner
    FROM Courses c join users u on u.id = c.owner
    WHERE u.username = :author;
"""

LIST_ALL_COURSE_QUERY = """
    SELECT c.id, c.name, c.description, c.price,  c.created_at, c.updated_at, u.username as owner
      FROM Courses c join users u on u.id = c.owner;
"""
LIST_ALL_USER_COURSES_QUERY = """
    SELECT c.id, c.name, c.description, c.price,  c.created_at, c.updated_at, u.username as owner
    FROM Courses c join users u on u.id = c.owner
    WHERE owner = :owner;
"""
DELETE_COURSE_BY_ID_QUERY = """
    DELETE FROM courses
    WHERE id = :id
    RETURNING id;
"""




class CoursesRepository(BaseRepository):
    """"
    All database actions associated with the Course resource
    """

    async def create_course(self, *, new_course: CourseCreate, requesting_user: UserInDB) -> CourseInDB:
        course = await self.db.fetch_one(
            query=CREATE_COURSE_QUERY, values={**new_course.dict(), "owner": requesting_user.id}
        )
        return CourseInDB(**course)

    async def create_course_with_skills(self, *, new_course: CourseCreateWithSkills, requesting_user: UserInDB) -> CourseInDB:
        course = await self.db.fetch_one(
            query=CREATE_COURSE_QUERY, values={**CourseCreate(**new_course.dict()).dict(), "owner": requesting_user.id}
        )
        course = CourseInDB(**course)
        # print('\n' * 10)
        # print(new_course.skills.skills)

        for skill in  new_course.skills.skills:
            # print(skill)
            created_skill = await self.db.fetch_one(query=CREATE_SKILL_QUERY_IF_NOT_EXITS,
                                                    values={"name": skill.name})

            created_skill = SkillInDB(**created_skill)

            id = await self.db.fetch_one(query=CREATE_CONNECT_SKILL_TO_COURSE_QUERY,
                                             values={"id_course": course.id, "id_skill": created_skill.id})
            id = SkillConnectionINDB(**id)
            # print(created_skill,id)

        return course

    async def get_courses_by_author(self, *, name: str) -> List[CoursePublic]:
        course_records = await self.db.fetch_all(query=GET_COURSES_BY_AUTHOR_QUERY, values={"author": name})
        if not course_records:
            return None

        return [CoursePublic(**l) for  l in course_records]


    async def list_all_courses(self) -> List[CoursePublic]:
        course_records = await self.db.fetch_all(
            query=LIST_ALL_COURSE_QUERY, values=None
        )
        return [CoursePublic(**l) for l in course_records]

    async def list_all_user_courses(self, requesting_user: UserInDB) -> List[CoursePublic]:
        course_records = await self.db.fetch_all(
            query=LIST_ALL_USER_COURSES_QUERY, values={"owner": requesting_user.id}
        )
        return [CoursePublic(**l) for l in course_records]

    async def delete_course_by_id(self, *, course: CourseInDB) -> int:
        return await self.db.execute(query=DELETE_COURSE_BY_ID_QUERY, values={"id": course.id})
