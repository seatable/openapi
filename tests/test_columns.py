import pytest
from conftest import Base, base_operations_schema, USES_GO_DTABLE_SERVER
from schemathesis import Case
from syrupy.assertion import SnapshotAssertion
from syrupy.matchers import path_type

from test_base_operations import create_table, COLUMNS


def test_listColumns(base: Base, snapshot_json: SnapshotAssertion):
    table_name = 'test_listColumns'
    create_table(base, table_name, COLUMNS)

    path_parameters = {'base_uuid': base.uuid}
    query = {'table_name': table_name}
    headers = {'Authorization': f'Bearer {base.token}'}

    case: Case = base_operations_schema.find_operation_by_id('listColumns') \
        .Case(path_parameters=path_parameters, query=query, headers=headers)
    response = case.call()

    assert response.status_code == 200

    data = response.json()
    assert 'columns' in data
    column_names = [c['name'] for c in data['columns']]
    # Verify a representative set of column types is present
    for col in COLUMNS:
        assert col['column_name'] in column_names

    matcher = path_type({
        r"columns\..*\.key": (str,),
    }, regex=True)

    assert snapshot_json(matcher=matcher) == data


# Column definitions for insertColumn and appendColumns tests — covers complex types
# that are not tested via createTable (which uses COLUMNS from test_base_operations).
INSERT_COLUMNS = [
    {
        'column_name': 'number-yuan',
        'column_type': 'number',
        'column_data': {
            'format': 'yuan',
            'decimal': 'dot',
            'thousands': 'comma',
        },
    },
    {
        'column_name': 'date-iso',
        'column_type': 'date',
        'column_data': {
            'format': 'YYYY-MM-DD',
        },
    },
    {
        'column_name': 'duration-h-mm-ss',
        'column_type': 'duration',
        'column_data': {
            'format': 'duration',
            'duration_format': 'h:mm:ss',
        },
    },
    {
        'column_name': 'single-select',
        'column_type': 'single-select',
        'column_data': {
            'options': [
                {'id': '0000', 'name': 'alpha', 'color': '#9860E5', 'textColor': '#000000'},
                {'id': 'ef3s', 'name': 'beta', 'color': '#89D2EA', 'textColor': '#000000'},
            ],
        },
    },
    {
        'column_name': 'checkbox',
        'column_type': 'checkbox',
    },
    {
        'column_name': 'rate',
        'column_type': 'rate',
        'column_data': {'rate_max_number': 5},
    },
    {
        'column_name': 'formula-sum',
        'column_type': 'formula',
        'column_data': {
            'formula': '1 + 2',
        },
    },
    {
        'column_name': 'geolocation',
        'column_type': 'geolocation',
        'column_data': {
            'geo_format': 'lng_lat',
        },
    },
    {
        'column_name': 'email',
        'column_type': 'email',
    },
    {
        'column_name': 'url',
        'column_type': 'url',
    },
    {
        'column_name': 'auto-number',
        'column_type': 'auto-number',
        'column_data': {
            'format': '0000',
            'digits': 4,
        },
    },
]


@pytest.mark.parametrize('column', INSERT_COLUMNS, ids=lambda c: c['column_name'])
def test_insertColumn(base: Base, snapshot_json: SnapshotAssertion, column: dict):
    table_name = f'test_insertColumn_{column["column_name"]}'
    create_table(base, table_name, [])

    path_parameters = {'base_uuid': base.uuid}
    headers = {'Authorization': f'Bearer {base.token}'}
    body = {
        'table_name': table_name,
        'column_name': column['column_name'],
        'column_type': column['column_type'],
    }
    if 'column_data' in column:
        body['column_data'] = column['column_data']

    case: Case = base_operations_schema.find_operation_by_id('insertColumn') \
        .Case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200

    data = response.json()
    assert data['name'] == column['column_name']
    assert data['type'] == column['column_type']

    matcher = path_type({
        'key': (str,),
    })

    assert snapshot_json(matcher=matcher) == data


# appendColumns (batch) does not support formula and auto-number column types
APPEND_COLUMNS = [c for c in INSERT_COLUMNS if c['column_type'] not in ('formula', 'auto-number')]


def test_appendColumns(base: Base, snapshot_json: SnapshotAssertion):
    table_name = 'test_appendColumns'
    create_table(base, table_name, [])

    path_parameters = {'base_uuid': base.uuid}
    headers = {'Authorization': f'Bearer {base.token}'}
    body = {
        'table_name': table_name,
        'columns': APPEND_COLUMNS,
    }

    case: Case = base_operations_schema.find_operation_by_id('appendColumns') \
        .Case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200

    data = response.json()
    assert 'columns' in data
    new_names = [c['name'] for c in data['columns']]
    for col in APPEND_COLUMNS:
        assert col['column_name'] in new_names

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

    case: Case = base_operations_schema.find_operation_by_id('updateColumn') \
        .Case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200

    # Verify rename
    query = {'table_name': table_name}
    case: Case = base_operations_schema.find_operation_by_id('listColumns') \
        .Case(path_parameters=path_parameters, query=query, headers=headers)
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

    case: Case = base_operations_schema.find_operation_by_id('updateColumn') \
        .Case(path_parameters=path_parameters, body=body, headers=headers)
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
    case: Case = base_operations_schema.find_operation_by_id('updateColumn') \
        .Case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200

    # Unfreeze
    body['frozen'] = False
    case: Case = base_operations_schema.find_operation_by_id('updateColumn') \
        .Case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200


@pytest.mark.xfail(reason="appendColumns does not work with link-formula columns")
def test_appendColumns_link_formula(base: Base):
    table_name_1 = 'test_appendColumns_lf_1'
    table_name_2 = 'test_appendColumns_lf_2'
    create_table(base, table_name_1, [{'column_name': 'number', 'column_type': 'number'}])
    create_table(base, table_name_2, [{'column_name': 'number', 'column_type': 'number'}])

    path_parameters = {'base_uuid': base.uuid}
    headers = {'Authorization': f'Bearer {base.token}'}

    # Insert a link column on table_2 pointing to table_1
    body = {
        'table_name': table_name_2,
        'column_name': 'link',
        'column_type': 'link',
        'column_data': {
            'table': table_name_2,
            'other_table': table_name_1,
        },
    }
    case: Case = base_operations_schema.find_operation_by_id('insertColumn') \
        .Case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()
    assert response.status_code == 200

    # Try to append link-formula columns via appendColumns
    body = {
        'table_name': table_name_2,
        'columns': [
            {
                'column_name': 'link-formula-lookup',
                'column_type': 'link-formula',
                'column_data': {
                    'formula': 'lookup',
                    'link_column': 'link',
                    'level1_linked_column': 'number',
                },
            },
            {
                'column_name': 'link-formula-countlinks',
                'column_type': 'link-formula',
                'column_data': {
                    'formula': 'count_links',
                    'link_column': 'link',
                },
            },
        ],
    }
    case: Case = base_operations_schema.find_operation_by_id('appendColumns') \
        .Case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200

    data = response.json()
    assert 'columns' in data
    column_names = [c['name'] for c in data['columns']]
    assert 'link-formula-lookup' in column_names
    assert 'link-formula-countlinks' in column_names


@pytest.mark.xfail(reason="Server rejects DD/MM/YYYY HH:mm format as not meeting specifications")
def test_insertColumn_date_european_hours_minutes(base: Base):
    table_name = 'test_insertColumn_date_european_hm'
    create_table(base, table_name, [])

    path_parameters = {'base_uuid': base.uuid}
    headers = {'Authorization': f'Bearer {base.token}'}
    body = {
        'table_name': table_name,
        'column_name': 'date-european-hours-minutes',
        'column_type': 'date',
        'column_data': {
            'format': 'DD/MM/YYYY HH:mm',
        },
    }

    case: Case = base_operations_schema.find_operation_by_id('insertColumn') \
        .Case(path_parameters=path_parameters, body=body, headers=headers)
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

    case: Case = base_operations_schema.find_operation_by_id('deleteColumn') \
        .Case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200

    # Verify column is gone
    query = {'table_name': table_name}
    case: Case = base_operations_schema.find_operation_by_id('listColumns') \
        .Case(path_parameters=path_parameters, query=query, headers=headers)
    response = case.call()

    assert response.status_code == 200
    column_names = [c['name'] for c in response.json()['columns']]
    assert 'keep' in column_names
    assert 'delete-me' not in column_names


def test_insertColumn_duplicate_name_returns_400(base: Base):
    table_name = 'test_insertColumn_duplicate'
    create_table(base, table_name, [{'column_name': 'existing', 'column_type': 'text'}])

    path_parameters = {'base_uuid': base.uuid}
    headers = {'Authorization': f'Bearer {base.token}'}
    body = {'table_name': table_name, 'column_name': 'existing', 'column_type': 'text'}

    # Inserting a column whose name collides with an existing column is rejected
    case: Case = base_operations_schema.find_operation_by_id('insertColumn') \
        .Case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 400
    # application/json is also enforced by the conformance hook against the documented 400
    assert response.headers['content-type'][0].startswith('application/json')


@pytest.mark.xfail(
    not USES_GO_DTABLE_SERVER,
    reason="insertColumn returns the plain-text body 'Column ColA exists.' with an "
           "application/json content-type on a duplicate-column 400 (not valid JSON)",
)
def test_insertColumn_duplicate_name_returns_json(base: Base):
    table_name = 'test_insertColumn_duplicate_json'
    create_table(base, table_name, [{'column_name': 'existing', 'column_type': 'text'}])

    path_parameters = {'base_uuid': base.uuid}
    headers = {'Authorization': f'Bearer {base.token}'}
    body = {'table_name': table_name, 'column_name': 'existing', 'column_type': 'text'}

    case: Case = base_operations_schema.find_operation_by_id('insertColumn') \
        .Case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 400
    # The body should be valid JSON; currently raises JSONDecodeError (plain text)
    response.json()


def test_updateColumn_rename_collision_returns_400(base: Base):
    table_name = 'test_updateColumn_collision'
    create_table(base, table_name, [
        {'column_name': 'col-a', 'column_type': 'text'},
        {'column_name': 'col-b', 'column_type': 'text'},
    ])

    path_parameters = {'base_uuid': base.uuid}
    headers = {'Authorization': f'Bearer {base.token}'}
    body = {
        'op_type': 'rename_column',
        'table_name': table_name,
        'column': 'col-b',
        'new_column_name': 'col-a',
    }

    # Renaming a column to collide with an existing column name is rejected
    case: Case = base_operations_schema.find_operation_by_id('updateColumn') \
        .Case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 400
    assert response.headers['content-type'][0].startswith('application/json')
