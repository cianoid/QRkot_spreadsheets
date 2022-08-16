from datetime import datetime
from typing import List, Tuple

from aiogoogle import Aiogoogle

from app.core.config import settings

FORMAT = '%Y/%m/%d %H:%M:%S'
SHEET_ID = 0
SHEET_ROW_COUNT = 100
SHEET_COLUMN_COUNT = 11
UPDATE_RANGE = 'A1:E30'

RANGE_AUTORESIZE_COLUMN = (0, 3)
RANGE_DURATION_FORMAT_COLUMN = (1, 2)
RANGE_DURATION_FORMAT_ROW = (3, 30)

DURATION_PATTERN = '[h]:mm:ss'


async def spreadsheets_create(wrapper_services: Aiogoogle) -> Tuple:
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover(
        'sheets', settings.sheets_api_version)
    spreadsheet_body = {
        'properties': {
            'title': f'Отчет на {now_date_time}',
            'locale': settings.file_locale},
        'sheets': [
            {
                'properties': {
                    'sheetType': 'GRID',
                    'sheetId': SHEET_ID,
                    'title': 'Лист1',
                    'gridProperties': {
                        'rowCount': SHEET_ROW_COUNT,
                        'columnCount': SHEET_COLUMN_COUNT
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
    service = await wrapper_services.discover('drive', settings.drive_api_version)
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheetid,
            json=permissions_body,
            fields='id'
        ))


async def spreadsheets_update_value(
        spreadsheetid: str,
        projects: List,
        wrapper_services: Aiogoogle
) -> None:
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', settings.sheets_api_version)
    table_values = [
        ['Отчет от', now_date_time],
        ['Топ проектов по скорости закрытия'],
        ['Название проекта', 'Время сбора', 'Описание']
    ]
    for res in projects:
        new_row = [
            str(res['name']),
            str(res['duration']).replace('.', ','),
            str(res['description'])
        ]
        table_values.append(new_row)

    format_body = {
        'requests': [
            {
                'autoResizeDimensions': {
                    'dimensions': {
                        'dimension': 'COLUMNS',
                        'startIndex': RANGE_AUTORESIZE_COLUMN[0],
                        'endIndex': RANGE_AUTORESIZE_COLUMN[1]
                    },
                },
            },
            {
                'repeatCell': {
                    'range': {
                        'sheetId': SHEET_ID,
                        'startRowIndex': RANGE_DURATION_FORMAT_ROW[0],
                        'endRowIndex': RANGE_DURATION_FORMAT_ROW[1],
                        'startColumnIndex': RANGE_DURATION_FORMAT_COLUMN[0],
                        'endColumnIndex': RANGE_DURATION_FORMAT_COLUMN[1],
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'numberFormat': {
                                'type': 'DATE_TIME',
                                'pattern': DURATION_PATTERN,
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

    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheetid,
            range=UPDATE_RANGE,
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )

    await wrapper_services.as_service_account(
        service.spreadsheets.batchUpdate(
            spreadsheetId=spreadsheetid,
            json=format_body)
    )
