import datetime
from typing import Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.models.charity_project import CharityProject
from app.models.donation import Donation


async def proceed_dontaion(
        donation: Donation, project: CharityProject, session: AsyncSession
) -> Tuple:
    donation_left_amount = donation.full_amount - donation.invested_amount
    project_left_amount = project.full_amount - project.invested_amount

    close_project = False
    close_dontaion = False

    if project_left_amount > donation_left_amount:
        project.invested_amount += donation_left_amount
        close_dontaion = True
    elif project_left_amount < donation_left_amount:
        close_project = True
        donation.invested_amount += project_left_amount
    else:
        close_project = True
        close_dontaion = True

    if close_dontaion:
        donation.invested_amount = donation.full_amount
        donation.close_date = datetime.datetime.now()
        donation.fully_invested = True

    if close_project:
        project.invested_amount = project.full_amount
        project.close_date = datetime.datetime.now()
        project.fully_invested = True

    session.add(project)
    session.add(donation)
    await session.commit()
    await session.refresh(donation)
    await session.refresh(project)

    return donation, project


async def make_donation(
        donation: Donation, session: AsyncSession) -> Tuple:
    project = await charity_project_crud.get_by_attribute(
        'fully_invested', '0', session
    )

    if not project:
        return donation, None

    dontaion, project = await proceed_dontaion(donation, project, session)

    if not donation.fully_invested:
        donation, project = await make_donation(donation, session)
        return donation, project

    return dontaion, project


async def distribute_donations(
        project: CharityProject, session: AsyncSession
) -> Tuple:
    donation = await donation_crud.get_by_attribute(
        'fully_invested', '0', session)

    if not donation or project.fully_invested:
        return None, project

    dontaion, project = await proceed_dontaion(donation, project, session)

    dontaion, project = await distribute_donations(project, session)

    return dontaion, project
