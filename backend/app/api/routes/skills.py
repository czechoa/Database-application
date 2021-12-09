from fastapi import Depends, HTTPException, status, APIRouter, Body, Path
from app.api.dependencies.database import get_repository
from app.models.skill import SkillPublic,SkillCreate, SkillConnection,SkillConnectionINDB
from app.db.repositories.skills import SkillsRepository

router = APIRouter()

@router.post("/", response_model= SkillPublic, name="skill:create_skill")
async def create_skill(
        skills_repo: SkillsRepository = Depends(get_repository(SkillsRepository)),
        new_skill: SkillCreate = Body(..., embed=True),
) -> SkillPublic:

    return await skills_repo.create_skill( skill_post = new_skill)


@router.post("/skills_connect/", response_model= SkillConnectionINDB, name="skill:f create_skill_and_connect_skill_to_course")
async def create_skill_and_connect_skill_to_course(
        skills_repo: SkillsRepository = Depends(get_repository(SkillsRepository)),
        new_skill: SkillConnection = Body(..., embed=True),

) -> SkillConnectionINDB:

    return await skills_repo.create_skill_and_connect_to_course(skill_post = new_skill)
