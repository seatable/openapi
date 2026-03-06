import pytest
from conftest import Base, base_operations_schema
from schemathesis import Case
from syrupy.assertion import SnapshotAssertion
from syrupy.matchers import path_type

from test_base_operations import create_table, append_rows


SIMPLE_COLUMNS = [
    {'column_name': 'text', 'column_type': 'text'},
    {'column_name': 'number', 'column_type': 'number'},
    {'column_name': 'checkbox', 'column_type': 'checkbox'},
]


def test_updateRow(base: Base, snapshot_json: SnapshotAssertion):
    table_name = 'test_updateRow'
    create_table(base, table_name, SIMPLE_COLUMNS)
    row_ids = append_rows(base, table_name, [
        {'text': 'original', 'number': 1, 'checkbox': False},
    ])

    path_parameters = {'base_uuid': base.uuid}
    body = {
        'table_name': table_name,
        'updates': [
            {
                'row_id': row_ids[0],
                'row': {'text': 'updated', 'number': 99, 'checkbox': True},
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
    assert data['text'] == 'updated'
    assert data['number'] == 99
    assert data['checkbox'] is True

    matcher = path_type({
        '_id': (str,),
        '_ctime': (str,),
        '_mtime': (str,),
        '_creator': (str,),
        '_last_modifier': (str,),
    })

    assert snapshot_json(matcher=matcher) == data


def test_updateRow_multiple(base: Base):
    table_name = 'test_updateRow_multiple'
    create_table(base, table_name, SIMPLE_COLUMNS)
    row_ids = append_rows(base, table_name, [
        {'text': 'row-1', 'number': 1},
        {'text': 'row-2', 'number': 2},
        {'text': 'row-3', 'number': 3},
    ])

    path_parameters = {'base_uuid': base.uuid}
    body = {
        'table_name': table_name,
        'updates': [
            {'row_id': row_ids[0], 'row': {'text': 'updated-1', 'number': 10}},
            {'row_id': row_ids[1], 'row': {'text': 'updated-2', 'number': 20}},
            {'row_id': row_ids[2], 'row': {'text': 'updated-3', 'number': 30}},
        ],
    }
    headers = {'Authorization': f'Bearer {base.token}'}
    case: Case = base_operations_schema.get_operation_by_id('updateRow') \
        .make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200


def test_deleteRow(base: Base):
    table_name = 'test_deleteRow'
    create_table(base, table_name, SIMPLE_COLUMNS)
    row_ids = append_rows(base, table_name, [
        {'text': 'to-delete-1'},
        {'text': 'to-delete-2'},
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
    create_table(base, table_name, SIMPLE_COLUMNS)
    row_ids = append_rows(base, table_name, [
        {'text': 'lock-me'},
    ])

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
