from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (check_project_could_be_deleted,
                                check_project_data_for_create,
                                check_project_exist,
                                check_project_name_duplicate,
                                check_update_possibility)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.schemas.charity_project import (CharityProjectCreateUpdate,
                                         CharityProjectResponse,
                                         CharityProjectResponseSuperuser)
from app.services.donation import distribute_donations

router = APIRouter()


@router.get(
    '/',
    response_model=List[CharityProjectResponse],
    response_model_exclude_none=True,
)
async def get_all_charity_projects(
        session: AsyncSession = Depends(get_async_session),
):
    """Возвращает список всех проектов."""

    projects = await charity_project_crud.get_multi(session)
    return projects


@router.post(
    '/',
    response_model=CharityProjectResponse,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)]
)
async def create_charity_project(
        projectdata: CharityProjectCreateUpdate,
        session: AsyncSession = Depends(get_async_session),
):
    """Эндпоинт для создания проекта."""

    await check_project_data_for_create(projectdata)
    await check_project_name_duplicate(projectdata.name, session)

    project = await charity_project_crud.create(projectdata, session)

    # Распределение донатов, если таковые имеются
    dontaion, project = await distribute_donations(project, session)

    return project


@router.patch(
    '/{project_id}',
    response_model=CharityProjectResponseSuperuser,
    response_model_exclude_none=False,
    dependencies=[Depends(current_superuser)]
)
async def update_charity_project(
        project_id: int,
        obj_in: CharityProjectCreateUpdate,
        session: AsyncSession = Depends(get_async_session),
):
    """Эндпоинт редактирования проекта."""

    project = await check_project_exist(project_id, session)
    await check_update_possibility(project, obj_in, session)

    project = await charity_project_crud.update(project, obj_in, session)

    return project


@router.delete(
    '/{project_id}',
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)]
)
async def delete_charity_project(
        project_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """Эндпоинт удаления проекта."""

    project = await check_project_could_be_deleted(project_id, session)

    project = await charity_project_crud.remove(project, session)
    return project
