import pytest
from conftest import Base, base_operations_schema
from schemathesis import Case
from syrupy.assertion import SnapshotAssertion
from syrupy.matchers import path_type

from test_base_operations import create_table


def test_listColumns(base: Base, snapshot_json: SnapshotAssertion):
    table_name = 'test_listColumns'
    columns = [
        {'column_name': 'text', 'column_type': 'text'},
        {'column_name': 'number', 'column_type': 'number'},
        {'column_name': 'checkbox', 'column_type': 'checkbox'},
    ]
    create_table(base, table_name, columns)

    path_parameters = {'base_uuid': base.uuid}
    query = {'table_name': table_name}
    headers = {'Authorization': f'Bearer {base.token}'}

    case: Case = base_operations_schema.get_operation_by_id('listColumns') \
        .make_case(path_parameters=path_parameters, query=query, headers=headers)
    response = case.call()

    assert response.status_code == 200

    data = response.json()
    assert 'columns' in data
    column_names = [c['name'] for c in data['columns']]
    assert 'text' in column_names
    assert 'number' in column_names
    assert 'checkbox' in column_names

    matcher = path_type({
        r"columns\..*\.key": (str,),
    }, regex=True)

    assert snapshot_json(matcher=matcher) == data


def test_insertColumn(base: Base, snapshot_json: SnapshotAssertion):
    table_name = 'test_insertColumn'
    create_table(base, table_name, [])

    path_parameters = {'base_uuid': base.uuid}
    headers = {'Authorization': f'Bearer {base.token}'}
    body = {
        'table_name': table_name,
        'column_name': 'rating',
        'column_type': 'rate',
        'column_data': {'rate_max_number': 5},
    }

    case: Case = base_operations_schema.get_operation_by_id('insertColumn') \
        .make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200

    data = response.json()
    assert data['name'] == 'rating'
    assert data['type'] == 'rate'

    matcher = path_type({
        'key': (str,),
    })

    assert snapshot_json(matcher=matcher) == data


def test_appendColumns(base: Base, snapshot_json: SnapshotAssertion):
    table_name = 'test_appendColumns'
    create_table(base, table_name, [])

    path_parameters = {'base_uuid': base.uuid}
    headers = {'Authorization': f'Bearer {base.token}'}
    body = {
        'table_name': table_name,
        'columns': [
            {'column_name': 'email', 'column_type': 'email'},
            {'column_name': 'url', 'column_type': 'url'},
            {'column_name': 'rate', 'column_type': 'rate', 'column_data': {'rate_max_number': 10}},
        ],
    }

    case: Case = base_operations_schema.get_operation_by_id('appendColumns') \
        .make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200

    data = response.json()
    assert 'columns' in data
    new_names = [c['name'] for c in data['columns']]
    assert 'email' in new_names
    assert 'url' in new_names
    assert 'rate' in new_names

    matcher = path_type({
        r"columns\..*\.key": (str,),
    }, regex=True)

    assert snapshot_json(matcher=matcher) == data


def test_updateColumn_rename(base: Base):
    table_name = 'test_updateColumn_rename'
    columns = [{'column_name': 'old-name', 'column_type': 'text'}]
    create_table(base, table_name, columns)

    path_parameters = {'base_uuid': base.uuid}
    headers = {'Authorization': f'Bearer {base.token}'}
    body = {
        'op_type': 'rename_column',
        'table_name': table_name,
        'column': 'old-name',
        'new_column_name': 'new-name',
    }

    case: Case = base_operations_schema.get_operation_by_id('updateColumn') \
        .make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200

    # Verify rename
    query = {'table_name': table_name}
    case: Case = base_operations_schema.get_operation_by_id('listColumns') \
        .make_case(path_parameters=path_parameters, query=query, headers=headers)
    response = case.call()

    assert response.status_code == 200
    column_names = [c['name'] for c in response.json()['columns']]
    assert 'new-name' in column_names
    assert 'old-name' not in column_names


def test_updateColumn_resize(base: Base):
    table_name = 'test_updateColumn_resize'
    columns = [{'column_name': 'text-col', 'column_type': 'text'}]
    create_table(base, table_name, columns)

    path_parameters = {'base_uuid': base.uuid}
    headers = {'Authorization': f'Bearer {base.token}'}
    body = {
        'op_type': 'resize_column',
        'table_name': table_name,
        'column': 'text-col',
        'new_column_width': 400,
    }

    case: Case = base_operations_schema.get_operation_by_id('updateColumn') \
        .make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200


def test_updateColumn_freeze(base: Base):
    table_name = 'test_updateColumn_freeze'
    columns = [{'column_name': 'freeze-me', 'column_type': 'text'}]
    create_table(base, table_name, columns)

    path_parameters = {'base_uuid': base.uuid}
    headers = {'Authorization': f'Bearer {base.token}'}

    # Freeze
    body = {
        'op_type': 'freeze_column',
        'table_name': table_name,
        'column': 'freeze-me',
        'frozen': True,
    }
    case: Case = base_operations_schema.get_operation_by_id('updateColumn') \
        .make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200

    # Unfreeze
    body['frozen'] = False
    case: Case = base_operations_schema.get_operation_by_id('updateColumn') \
        .make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200


def test_deleteColumn(base: Base):
    table_name = 'test_deleteColumn'
    columns = [
        {'column_name': 'keep', 'column_type': 'text'},
        {'column_name': 'delete-me', 'column_type': 'text'},
    ]
    create_table(base, table_name, columns)

    path_parameters = {'base_uuid': base.uuid}
    headers = {'Authorization': f'Bearer {base.token}'}
    body = {
        'table_name': table_name,
        'column': 'delete-me',
    }

    case: Case = base_operations_schema.get_operation_by_id('deleteColumn') \
        .make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200

    # Verify column is gone
    query = {'table_name': table_name}
    case: Case = base_operations_schema.get_operation_by_id('listColumns') \
        .make_case(path_parameters=path_parameters, query=query, headers=headers)
    response = case.call()

    assert response.status_code == 200
    column_names = [c['name'] for c in response.json()['columns']]
    assert 'keep' in column_names
    assert 'delete-me' not in column_names
