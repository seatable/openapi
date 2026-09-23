from conftest import Base, base_operations_schema
from schemathesis import Case
from syrupy.assertion import SnapshotAssertion
from syrupy.matchers import path_type

from test_base_operations import create_table


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

    assert snapshot_json(matcher=matcher) == data


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
