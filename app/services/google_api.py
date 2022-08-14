from datetime import datetime
from typing import List, Tuple

import aiogoogle.excs
from aiogoogle import Aiogoogle
from fastapi import HTTPException, status

from app.core.config import settings

FORMAT = "%Y/%m/%d %H:%M:%S"


async def spreadsheets_create(wrapper_services: Aiogoogle) -> Tuple:
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    spreadsheet_body = {
        'properties': {
            'title': f'Отчет на {now_date_time}',
            'locale': 'ru_RU'},
        'sheets': [
            {
                'properties': {
                    'sheetType': 'GRID',
                    'sheetId': 0,
                    'title': 'Лист1',
                    'gridProperties': {
                        'rowCount': 100,
                        'columnCount': 11
                    }
                }
            }
        ]
    }
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    return response['spreadsheetId'], response['spreadsheetUrl']


async def set_user_permissions(
        spreadsheetid: str, wrapper_services: Aiogoogle
) -> None:
    permissions_body = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': settings.email
    }
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheetid,
            json=permissions_body,
            fields="id"
        ))


async def spreadsheets_update_value(
        spreadsheetid: str,
        projects: List,
        wrapper_services: Aiogoogle
) -> None:
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    table_values = [
        ['Отчет от', now_date_time],
        ['Топ проектов по скорости закрытия'],
        ['Название проекта', 'Время сбора', 'Описание']
    ]
    for res in projects:
        new_row = [
            str(res['name']), str(res['duration']).replace('.', ','), str(res['description'])]
        table_values.append(new_row)

    format_body = {
        'requests': [
            {
                'autoResizeDimensions': {
                    'dimensions': {
                        'dimension': 'COLUMNS',
                        'startIndex': 0,
                        'endIndex': 3
                    },
                },
            },
            {
                'repeatCell': {
                    'range': {
                        'sheetId': 0,
                        'startRowIndex': 3,
                        'endRowIndex': 30,
                        'startColumnIndex': 1,
                        'endColumnIndex': 2,
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'numberFormat': {
                                'type': 'DATE_TIME',
                                "pattern": "[h]:mm:ss",
                            }
                        }
                    },
                    'fields': 'userEnteredFormat.numberFormat'
                },
            },
        ]
    }

    update_body = {
        'majorDimension': 'ROWS',
        'values': table_values,
    }

    try:
        await wrapper_services.as_service_account(
            service.spreadsheets.values.update(
                spreadsheetId=spreadsheetid,
                range='A1:E30',
                valueInputOption='USER_ENTERED',
                json=update_body
            )
        )

        await wrapper_services.as_service_account(
            service.spreadsheets.batchUpdate(
                spreadsheetId=spreadsheetid,
                json=format_body)
        )
    except aiogoogle.excs.HTTPError as err:
        error = err.res.content.get('error', None)
        message = ': ' + error.get('message') if error is not None else ''

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='API Google вернул ошибку' + message,
        )
