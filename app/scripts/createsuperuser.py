import asyncio
from getpass import getpass

from app.core.init_db import create_first_superuser


async def run(email: str, password: str):
    await create_first_superuser(email, password)


if __name__ == '__main__':
    asyncio.run(run(
        input('Введите адрес электронной почты: '),
        getpass('Введите пароль: ')))
