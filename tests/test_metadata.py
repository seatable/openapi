from conftest import Base, base_operations_schema
from schemathesis import Case

from test_base_operations import create_table


def test_getMetadata(base: Base):
    create_table(base, 'test_metadata', [
        {'column_name': 'text', 'column_type': 'text'},
        {'column_name': 'number', 'column_type': 'number'},
    ])

    path_parameters = {'base_uuid': base.uuid}
    headers = {'Authorization': f'Bearer {base.token}'}

    case: Case = base_operations_schema.get_operation_by_id('getMetadata') \
        .make_case(path_parameters=path_parameters, headers=headers)
    response = case.call()

    assert response.status_code == 200

    data = response.json()
    assert 'metadata' in data
    assert 'tables' in data['metadata']
    table_names = [t['name'] for t in data['metadata']['tables']]
    assert 'test_metadata' in table_names

    # Verify table has our columns
    table = next(t for t in data['metadata']['tables'] if t['name'] == 'test_metadata')
    column_names = [c['name'] for c in table['columns']]
    assert 'text' in column_names
    assert 'number' in column_names


def test_listCollaborators(base: Base):
    path_parameters = {'base_uuid': base.uuid}
    headers = {'Authorization': f'Bearer {base.token}'}

    case: Case = base_operations_schema.get_operation_by_id('listCollaborators') \
        .make_case(path_parameters=path_parameters, headers=headers)
    response = case.call()

    assert response.status_code == 200

    data = response.json()
    assert 'user_list' in data
    assert isinstance(data['user_list'], list)
    assert len(data['user_list']) >= 1

    user = data['user_list'][0]
    assert 'email' in user
    assert 'name' in user
    assert 'contact_email' in user
