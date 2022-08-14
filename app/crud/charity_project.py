from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject


class CRUDCharityProject(CRUDBase):
    async def get_project_id_by_name(
            self, project_name: str, session: AsyncSession):
        db_project_id = await session.execute(
            select(CharityProject.id).where(CharityProject.name == project_name))
        db_project_id = db_project_id.scalars().first()

        return db_project_id

    async def get_projects_by_completion_rate(self, session: AsyncSession):
        projects = await session.execute(
            select([
                CharityProject.name, CharityProject.description,
                (
                        func.julianday(CharityProject.close_date) -
                        func.julianday(CharityProject.create_date)
                ).label('duration')
            ]).where(
                CharityProject.fully_invested
            ).order_by('duration')
        )
        projects = projects.all()

        return projects


charity_project_crud = CRUDCharityProject(CharityProject)
