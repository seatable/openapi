import schemathesis
from conftest import BASE_URL, Secret, authentication_schema
from schemathesis import Case

ping_and_info_schema = schemathesis.from_path('../ping_and_info.yaml', base_url=BASE_URL, validate_schema=True)

def test_getServerInfo():
    case: Case = ping_and_info_schema.get_operation_by_id('getServerInfo').make_case()
    response = case.call()

    assert response.status_code == 200

    data = response.json()
    assert 'version' in data
    assert 'edition' in data
    assert isinstance(data['version'], str)
    assert isinstance(data['edition'], str)

def test_pingServer():
    case: Case = ping_and_info_schema.get_operation_by_id('pingServer').make_case()
    response = case.call()

    assert response.status_code == 200
    assert response.text.strip('"') == 'pong'

def test_pingServerWithAuth(account_token: Secret):
    case: Case = ping_and_info_schema.get_operation_by_id('pingServerWithAuth').make_case()
    response = case.call(headers={'Authorization': f'Bearer {account_token.value}'})

    assert response.status_code == 200
    assert response.text.strip('"') == 'pong'

def test_pingDtableServer():
    case: Case = ping_and_info_schema.get_operation_by_id('pingDtableServer').make_case()
    response = case.call()

    assert response.status_code == 200

def test_pingDtableDbServer():
    case: Case = ping_and_info_schema.get_operation_by_id('pingDtableDbServer').make_case()
    response = case.call()

    assert response.status_code == 200

def test_pingApiGateway():
    case: Case = ping_and_info_schema.get_operation_by_id('pingApiGateway').make_case()
    response = case.call()

    assert response.status_code == 200
