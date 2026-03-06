import pytest
import requests
import schemathesis
from conftest import Base, BASE_URL, Secret, user_account_operations, base_operations_schema
from schemathesis import Case
from syrupy.assertion import SnapshotAssertion
from syrupy.matchers import path_type

file_operations = schemathesis.from_path('../file_operations.yaml', base_url=BASE_URL, validate_schema=True)

COLUMNS = [
    {
        'column_name': 'text',
        'column_type': 'text',
    },
    {
        'column_name': 'long-text',
        'column_type': 'long-text',
    },
    {
        'column_name': 'number',
        'column_type': 'number',
    },
    {
        'column_name': 'number-decimal-dot-thousands-comma',
        'column_type': 'number',
        'column_data': {
            'format': 'number',
            'decimal': 'dot',
            'thousands': 'comma',
        },
    },
    {
        'column_name': 'number-percent',
        'column_type': 'number',
        'column_data': {
            'format': 'percent',
            'decimal': 'comma',
            'thousands': 'no',
        },
    },
    {
        'column_name': 'number-euro',
        'column_type': 'number',
        'column_data': {
            'format': 'euro',
            'decimal': 'comma',
            'thousands': 'no',
        },
    },
    {
        'column_name': 'collaborator',
        'column_type': 'collaborator',
    },
    {
        'column_name': 'date-iso',
        'column_type': 'date',
        'column_data': {
            'format': 'YYYY-MM-DD'
        }
    },
    {
        'column_name': 'date-iso-hours-minutes',
        'column_type': 'date',
        'column_data': {
            'format': 'YYYY-MM-DD HH:mm'
        }
    },
    {
        'column_name': 'date-us',
        'column_type': 'date',
        'column_data': {
            'format': 'M/D/YYYY'
        }
    },
    {
        'column_name': 'date-us-hours-minutes',
        'column_type': 'date',
        'column_data': {
            'format': 'M/D/YYYY HH:mm'
        }
    },
        {
        'column_name': 'date-european',
        'column_type': 'date',
        'column_data': {
            'format': 'DD/MM/YYYY'
        }
    },
    # FIXME: Fix this
    # Also fails with insertColumn operation on api.seatable.com: {"error_type": "column_data_error", "error_message": "column_data: {\"format\":\"DD/MM/YYYY HH:mm\"} do not meet specifications."}
    #{
    #     'column_name': 'date-european-hours-minutes',
    #     'column_type': 'date',
    #     'column_data': {
    #         'format': 'DD/MM/YYYY HH:mm'
    #     }
    #},
    {
        'column_name': 'date-german',
        'column_type': 'date',
        'column_data': {
            'format': 'DD.MM.YYYY'
        }
    },
    {
        'column_name': 'date-german-hours-minutes',
        'column_type': 'date',
        'column_data': {
            'format': 'DD.MM.YYYY HH:mm'
        }
    },
    {
        'column_name': 'duration-hours-minutes',
        'column_type': 'duration',
        'column_data': {
            'format': 'duration',
            'duration_format': 'h:mm'
        }
    },
    {
        'column_name': 'duration-hours-minutes-seconds',
        'column_type': 'duration',
        'column_data': {
            'format': 'duration',
            'duration_format': 'h:mm:ss'
        }
    },
    {
        'column_name': 'single-select',
        'column_type': 'single-select',
        'column_data': {
            'options': [
               {'id': "0000", 'name': 'option-1', 'color': '#9860E5', 'textColor': '#000000'},
               {'id': "ef3s", 'name': 'option-2', 'color': '#89D2EA', 'textColor': '#000000'},
               {'id': "38d7", 'name': 'option-3', 'color': '#59CB74', 'textColor': '#000000'},
            ]
        }
    },
    {
        'column_name': 'multiple-select',
        'column_type': 'multiple-select',
        'column_data': {
            'options': [
               {'id': "0000", 'name': 'option-1', 'color': '#9860E5', 'textColor': '#000000'},
               {'id': "ef32", 'name': 'option-2', 'color': '#89D2EA', 'textColor': '#000000'},
               {'id': "yze2", 'name': 'option-3', 'color': '#59CB74', 'textColor': '#000000'},
            ]
        }
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
        'column_name': 'checkbox',
        'column_type': 'checkbox',
    },
    {
        'column_name': 'rate',
        'column_type': 'rate',
        'column_data': {
            'rate_max_number': 10,
        },
    },
    {
        'column_name': 'formula',
        'column_type': 'formula',
        'column_data': {
            'formula': "dateAdd({date-iso}, 1, 'year')"
        }
    },
    {
        'column_name': 'formula-integer-return-value',
        'column_type': 'formula',
        'column_data': {
            'formula': '1 + 2',
        },
    },
    {
        'column_name': 'formula-float-return-value',
        'column_type': 'formula',
        'column_data': {
            'formula': '1.3 + 2.6',
        },
    },
    {
        'column_name': 'formula-boolean-return-value',
        'column_type': 'formula',
        'column_data': {
            'formula': 'and(true(), false())',
        },
    },
    {
        'column_name': 'geolocation-country-region',
        'column_type': 'geolocation',
        'column_data': {
            'geo_format': 'country_region',
            'lang': 'en',
        },
    },
    {
        'column_name': 'geolocation-lat-lon',
        'column_type': 'geolocation',
        'column_data': {
            'geo_format': 'lng_lat',
        },
    },
    {
        'column_name': 'auto-number-integer',
        'column_type': 'auto-number',
        'column_data': {
            'format': '0000',
            'digits': 4,
        },
    },
    {
        'column_name': 'auto-number-string-prefix',
        'column_type': 'auto-number',
        'column_data': {
            'format': '0000',
            'digits': 4,
            'prefix_type': 'string',
            'prefix': 'row',
        },
    },
    {
        'column_name': 'auto-number-date-prefix',
        'column_type': 'auto-number',
        'column_data': {
            'format': '0000',
            'digits': 4,
            'prefix_type': 'date',
        },
    },
    {
        'column_name': 'digital-sign',
        'column_type': 'digital-sign',
    },
]

ROWS = [
    {
        'text': 'ABC',
        'long-text': '## Heading\n- Item 1\n- Item 2',
        'number': 499.99,
        'number-decimal-dot-thousands-comma': 1_000_000.123,
        'number-percent': 5,
        'number-euro': 5.23,
        'date-iso': '2030/06/20',
        'date-iso-hours-minutes': '2030/06/20 23:55',
        'date-us': '6/5/2024',
        'date-us-hours-minutes': '6/5/2024 23:55',
        'date-european': '05/06/2024',
        'date-european-hours-minutes': '05/06/2024 23:55',
        'date-german': '20.06.2030',
        'date-german-hours-minutes': '20.06.2030 23:55',
        # Duration values are in seconds
        'duration-hours-minutes': '5400',
        'duration-hours-minutes-seconds': '5430',
        'single-select': 'option-1',
        'multiple-select': ['option-1', 'option-2'],
        'email': 'example@seatable.io',
        'url': 'https://seatable.com',
        'checkbox': True,
        'rate': 7,
        'geolocation-country-region': {'country_region': 'Germany'},
        'geolocation-lat-lon': {'lng': 8.23, 'lat': 50.00},
        'digital-sign': {
            'username': 'some-user@auth.local',
            # Using an external image is a shortcut, but seems to work :)
            'sign_image_url': 'https://admin.seatable.com/assets/SeaTable256-256.png',
            'sign_time': '2024-06-05T13:28:56.090+00:00',
        },
    },
    {
        'text': 'D',
        'long-text': '## Heading\n- Item 1\n- Item 2',
        'number': 500,
        'number-percent': 5.12345,
        'number-euro': 10.2345,
        'date-iso': '2030/06/20',
        'date-iso-hours-minutes': '2030/06/20 23:55',
        'date-german': '20.06.2030',
        'date-german-hours-minutes': '20.06.2030 23:55',
        'single-select': 'option-2',
        'multiple-select': ['option-2', 'option-3'],
        'checkbox': False,
    },
    {
        'text': 'E',
        'long-text': '## Heading\n- Item 1\n- Item 2',
        'number': -10,
        'date-iso': '2030/06/20',
        'date-iso-hours-minutes': '2030/06/20 23:55',
        'date-german': '20.06.2030',
        'date-german-hours-minutes': '20.06.2030 23:55',
        'single-select': 'option-3',
        'multiple-select': ['option-1', 'option-2', 'option-3'],
        'checkbox': True,
    },
    {
        # Regression test for https://forum.seatable.com/t/python-modification-in-rows-data-since-4-4/4254
        'text': 'row-with-empty-values'
    }
]

def test_createBase(workspace_id: int, account_token: Secret, snapshot_json: SnapshotAssertion):
    body = {"workspace_id": workspace_id, "name": 'automated-testing-ahSh2sot'}
    case: Case = user_account_operations.get_operation_by_id('createBase').make_case(body=body)
    response = case.call(headers={"Authorization": f"Bearer {account_token.value}"})

    assert response.status_code == 201

    matcher = path_type({
        'table.created_at': (str,),
        'table.id': (int,),
        'table.updated_at': (str,),
        'table.uuid': (str,),
        'table.workspace_id': (int,),
    })

    assert snapshot_json(matcher=matcher) == response.json()

@pytest.mark.parametrize('operation_id', ['createTable'])
def test_createTable(base: Base, snapshot_json: SnapshotAssertion, operation_id: str):
    table_name = f'test_{operation_id}'

    path_parameters = {'base_uuid': base.uuid}
    body = {'table_name': table_name, 'columns': COLUMNS}
    headers = {'Authorization': f'Bearer {base.token}'}
    operation = base_operations_schema.get_operation_by_id('createTable')

    case: Case = operation.make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200

    matcher = path_type(
        {
            "_id": (str,),
            'columns': (list,)
        },
    )

    assert snapshot_json(matcher=matcher) == response.json()

@pytest.mark.parametrize('operation_id', ['appendRows'])
def test_appendRows(base: Base, snapshot_json: SnapshotAssertion, operation_id: str):
    table_name = f'test_{operation_id}'

    create_table(base, table_name, COLUMNS)

    path_parameters = {'base_uuid': base.uuid}
    body = {'table_name': table_name, 'rows': ROWS}
    headers = {'Authorization': f'Bearer {base.token}'}
    operation = base_operations_schema.get_operation_by_id(operation_id)

    case: Case = operation.make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200

    data = response.json()

    matcher = path_type(
        {
            'first_row': (dict,),
            r"row_ids\..*\._id": (str,),
        },
        regex=True
    )

    assert snapshot_json(matcher=matcher) == data

@pytest.mark.parametrize('operation_id', ['getRow'])
def test_getRow(base: Base, snapshot_json, operation_id: str):
    table_name = f'test_{operation_id}'

    create_table(base, table_name, COLUMNS)

    row = {
        'text': 'ABC',
        'long-text': '## Heading\n- Item 1\n- Item 2',
        'number': 499.99,
        'date-iso': '2030/06/20',
        'date-iso-hours-minutes': '2030/06/20 23:55',
        'date-german': '20.06.2030',
        'date-german-hours-minutes': '20.06.2030 23:55',
        'checkbox': True,
        'single-select': "option-1",
        'multiple-select': ["option-1", "option-2"],
        'rate': 2,
        'url': 'https://cloud.seatable.io',
        'email': 'demo@example.com'
    }
    row_id = append_rows(base, table_name, [row])[0]

    path_parameters = {'base_uuid': base.uuid, 'row_id': row_id}
    query = {'table_name': table_name, 'convert_keys': True}
    headers = {'Authorization': f'Bearer {base.token}'}
    operation = base_operations_schema.get_operation_by_id(operation_id)

    case: Case = operation.make_case(path_parameters=path_parameters, query=query, headers=headers)

    response = case.call()

    assert response.status_code == 200

    # Configure a custom matcher since some values will always change
    matcher = path_type({
        '_id': (str,),
        '_ctime': (str,),
        '_mtime': (str,),
        '_creator': (str,),
        '_last_modifier': (str,),
        'auto-number-date-prefix': (str,),
    })

    assert snapshot_json(matcher=matcher) == response.json()

@pytest.mark.parametrize('operation_id', ['listRows'])
def test_listRows(base: Base, snapshot_json, operation_id: str):
    table_name = f'test_{operation_id}'

    create_table(base, table_name, COLUMNS)
    append_rows(base, table_name, ROWS)

    path_parameters = {'base_uuid': base.uuid}
    query = {'table_name': table_name, 'convert_keys': True}
    headers = {'Authorization': f'Bearer {base.token}'}
    operation = base_operations_schema.get_operation_by_id(operation_id)

    case: Case = operation.make_case(path_parameters=path_parameters, query=query, headers=headers)

    response = case.call()

    assert response.status_code == 200

    # Create a custom matcher to validate that certain fields contain
    # strings without storing their actual value since they are not stable
    matcher = path_type(
        {
            r"rows\..*\.(_id|_ctime|_mtime|_creator|_last_modifier|auto-number-date-prefix)": (str,),
        },
        regex=True,
    )

    # Verify that response matches snapshot
    assert snapshot_json(matcher=matcher) == response.json()

@pytest.mark.parametrize('operation_id', ['listRows'])
def test_listRows_links(base: Base,  snapshot_json: SnapshotAssertion, operation_id: str):
    table_name_1 = f'test_{operation_id}_links-1'
    columns_1 = [
        {'column_name': 'number', 'column_type': 'number'},
    ]
    create_table(base, table_name_1, columns_1)

    table_name_2 = f'test_{operation_id}_links-2'
    columns_2 = [
        {'column_name': 'number', 'column_type': 'number'},
    ]
    create_table(base, table_name_2, columns_2)

    # Add rows
    table_1_rows = [
        {'number': 1.1},
        {'number': 1.1},
        {'number': 1.2},
        {'number': 1.3},
        {'number': 1.4},
        {'number': 1.4},
    ]
    table_1_row_ids = append_rows(base, table_name_1, table_1_rows)
    table_2_row_id = append_rows(base, table_name_2, [{'number': 2.1}])[0]

    # Insert link column
    path_parameters = {'base_uuid': base.uuid}
    body = {
        'table_name': table_name_2,
        'column_name': 'link',
        'column_type': 'link',
        'column_data': {
            'table': table_name_2,
            'other_table': table_name_1
        },
    }
    headers = {'Authorization': f'Bearer {base.token}'}
    case: Case = base_operations_schema.get_operation_by_id('insertColumn') \
        .make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    link_id = response.json()['data']['link_id']
    assert isinstance(link_id, str)

    # Create row link
    body = {
        'table_name': table_name_2,
        'other_table_name': table_name_1,
        'link_id': link_id,
        'other_rows_ids_map': {
            table_2_row_id: table_1_row_ids,
        },
    }
    case: Case = base_operations_schema.get_operation_by_id('createRowLink') \
        .make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200

    # TODO: Use appendColumns operation (does not work with link-formula columns?)
    link_formula_columns = [
        {
            'table_name': table_name_2,
            'column_name': 'link-formula-lookup',
            'column_type': 'link-formula',
            'column_data': {
                'formula': 'lookup',
                'link_column': 'link',
                'level1_linked_column': 'number',
            },
        },
        {
            'table_name': table_name_2,
            'column_name': 'link-formula-countlinks',
            'column_type': 'link-formula',
            'column_data': {
                'formula': 'count_links',
                'link_column': 'link',
            },
        },
        {
            'table_name': table_name_2,
            'column_name': 'link-formula-rollup-average',
            'column_type': 'link-formula',
            'column_data': {
                'formula': 'rollup',
                'link_column': 'link',
                'summary_column': 'number',
                'summary_method': 'average',
            },
        },
        {
            'table_name': table_name_2,
            'column_name': 'link-formula-rollup-max',
            'column_type': 'link-formula',
            'column_data': {
                'formula': 'rollup',
                'link_column': 'link',
                'summary_column': 'number',
                'summary_method': 'max',
            },
        },
        {
            'table_name': table_name_2,
            'column_name': 'link-formula-rollup-concatenate',
            'column_type': 'link-formula',
            'column_data': {
                'formula': 'rollup',
                'link_column': 'link',
                'summary_column': 'number',
                'summary_method': 'concatenate',
            },
        },
        {
            'table_name': table_name_2,
            'column_name': 'link-formula-findmax',
            'column_type': 'link-formula',
            'column_data': {
                'formula': 'findmax',
                'link_column': 'link',
                'searched_column': 'number',
                'comparison_column': 'number',
            },
        },
        {
            'table_name': table_name_2,
            'column_name': 'link-formula-findmin',
            'column_type': 'link-formula',
            'column_data': {
                'formula': 'findmin',
                'link_column': 'link',
                'searched_column': 'number',
                'comparison_column': 'number',
            },
        },
    ]

    # Insert link-formula columns to table 2
    for column in link_formula_columns:
        path_parameters = {'base_uuid': base.uuid}
        case: Case = base_operations_schema.get_operation_by_id('insertColumn') \
            .make_case(path_parameters=path_parameters, body=column, headers=headers)
        response = case.call()
        assert response.status_code == 200

    # List rows
    query = {'table_name': table_name_2, 'convert_keys': True}
    operation = base_operations_schema.get_operation_by_id(operation_id)
    matcher = path_type(
        {
            r"rows\..*\.(_id|_ctime|_mtime|_creator|_last_modifier)": (str,),
            r"rows\..*\.link.*\.row_id": (str,),
        },
        regex=True,
    )

    case: Case = operation.make_case(path_parameters=path_parameters, query=query, headers=headers)
    response = case.call()

    # Verify that response matches snapshot
    assert snapshot_json(matcher=matcher) == response.json()

@pytest.mark.parametrize('operation_id', ['listRows'])
def test_listRows_files_images(base: Base,  snapshot_json: SnapshotAssertion, operation_id: str):
    table_name = f'test_{operation_id}_files_images'
    columns = [
        {'column_name': 'text', 'column_type': 'text'},
        {'column_name': 'images', 'column_type': 'image'},
        {'column_name': 'files', 'column_type': 'file'},
    ]
    create_table(base, table_name, columns)

    # Generate upload link
    headers = {'Authorization': f'Bearer {base.api_token}'}
    case: Case = file_operations.get_operation_by_id('getUploadLink').make_case(headers=headers)
    response = case.call()
    assert response.status_code == 200

    upload_link_data = response.json()

    # TODO: Use schemathesis to execute uploadFile requests

    # Upload image
    files = { "file": ("seatable-logo.svg", open("assets/seatable-logo.svg", "rb"), "image/svg+xml") }
    payload = {
        'parent_dir': upload_link_data['parent_path'],
        'relative_path': upload_link_data['img_relative_path'],
        'replace': 1,
    }
    headers = {'Accept': 'application/json'}
    response = requests.post(f'{upload_link_data["upload_link"]}?ret-json=1', data=payload, files=files, headers=headers)
    assert response.status_code == 200
    uploaded_image = response.json()

    # Upload file
    files = { "file": ("test.txt", open("assets/test.txt", "rb"), "text/plain") }
    payload = {
        'parent_dir': upload_link_data['parent_path'],
        'relative_path': upload_link_data['file_relative_path'],
        'replace': 1,
    }
    headers = {'Accept': 'application/json'}
    response = requests.post(f'{upload_link_data["upload_link"]}?ret-json=1', data=payload, files=files, headers=headers)
    assert response.status_code == 200
    uploaded_file = response.json()

    # Insert row
    row = {
        'images': [f'/workspace/{base.workspace_id}{upload_link_data["parent_path"]}/{upload_link_data["img_relative_path"]}/{uploaded_image[0]["name"]}'],
        'files': [
            {
                'name': uploaded_file[0]['name'],
                'size': uploaded_file[0]['size'],
                'type': 'file',
                'url': f'/workspace/{base.workspace_id}{upload_link_data["parent_path"]}/{upload_link_data["file_relative_path"]}/{uploaded_file[0]["name"]}'
            }
        ],
    }
    append_rows(base, table_name, [row])

    # List rows
    path_parameters = {'base_uuid': base.uuid}
    query = {'table_name': table_name, 'convert_keys': True}
    headers = {'Authorization': f'Bearer {base.token}'}
    operation = base_operations_schema.get_operation_by_id(operation_id)
    case: Case = operation.make_case(path_parameters=path_parameters, query=query, headers=headers)
    response = case.call()

    # Verify that response matches snapshot
    matcher = path_type(
            {
                r"rows\..*\.(_id|_ctime|_mtime|_creator|_last_modifier)": (str,),
                r"rows\..*\.files.0.url": (str,),
                r"rows\..*\.images.0": (str,),
            },
            regex=True,
        )
    assert snapshot_json(matcher=matcher) == response.json()

@pytest.mark.parametrize('operation_id', ['querySQL'])
def test_querySQL(base: Base, snapshot_json: SnapshotAssertion, operation_id: str):
    table_name = f'test_{operation_id}'

    create_table(base, table_name, COLUMNS)
    append_rows(base, table_name, ROWS)

    path_parameters = {'base_uuid': base.uuid}
    body = {'sql': f'SELECT * FROM {table_name}', 'convert_keys': True}
    headers = {'Authorization': f'Bearer {base.token}'}
    operation = base_operations_schema.get_operation_by_id(operation_id)

    case: Case = operation.make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200

    matcher = path_type(
        {
            "metadata": (list,),
            # Exclude unstable props from value comparison and just store their types
            r"results\..*\.(_id|_ctime|_mtime|_creator|_last_modifier|auto-number-date-prefix)": (str,),
        },
        regex=True,
    )

    assert snapshot_json(matcher=matcher) == response.json()

def create_table(base: Base, table_name: str, columns: list[dict]):
    path_parameters = {'base_uuid': base.uuid}
    body = {'table_name': table_name, 'columns': columns}
    headers = {'Authorization': f'Bearer {base.token}'}

    operation = base_operations_schema.get_operation_by_id('createTable')
    case: Case = operation.make_case(path_parameters=path_parameters, body=body, headers=headers)

    response = case.call()

    assert response.status_code == 200

def append_rows(base: Base, table_name: str, rows: list[dict]) -> list[str]:
    path_parameters = {'base_uuid': base.uuid}
    body = {'table_name': table_name, 'rows': rows}
    headers = {'Authorization': f'Bearer {base.token}'}

    operation = base_operations_schema.get_operation_by_id('appendRows')
    case: Case = operation.make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200

    # Extract row IDs
    row_ids = [r['_id'] for r in response.json()['row_ids']]

    assert len(row_ids) == len(rows)

    return row_ids
