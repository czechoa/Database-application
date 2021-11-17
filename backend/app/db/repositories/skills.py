from app.db.repositories.base import BaseRepository
from app.models.skill import SkillCreate, SkillInDB, SkillConnection

CREATE_SKILL_QUERY = """
    insert into skills (name)
    values (:name)
    RETURNING id,name;
"""
CONNECT_SKILL_TO_COURSE_QUERY = """
    WITH rows AS (
        insert into skills (name)
        values (:name)
        RETURNING id
        )
    INSERT INTO skills_courses (id_course,id_skill)
        SELECT :id_course,id as id_skill
        FROM rows
        RETURNING id_course;
"""

class SkillsRepository(BaseRepository):

    async def create_skill(self, *, skill_post: SkillCreate) -> SkillInDB:
        created_skill = await self.db.fetch_one(query=CREATE_SKILL_QUERY, values=skill_post.dict())
        return created_skill

    async def create_skill_and_connect_to_course(self, *, skill_post: SkillConnection) -> SkillConnection:
        created_skill = await self.db.fetch_one(query=CONNECT_SKILL_TO_COURSE_QUERY, values= skill_post.dict())
        # d  = skill_post.dict()
        # d['id_skill'] = created_skill['id']
        # d['id_course'] = id_course
        # created_connection = await self.db.fetch_one(query=CONNECT_SKILL_TO_COURSE_QUERY, values=d)

        return created_skill


