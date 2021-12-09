from fastapi import HTTPException, status
from fastapi.logger import logger
from app.db.repositories.base import BaseRepository
from app.models.skill import SkillCreate, SkillInDB, SkillConnection, SkillConnectionPublic, SkillConnectionINDB

CREATE_SKILL_QUERY = """
    insert into skills (name)
    values (:name)
    RETURNING id,name;
"""


CREATE_SKILL_QUERY_IF_NOT_EXITS = """
    with s as (
            select id, name
            from skills
            where name = :name
        ), i as (
            insert into skills (name)
            select :name
            where not exists (select 1 from s)
            returning id, name
        )
        select id ,name
        from i
        union all
        select id ,name
        from s
"""

# CONNECT_SKILL_TO_COURSE_QUERY = """
#     WITH rows AS (
#         with s as (
#             select id, name
#             from skills
#             where name = :name
#         ), i as (
#             insert into skills (name)
#             select :name
#             where not exists (select 1 from s)
#             returning id, name
#         )
#         select id
#         from i
#         union all
#         select id
#         from s
#         )
#     INSERT INTO skills_courses (id_course,id_skill)
#         SELECT :id_course,id as id_skill
#         FROM rows
#         RETURNING id;
# """
CREATE_CONNECT_SKILL_TO_COURSE_QUERY = """
    INSERT INTO skills_courses (id_course,id_skill)
    values (:id_course,:id_skill)
    returning id,id_course,id_skill
"""

LIST_SKILL_BY_NAME_QUERY = """
    select * from skills 
    where name = :name
"""
LIST_COURSE_BY_NAME_QUERY = """
    select * from courses 
    where id = :id_course
"""

class SkillsRepository(BaseRepository):

    async def create_skill(self, *, skill_post: SkillCreate) -> SkillInDB:
        created_skill = await self.db.fetch_one(query=CREATE_SKILL_QUERY, values=skill_post.dict())

        return created_skill

    async def create_skill_and_connect_to_course(self, *, skill_post: SkillConnection) -> SkillConnectionINDB:
        created_skill = await self.db.fetch_one(query=CREATE_SKILL_QUERY_IF_NOT_EXITS, values= {"name": skill_post.name})
        created_skill = SkillInDB(**created_skill)
        #
        course = await self.db.fetch_one(query=LIST_COURSE_BY_NAME_QUERY, values= {"id_course": skill_post.id_course})
        if course != None:
            id = await self.db.fetch_one(query=CREATE_CONNECT_SKILL_TO_COURSE_QUERY, values= {"id_course":skill_post.id_course,"id_skill":created_skill.id})
        else:
            return None
        return id



