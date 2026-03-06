from conftest import Base, base_operations_schema
from schemathesis import Case

from test_base_operations import create_table, append_rows


def _setup_linked_tables(base: Base, suffix: str = ''):
    """Create two tables with a link column and some linked rows. Returns table names, link_id, and row IDs."""
    table1 = f'test_links_source{suffix}'
    table2 = f'test_links_target{suffix}'

    create_table(base, table1, [{'column_name': 'name', 'column_type': 'text'}])
    create_table(base, table2, [{'column_name': 'name', 'column_type': 'text'}])

    t1_row_ids = append_rows(base, table1, [
        {'name': 'Alice'},
        {'name': 'Bob'},
    ])
    t2_row_ids = append_rows(base, table2, [
        {'name': 'Project A'},
        {'name': 'Project B'},
    ])

    # Insert link column on table1
    path_parameters = {'base_uuid': base.uuid}
    headers = {'Authorization': f'Bearer {base.token}'}
    body = {
        'table_name': table1,
        'column_name': 'projects',
        'column_type': 'link',
        'column_data': {
            'table': table1,
            'other_table': table2,
        },
    }
    case: Case = base_operations_schema.get_operation_by_id('insertColumn') \
        .make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()
    assert response.status_code == 200
    link_id = response.json()['data']['link_id']

    # Get table IDs from metadata
    case: Case = base_operations_schema.get_operation_by_id('getMetadata') \
        .make_case(path_parameters=path_parameters, headers=headers)
    response = case.call()
    tables = response.json()['metadata']['tables']
    t1_id = next(t['_id'] for t in tables if t['name'] == table1)
    t2_id = next(t['_id'] for t in tables if t['name'] == table2)

    # Create links: Alice -> Project A, Project B; Bob -> Project A
    body = {
        'table_id': t1_id,
        'other_table_id': t2_id,
        'link_id': link_id,
        'other_rows_ids_map': {
            t1_row_ids[0]: t2_row_ids,           # Alice -> both projects
            t1_row_ids[1]: [t2_row_ids[0]],      # Bob -> Project A
        },
    }
    case: Case = base_operations_schema.get_operation_by_id('createRowLink') \
        .make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()
    assert response.status_code == 200

    return table1, table2, link_id, t1_id, t2_id, t1_row_ids, t2_row_ids


def test_listRowLinks(base: Base):
    table1, table2, link_id, t1_id, t2_id, t1_row_ids, t2_row_ids = _setup_linked_tables(base, '_list')

    path_parameters = {'base_uuid': base.uuid}
    headers = {'Authorization': f'Bearer {base.token}'}
    body = {
        'table_name': table1,
        'link_column_name': 'projects',
        'rows': [
            {'row_id': t1_row_ids[0]},
            {'row_id': t1_row_ids[1]},
        ],
    }

    case: Case = base_operations_schema.get_operation_by_id('listRowLinks') \
        .make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200

    data = response.json()
    # Alice should have 2 links
    assert len(data[t1_row_ids[0]]) == 2
    # Bob should have 1 link
    assert len(data[t1_row_ids[1]]) == 1


def test_updateRowLink(base: Base):
    table1, table2, link_id, t1_id, t2_id, t1_row_ids, t2_row_ids = _setup_linked_tables(base, '_update')

    path_parameters = {'base_uuid': base.uuid}
    headers = {'Authorization': f'Bearer {base.token}'}

    # Update: Bob now links to Project B only (replaces Project A)
    body = {
        'table_id': t1_id,
        'other_table_id': t2_id,
        'link_id': link_id,
        'other_rows_ids_map': {
            t1_row_ids[1]: [t2_row_ids[1]],  # Bob -> Project B only
        },
    }

    case: Case = base_operations_schema.get_operation_by_id('updateRowLink') \
        .make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200
    assert response.json()['success'] is True

    # Verify via listRowLinks
    body = {
        'table_name': table1,
        'link_column_name': 'projects',
        'rows': [{'row_id': t1_row_ids[1]}],
    }
    case: Case = base_operations_schema.get_operation_by_id('listRowLinks') \
        .make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200
    bob_links = response.json()[t1_row_ids[1]]
    assert len(bob_links) == 1
    assert bob_links[0]['row_id'] == t2_row_ids[1]


def test_deleteRowLink(base: Base):
    table1, table2, link_id, t1_id, t2_id, t1_row_ids, t2_row_ids = _setup_linked_tables(base, '_delete')

    path_parameters = {'base_uuid': base.uuid}
    headers = {'Authorization': f'Bearer {base.token}'}

    # Delete Alice's link to Project B
    body = {
        'table_id': t1_id,
        'other_table_id': t2_id,
        'link_id': link_id,
        'other_rows_ids_map': {
            t1_row_ids[0]: [t2_row_ids[1]],  # Alice -x-> Project B
        },
    }

    case: Case = base_operations_schema.get_operation_by_id('deleteRowLink') \
        .make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200

    # Verify Alice now has only 1 link
    body = {
        'table_name': table1,
        'link_column_name': 'projects',
        'rows': [{'row_id': t1_row_ids[0]}],
    }
    case: Case = base_operations_schema.get_operation_by_id('listRowLinks') \
        .make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200
    alice_links = response.json()[t1_row_ids[0]]
    assert len(alice_links) == 1
    assert alice_links[0]['row_id'] == t2_row_ids[0]
