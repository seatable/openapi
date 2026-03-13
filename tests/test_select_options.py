from conftest import Base, base_operations_schema
from schemathesis import Case

from test_base_operations import create_table


def test_addSelectOption(base: Base):
    table_name = 'test_addSelectOption'
    columns = [{
        'column_name': 'status',
        'column_type': 'single-select',
    }]
    create_table(base, table_name, columns)

    path_parameters = {'base_uuid': base.uuid}
    headers = {'Authorization': f'Bearer {base.token}'}
    body = {
        'table_name': table_name,
        'column': 'status',
        'options': [
            {'name': 'open', 'color': '#FF8000', 'textColor': '#FFFFFF'},
            {'name': 'closed', 'color': '#59CB74', 'textColor': '#FFFFFF'},
            {'name': 'pending', 'color': '#9860E5', 'textColor': '#FFFFFF'},
        ],
    }

    case: Case = base_operations_schema.find_operation_by_id('addSelectOption') \
        .Case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200
    assert response.json()['success'] is True

    # Verify options exist via listColumns
    query = {'table_name': table_name}
    case: Case = base_operations_schema.find_operation_by_id('listColumns') \
        .Case(path_parameters=path_parameters, query=query, headers=headers)
    response = case.call()

    assert response.status_code == 200
    status_col = next(c for c in response.json()['columns'] if c['name'] == 'status')
    option_names = [o['name'] for o in status_col['data']['options']]
    assert 'open' in option_names
    assert 'closed' in option_names
    assert 'pending' in option_names


def test_updateSelectOption(base: Base):
    table_name = 'test_updateSelectOption'
    columns = [{
        'column_name': 'priority',
        'column_type': 'single-select',
        'column_data': {
            'options': [
                {'id': 'aaa1', 'name': 'low', 'color': '#59CB74', 'textColor': '#000000'},
                {'id': 'bbb2', 'name': 'high', 'color': '#FF8000', 'textColor': '#000000'},
            ],
        },
    }]
    create_table(base, table_name, columns)

    path_parameters = {'base_uuid': base.uuid}
    headers = {'Authorization': f'Bearer {base.token}'}
    body = {
        'table_name': table_name,
        'column': 'priority',
        'options': [
            {'id': 'aaa1', 'name': 'low-renamed', 'color': '#4ECCCB'},
        ],
        'return_options': True,
    }

    case: Case = base_operations_schema.find_operation_by_id('updateSelectOption') \
        .Case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200

    # Verify rename via listColumns
    query = {'table_name': table_name}
    case: Case = base_operations_schema.find_operation_by_id('listColumns') \
        .Case(path_parameters=path_parameters, query=query, headers=headers)
    response = case.call()

    assert response.status_code == 200
    col = next(c for c in response.json()['columns'] if c['name'] == 'priority')
    option_names = [o['name'] for o in col['data']['options']]
    assert 'low-renamed' in option_names
    assert 'low' not in option_names


def test_deleteSelectOption(base: Base):
    table_name = 'test_deleteSelectOption'
    create_table(base, table_name, [{'column_name': 'name', 'column_type': 'text'}])

    path_parameters = {'base_uuid': base.uuid}
    headers = {'Authorization': f'Bearer {base.token}'}

    # Add multiple-select column via insertColumn (createTable doesn't support multiple-select)
    body = {
        'table_name': table_name,
        'column_name': 'color',
        'column_type': 'multiple-select',
    }
    case: Case = base_operations_schema.find_operation_by_id('insertColumn') \
        .Case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()
    assert response.status_code == 200

    # Add options
    body = {
        'table_name': table_name,
        'column': 'color',
        'options': [
            {'name': 'red', 'color': '#FF0000', 'textColor': '#FFFFFF'},
            {'name': 'green', 'color': '#00FF00', 'textColor': '#FFFFFF'},
            {'name': 'blue', 'color': '#0000FF', 'textColor': '#FFFFFF'},
        ],
    }
    case: Case = base_operations_schema.find_operation_by_id('addSelectOption') \
        .Case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()
    assert response.status_code == 200

    body = {
        'table_name': table_name,
        'column': 'color',
        'option_names': ['red', 'blue'],
    }

    case: Case = base_operations_schema.find_operation_by_id('deleteSelectOption') \
        .Case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200
    assert response.json()['success'] is True

    # Verify only green remains
    query = {'table_name': table_name}
    case: Case = base_operations_schema.find_operation_by_id('listColumns') \
        .Case(path_parameters=path_parameters, query=query, headers=headers)
    response = case.call()

    assert response.status_code == 200
    col = next(c for c in response.json()['columns'] if c['name'] == 'color')
    option_names = [o['name'] for o in col['data']['options']]
    assert option_names == ['green']
