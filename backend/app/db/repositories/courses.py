from typing import List
from app.db.repositories.base import BaseRepository
from app.db.repositories.skills import CREATE_SKILL_QUERY_IF_NOT_EXITS, CREATE_CONNECT_SKILL_TO_COURSE_QUERY
from app.models.course import CourseCreate, CourseInDB, CoursePublic, CourseCreateWithSkills
from app.models.skill import SkillInDB, SkillConnectionINDB, SkillPublic, SkillCreate, SkillsPublic
from app.models.user import UserInDB

CREATE_COURSE_QUERY = """
    INSERT INTO Courses (name, description, price, owner)
    VALUES (:name, :description, :price, :owner)
    RETURNING id, name, description, price, owner, created_at, updated_at;
"""
# GET_COURSE_BY_ID_QUERY = """
#     SELECT c.id, c.name, c.description, c.price,  c.created_at, c.updated_at, u.username as owner
#     FROM Courses c join users u on u.id = c.owner
#     WHERE c.id = :id;
# """
GET_COURSE_BY_ID_QUERY = """
    SELECT * 
    FROM Courses c 
    WHERE c.id = :id;
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

LIST_ALL_COURSES_BUYING_BY_USER_QUERY = """
    select c.id, c.name, c.description, c.price,  c.created_at, c.updated_at, u.username as owner
    from payments p join users u on u.id = p.user_id
    join courses c on p.course_id = c.id
    where u.id = :user_id;
"""

LIST_COURSE_SKILLS = """
    select c.id,s.name
    from skills s
    join skills_courses sc on s.id = sc.id_skill
    join courses c on sc.id_course = c.id
    where c.id= :id;
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

    async def create_course_with_skills(self, *, new_course: CourseCreateWithSkills,
                                        requesting_user: UserInDB) -> CourseInDB:
        course = await self.db.fetch_one(
            query=CREATE_COURSE_QUERY, values={**CourseCreate(**new_course.dict()).dict(), "owner": requesting_user.id}
        )
        course = CourseInDB(**course)
        # print('\n' * 10)
        # print(new_course.skills.skills)

        for skill in new_course.skills.skills:
            # print(skill)
            created_skill = await self.db.fetch_one(query=CREATE_SKILL_QUERY_IF_NOT_EXITS,
                                                    values={"name": skill.name})

            created_skill = SkillInDB(**created_skill)

            await self.db.fetch_one(query=CREATE_CONNECT_SKILL_TO_COURSE_QUERY,
                                    values={"id_course": course.id, "id_skill": created_skill.id})
            # id = SkillConnectionINDB(**id)
            # print(created_skill,id)

        return course

    async def get_courses_by_author(self, *, name: str) -> List[CoursePublic]:
        course_records = await self.db.fetch_all(query=GET_COURSES_BY_AUTHOR_QUERY, values={"author": name})
        if not course_records:
            return None

        return [CoursePublic(**l) for l in course_records]

    async def get_course_by_id(self, *, id: int) -> CourseInDB:

        cleaning = await self.db.fetch_one(query=GET_COURSE_BY_ID_QUERY, values={"id": id})
        if not cleaning:
            return None
        return CourseInDB(**cleaning)

    async def list_all_courses(self) -> List[CoursePublic]:
        course_records = await self.db.fetch_all(
            query=LIST_ALL_COURSE_QUERY, values=None
        )
        return [CoursePublic(**l) for l in course_records]

    async def list_all_user_courses(self, *, owner: int) -> List[CoursePublic]:
        course_records = await self.db.fetch_all(
            query=LIST_ALL_USER_COURSES_QUERY, values={"owner_id": owner}
        )
        return [CoursePublic(**l) for l in course_records]

    async def delete_course_by_id(self, *, course_id: int) -> int:
        return await self.db.execute(query=DELETE_COURSE_BY_ID_QUERY, values={"id": course_id})

    async def list_all_user_buying_courses(self, *, user: UserInDB) -> List[CourseCreateWithSkills]:
        print('tralalaa in repo')
        print(type(user))
        course_records = await self.db.fetch_all(
            query=LIST_ALL_COURSES_BUYING_BY_USER_QUERY, values={"user_id": user.id}
        )
        print('\n' * 10)
        courses_with_skills = []
        for course in [CoursePublic(**l) for l in course_records]:
            skills_records = await self.db.fetch_all(
                query=LIST_COURSE_SKILLS, values={"id": course.id}
            )
            skills = [SkillPublic(**l) for l in skills_records]
            skills_public  = SkillsPublic(skills = skills)
            course_with_skills = CourseCreateWithSkills(**course.dict(),skills= skills_public)
            courses_with_skills.append(course_with_skills)
        # return [CoursePublic(**l) for l in course_records]
        return courses_with_skills

        # return [CoursePublic(**l) for l in course_records]
