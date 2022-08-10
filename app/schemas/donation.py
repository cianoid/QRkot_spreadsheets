from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, PositiveInt


class DonationBase(BaseModel):
    full_amount: PositiveInt
    comment: Optional[str]

    class Config:
        extra = Extra.forbid


class DonationCreate(DonationBase):
    pass


class DonationReponse(DonationBase):
    id: int
    create_date: datetime

    class Config:
        orm_mode = True


class DonationReponseSuperuser(DonationReponse):
    fully_invested: bool
    invested_amount: int
    user_id: int
