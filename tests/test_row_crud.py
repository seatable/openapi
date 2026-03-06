import pytest
from conftest import Base, base_operations_schema
from schemathesis import Case
from syrupy.assertion import SnapshotAssertion
from syrupy.matchers import path_type

from test_base_operations import create_table, append_rows, COLUMNS, ROWS


# Row data for update test — changes many column types at once
UPDATE_ROW = {
    'text': 'updated-text',
    'long-text': '## Updated\n- New Item 1\n- New Item 2',
    'number': 999.01,
    'number-decimal-dot-thousands-comma': 2_000_000.456,
    'number-percent': 99.5,
    'number-euro': 42.00,
    'date-iso': '2031/12/31',
    'date-iso-hours-minutes': '2031/12/31 11:30',
    'date-us': '12/31/2031',
    'date-us-hours-minutes': '12/31/2031 11:30',
    'date-european': '31/12/2031',
    'date-german': '31.12.2031',
    'date-german-hours-minutes': '31.12.2031 11:30',
    'duration-hours-minutes': '7200',
    'duration-hours-minutes-seconds': '7265',
    'single-select': 'option-2',
    'multiple-select': ['option-3'],
    'email': 'updated@seatable.io',
    'url': 'https://cloud.seatable.io',
    'checkbox': False,
    'rate': 10,
    'geolocation-country-region': {'country_region': 'France'},
    'geolocation-lat-lon': {'lng': 2.35, 'lat': 48.86},
}


def test_updateRow(base: Base, snapshot_json: SnapshotAssertion):
    table_name = 'test_updateRow'
    create_table(base, table_name, COLUMNS)
    row_ids = append_rows(base, table_name, [ROWS[0]])

    path_parameters = {'base_uuid': base.uuid}
    body = {
        'table_name': table_name,
        'updates': [
            {
                'row_id': row_ids[0],
                'row': UPDATE_ROW,
            }
        ],
    }
    headers = {'Authorization': f'Bearer {base.token}'}
    case: Case = base_operations_schema.get_operation_by_id('updateRow') \
        .make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200

    # Verify the update by reading the row back
    query = {'table_name': table_name, 'convert_keys': True}
    case: Case = base_operations_schema.get_operation_by_id('getRow') \
        .make_case(path_parameters={'base_uuid': base.uuid, 'row_id': row_ids[0]}, query=query, headers=headers)
    response = case.call()

    assert response.status_code == 200

    data = response.json()
    assert data['text'] == 'updated-text'
    assert data['number'] == 999.01
    assert data['checkbox'] is False
    assert data['single-select'] == 'option-2'
    assert data['email'] == 'updated@seatable.io'
    assert data['rate'] == 10

    matcher = path_type({
        '_id': (str,),
        '_ctime': (str,),
        '_mtime': (str,),
        '_creator': (str,),
        '_last_modifier': (str,),
        'auto-number-date-prefix': (str,),
    })

    assert snapshot_json(matcher=matcher) == data


def test_updateRow_multiple(base: Base):
    table_name = 'test_updateRow_multiple'
    create_table(base, table_name, COLUMNS)
    row_ids = append_rows(base, table_name, ROWS[:3])

    path_parameters = {'base_uuid': base.uuid}
    body = {
        'table_name': table_name,
        'updates': [
            {'row_id': row_ids[0], 'row': {'text': 'updated-1', 'number': 10, 'single-select': 'option-3', 'checkbox': False}},
            {'row_id': row_ids[1], 'row': {'text': 'updated-2', 'number': 20, 'single-select': 'option-1', 'rate': 5}},
            {'row_id': row_ids[2], 'row': {'text': 'updated-3', 'number': 30, 'email': 'multi@seatable.io', 'url': 'https://seatable.io'}},
        ],
    }
    headers = {'Authorization': f'Bearer {base.token}'}
    case: Case = base_operations_schema.get_operation_by_id('updateRow') \
        .make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200


def test_deleteRow(base: Base):
    table_name = 'test_deleteRow'
    create_table(base, table_name, COLUMNS)
    row_ids = append_rows(base, table_name, [
        ROWS[0],
        ROWS[1],
        {'text': 'keep'},
    ])

    path_parameters = {'base_uuid': base.uuid}
    body = {
        'table_name': table_name,
        'row_ids': [row_ids[0], row_ids[1]],
    }
    headers = {'Authorization': f'Bearer {base.token}'}
    case: Case = base_operations_schema.get_operation_by_id('deleteRow') \
        .make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200

    # Verify only one row remains
    query = {'table_name': table_name, 'convert_keys': True}
    case: Case = base_operations_schema.get_operation_by_id('listRows') \
        .make_case(path_parameters=path_parameters, query=query, headers=headers)
    response = case.call()

    assert response.status_code == 200
    assert len(response.json()['rows']) == 1
    assert response.json()['rows'][0]['text'] == 'keep'


def test_lockRows(base: Base):
    table_name = 'test_lockRows'
    create_table(base, table_name, COLUMNS)
    row_ids = append_rows(base, table_name, [ROWS[0]])

    path_parameters = {'base_uuid': base.uuid}
    headers = {'Authorization': f'Bearer {base.token}'}

    # Lock
    body = {'table_name': table_name, 'row_ids': row_ids}
    case: Case = base_operations_schema.get_operation_by_id('lockRows') \
        .make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200

    # Unlock
    case: Case = base_operations_schema.get_operation_by_id('unlockRows') \
        .make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200
