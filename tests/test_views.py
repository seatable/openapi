import pytest
from conftest import Base, base_operations_schema
from schemathesis import Case
from syrupy.assertion import SnapshotAssertion
from syrupy.matchers import path_type

from test_base_operations import create_table, append_rows


SIMPLE_COLUMNS = [
    {'column_name': 'text', 'column_type': 'text'},
    {'column_name': 'number', 'column_type': 'number'},
]


def test_listViews(base: Base, snapshot_json: SnapshotAssertion):
    table_name = 'test_listViews'
    create_table(base, table_name, SIMPLE_COLUMNS)

    path_parameters = {'base_uuid': base.uuid}
    query = {'table_name': table_name}
    headers = {'Authorization': f'Bearer {base.token}'}

    case: Case = base_operations_schema.get_operation_by_id('listViews') \
        .make_case(path_parameters=path_parameters, query=query, headers=headers)
    response = case.call()

    assert response.status_code == 200

    data = response.json()
    assert 'views' in data
    assert len(data['views']) >= 1

    # Every new table has a "Default View"
    default_view = data['views'][0]
    assert default_view['name'] == 'Default View'

    matcher = path_type({
        r"views\..*\._id": (str,),
    }, regex=True)

    assert snapshot_json(matcher=matcher) == data


def test_createView(base: Base, snapshot_json: SnapshotAssertion):
    table_name = 'test_createView'
    create_table(base, table_name, SIMPLE_COLUMNS)

    path_parameters = {'base_uuid': base.uuid}
    query = {'table_name': table_name}
    headers = {'Authorization': f'Bearer {base.token}'}
    body = {'name': 'My Custom View', 'type': 'table'}

    case: Case = base_operations_schema.get_operation_by_id('createView') \
        .make_case(path_parameters=path_parameters, query=query, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200

    data = response.json()
    assert data['name'] == 'My Custom View'

    matcher = path_type({
        '_id': (str,),
    })

    assert snapshot_json(matcher=matcher) == data


def test_getView(base: Base, snapshot_json: SnapshotAssertion):
    table_name = 'test_getView'
    create_table(base, table_name, SIMPLE_COLUMNS)

    path_parameters = {'base_uuid': base.uuid, 'view_name': 'Default View'}
    query = {'table_name': table_name}
    headers = {'Authorization': f'Bearer {base.token}'}

    case: Case = base_operations_schema.get_operation_by_id('getView') \
        .make_case(path_parameters=path_parameters, query=query, headers=headers)
    response = case.call()

    assert response.status_code == 200

    data = response.json()
    assert data['name'] == 'Default View'

    matcher = path_type({
        '_id': (str,),
    })

    assert snapshot_json(matcher=matcher) == data


def test_updateView(base: Base):
    table_name = 'test_updateView'
    create_table(base, table_name, SIMPLE_COLUMNS)
    append_rows(base, table_name, [{'text': 'a', 'number': 1}, {'text': 'b', 'number': 2}])

    headers = {'Authorization': f'Bearer {base.token}'}
    query = {'table_name': table_name}

    # Create a view first
    body = {'name': 'View To Update', 'type': 'table'}
    case: Case = base_operations_schema.get_operation_by_id('createView') \
        .make_case(path_parameters={'base_uuid': base.uuid}, query=query, body=body, headers=headers)
    response = case.call()
    assert response.status_code == 200

    # Update the view: rename and add a sort
    path_parameters = {'base_uuid': base.uuid, 'view_name': 'View To Update'}
    body = {
        'name': 'Renamed View',
        'sorts': [{'column_name': 'number', 'sort_type': 'down'}],
    }
    case: Case = base_operations_schema.get_operation_by_id('updateView') \
        .make_case(path_parameters=path_parameters, query=query, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200

    data = response.json()
    assert data['name'] == 'Renamed View'


def test_deleteView(base: Base):
    table_name = 'test_deleteView'
    create_table(base, table_name, SIMPLE_COLUMNS)

    headers = {'Authorization': f'Bearer {base.token}'}
    query = {'table_name': table_name}

    # Create a view to delete
    body = {'name': 'View To Delete', 'type': 'table'}
    case: Case = base_operations_schema.get_operation_by_id('createView') \
        .make_case(path_parameters={'base_uuid': base.uuid}, query=query, body=body, headers=headers)
    response = case.call()
    assert response.status_code == 200

    # Delete it
    path_parameters = {'base_uuid': base.uuid, 'view_name': 'View To Delete'}
    case: Case = base_operations_schema.get_operation_by_id('deleteView') \
        .make_case(path_parameters=path_parameters, query=query, headers=headers)
    response = case.call()

    assert response.status_code == 200

    # Verify it's gone
    path_parameters = {'base_uuid': base.uuid}
    case: Case = base_operations_schema.get_operation_by_id('listViews') \
        .make_case(path_parameters=path_parameters, query=query, headers=headers)
    response = case.call()

    assert response.status_code == 200
    view_names = [v['name'] for v in response.json()['views']]
    assert 'View To Delete' not in view_names
