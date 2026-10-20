from conftest import Base, base_operations_schema
from schemathesis import Case
from syrupy.assertion import SnapshotAssertion
from syrupy.filters import paths
from syrupy.matchers import path_type

from test_base_operations import create_table

# Properties that differ between the JS and Go dtable-server
_DEFAULT_TABLE = 'metadata.tables.0'
_TEST_TABLE = 'metadata.tables.1'
_REMOVED_VIEW_PROPS = ('formula_rows', 'groups', 'rows', 'summaries')
EXCLUDED_PATHS = paths(
    'metadata.description',
    'metadata.scripts',
    *(f'{_DEFAULT_TABLE}.{p}' for p in (
        'description', 'header_settings', 'is_header_locked', 'summary_configs', 'table_permissions',
    )),
    *(f'{_DEFAULT_TABLE}.columns.0.{p}' for p in (
        'colorbys', 'data', 'description', 'draggable', 'edit_metadata_permission_type',
        'edit_metadata_permitted_group', 'edit_metadata_permitted_users', 'permission_type',
        'permitted_group', 'permitted_users',
    )),
    *(f'{_DEFAULT_TABLE}.views.0.{p}' for p in ('colorbys', 'private_for', 'row_height', *_REMOVED_VIEW_PROPS)),
    f'{_TEST_TABLE}.description',
    f'{_TEST_TABLE}.table_permissions',
    *(f'{_TEST_TABLE}.views.0.{p}' for p in ('colors', 'column_colors', *_REMOVED_VIEW_PROPS)),
)


def test_getMetadata(base: Base, snapshot_json: SnapshotAssertion):
    create_table(base, 'test_metadata', [
        {'column_name': 'text', 'column_type': 'text'},
        {'column_name': 'number', 'column_type': 'number'},
    ])

    path_parameters = {'base_uuid': base.uuid}
    headers = {'Authorization': f'Bearer {base.token}'}

    case: Case = base_operations_schema.find_operation_by_id('getMetadata') \
        .Case(path_parameters=path_parameters, headers=headers)
    response = case.call()

    assert response.status_code == 200

    data = response.json()

    matcher = path_type({
        r"metadata\.tables\..*\._id": (str,),
        r"metadata\.tables\..*\.columns\..*\.key": (str,),
    }, regex=True)

    assert snapshot_json(exclude=EXCLUDED_PATHS, matcher=matcher) == data


def test_listCollaborators(base: Base, snapshot_json: SnapshotAssertion):
    path_parameters = {'base_uuid': base.uuid}
    headers = {'Authorization': f'Bearer {base.token}'}

    case: Case = base_operations_schema.find_operation_by_id('listCollaborators') \
        .Case(path_parameters=path_parameters, headers=headers)
    response = case.call()

    assert response.status_code == 200

    data = response.json()

    matcher = path_type({
        r"user_list\..*\.email": (str,),
        r"user_list\..*\.avatar_url": (str,),
        r"user_list\..*\.contact_email": (str,),
        r"user_list\..*\.name": (str,),
        r"user_list\..*\.name_pinyin": (str,),
    }, regex=True)

    assert snapshot_json(matcher=matcher) == data
