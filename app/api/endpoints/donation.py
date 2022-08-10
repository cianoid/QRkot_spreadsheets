from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.donation import donation_crud
from app.models import User
from app.schemas.donation import (DonationCreate, DonationReponse,
                                  DonationReponseSuperuser)
from app.services.donation import make_donation

router = APIRouter()


@router.get(
    '/',
    response_model=List[DonationReponseSuperuser],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)]
)
async def get_all_donations(
        session: AsyncSession = Depends(get_async_session),
):
    """Вывод всех донатов."""

    donations = await donation_crud.get_multi(session)

    return donations


@router.post(
    '/',
    response_model=DonationReponse,
    response_model_exclude_none=True,
    dependencies=[Depends(current_user)]
)
async def create_donation(
        obj_in: DonationCreate,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user),
):
    """Создание доната."""

    donation = await donation_crud.create(obj_in, session, user)

    # Процесс доната в открытые проекты
    donation, project = await make_donation(donation, session)

    return donation


@router.get(
    '/my',
    response_model=List[DonationReponse],
    response_model_exclude_none=True,
    dependencies=[Depends(current_user)]
)
async def get_user_donations(
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user),
):
    """Выводит все донаты конкретного юзера."""

    donations = await donation_crud.get_multi_by_attribute(
        'user_id', user.id, session)

    return donations
