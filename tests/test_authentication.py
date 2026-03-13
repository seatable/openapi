from conftest import Base, USERNAME, PASSWORD, authentication_schema
from schemathesis import Case
from syrupy.assertion import SnapshotAssertion
from syrupy.matchers import path_type

def test_getAccountTokenfromUsername(snapshot_json: SnapshotAssertion):
    body = {'username': USERNAME, 'password': PASSWORD}
    case: Case = authentication_schema.find_operation_by_id('getAccountTokenfromUsername').Case(body=body)
    response = case.call()

    assert response.status_code == 200

    matcher = path_type({
        'token': (str,),
    })

    assert snapshot_json(matcher=matcher) == response.json()

def test_getBaseTokenWithApiToken(base: Base, snapshot_json: SnapshotAssertion):
    case: Case = authentication_schema.find_operation_by_id('getBaseTokenWithApiToken').Case()
    response = case.call(headers={'Authorization': f'Bearer {base.api_token}'})

    assert response.status_code == 200

    json = response.json()

    assert json['dtable_server'].startswith('http://') or json['dtable_server'].startswith('https://')
    assert json['dtable_server'].endswith('/api-gateway/')

    matcher = path_type({
        'access_token': (str,),
        'app_name': (str,),
        'dtable_name': (str,),
        'dtable_server': (str,),
        'dtable_uuid': (str,),
        'use_api_gateway': (bool,),
        'workspace_id': (int,),
    })

    assert snapshot_json(matcher=matcher) == json
