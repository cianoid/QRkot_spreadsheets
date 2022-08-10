from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, Field, PositiveInt


class CharityProjectBase(BaseModel):
    name: str = Field(None, min_length=1, max_length=100)
    description: str = Field(None, min_length=1)
    full_amount: PositiveInt = Field(None)

    class Config:
        extra = Extra.forbid


class CharityProjectCreateUpdate(CharityProjectBase):
    pass


class CharityProjectResponse(CharityProjectBase):
    id: int
    fully_invested: bool
    invested_amount: int
    create_date: datetime
    close_date: Optional[datetime]

    class Config:
        orm_mode = True


class CharityProjectResponseSuperuser(CharityProjectResponse):
    close_date: Optional[datetime]
