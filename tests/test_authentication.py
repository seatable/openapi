import schemathesis
from conftest import Base, BASE_URL, USERNAME, PASSWORD
from schemathesis import Case
from syrupy.assertion import SnapshotAssertion
from syrupy.matchers import path_type

authentication_schema = schemathesis.from_path('../authentication.yaml', base_url=BASE_URL, validate_schema=True)

def test_getAccountTokenfromUsername(snapshot_json: SnapshotAssertion):
    body = {'username': USERNAME, 'password': PASSWORD}
    case: Case = authentication_schema.get_operation_by_id('getAccountTokenfromUsername').make_case(body=body)
    response = case.call_and_validate()

    assert response.status_code == 200

    matcher = path_type({
        'token': (str,),
    })

    assert snapshot_json(matcher=matcher) == response.json()

def test_getBaseTokenWithApiToken(base: Base, snapshot_json: SnapshotAssertion):
    case: Case = authentication_schema.get_operation_by_id('getBaseTokenWithApiToken').make_case()
    response = case.call_and_validate(headers={'Authorization': f'Bearer {base.api_token}'})

    assert response.status_code == 200

    json = response.json()

    assert json['dtable_server'].startswith('https://')
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
