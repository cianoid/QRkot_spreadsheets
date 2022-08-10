from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.models import CharityProject
from app.schemas.charity_project import CharityProjectCreateUpdate


async def check_project_exist(
        project_id: int, session: AsyncSession
) -> CharityProject:
    project = await charity_project_crud.get(project_id, session)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Проекта с таким ID не существует',
        )

    return project


async def check_update_possibility(
        project: CharityProject,
        obj_in: CharityProjectCreateUpdate,
        session: AsyncSession
) -> None:
    """Проверка возможности обновления проекта."""

    if project.fully_invested:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Закрытый проект нельзя редактировать!',
        )

    amount_check = isinstance(obj_in.full_amount, int)

    if amount_check and obj_in.full_amount < project.invested_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(f'Сумма должна быть больше или равна '
                    f'{project.invested_amount}'),
        )

    if obj_in.name is not None:
        await check_project_name_duplicate(obj_in.name, session)


async def check_project_data_for_create(
        obj_in: CharityProjectCreateUpdate
) -> None:
    """Проверка данных для создания проекта."""

    if obj_in.name in [None, ""]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Не задано имя проекта',
        )

    if obj_in.description in [None, ""]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Не задано описание проекта',
        )

    if not isinstance(obj_in.full_amount, int):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Сумма должна быть целым числом',
        )


async def check_project_name_duplicate(
        project_name: str,
        session: AsyncSession,
) -> None:
    """Проверка имени проекта на повтор."""

    project_id = await charity_project_crud.get_project_id_by_name(
        project_name, session)

    if project_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Проект с таким именем уже существует!',
        )


async def check_project_could_be_deleted(
        project_id: int,
        session: AsyncSession
) -> CharityProject:
    """Проверка, можно ли удалить проект."""

    project = await check_project_exist(project_id, session)

    if project.invested_amount > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='В проект были внесены средства, не подлежит удалению!',
        )

    return project
