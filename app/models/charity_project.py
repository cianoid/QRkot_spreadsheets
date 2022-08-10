from sqlalchemy import Column, String, Text

from app.core.db import DonationBase


class CharityProject(DonationBase):
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
