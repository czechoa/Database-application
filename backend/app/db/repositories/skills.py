from fastapi import HTTPException, status
from fastapi.logger import logger
from typing import List
from app.db.repositories.base import BaseRepository
from app.models.skill import SkillCreate, SkillInDB, SkillConnection, SkillConnectionPublic, SkillConnectionINDB, SkillsPublic

CREATE_SKILL_QUERY = """
    insert into skills (name)
    values (:name)
    RETURNING id,name;
"""

CREATE_SKILLS_QUERY = """
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
# CREATE_CONNECT_SKILL_TO_COURSE_QUERY = """
#     INSERT INTO skills_courses (id_course,id_skill)
#     values (:id_course,:id_skill)
#     returning id,id_course,id_skill
#
# """
CREATE_CONNECT_SKILL_TO_COURSE_QUERY = """
 with s as (
            select *
            from skills_courses
            where id_course = :id_course and  id_skill  = :id_skill
        ), i as (
            INSERT INTO skills_courses (id_course,id_skill)
            select :id_course,:id_skill
            where not exists (select 1 from s)
            returning id,id_course,id_skill
        )
        select id,id_course,id_skill
        from i
        union all
        select id,id_course,id_skill
        from s
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

    async def create_skills(self, *, skills_post: SkillsPublic,id_course: int) -> SkillsPublic:
        # created_skill = await self.db.fetch_one(query=CREATE_SKILL_QUERY, values=skill_posts.dict())
        print('\n' * 10)

        for skill_post in  skills_post.skills:
            created_skill = await self.db.fetch_one(query=CREATE_SKILL_QUERY_IF_NOT_EXITS,
                                                    values={"name": skill_post.name})
            created_skill = SkillInDB(**created_skill)
            print(created_skill,id_course)
            # course = await self.db.fetch_one(query=LIST_COURSE_BY_NAME_QUERY,
            #                                  values={"id_course": id_course})
            # # if course != None:
            id = await self.db.fetch_one(query=CREATE_CONNECT_SKILL_TO_COURSE_QUERY,
                                             values={"id_course": id_course, "id_skill": created_skill.id})
            # else:
            #     return None
            print(SkillConnectionINDB(**id))

        return skills_post


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



