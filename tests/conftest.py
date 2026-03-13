import os
import re
import pytest
import schemathesis
import secrets
import string
from dataclasses import dataclass, field
from datetime import datetime
from random import randint
from requests import Response
from schemathesis import Case
from schemathesis.specs.openapi.checks import content_type_conformance, response_schema_conformance, status_code_conformance
from syrupy.extensions.json import JSONSnapshotExtension
from typing import Generator

# Patterns for volatile values that change between test runs
_TIMESTAMP_RE = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}')
_AUTH_LOCAL_RE = re.compile(r'^[0-9a-f]+@auth\.local$')
_ROW_ID_RE = re.compile(r'^[A-Za-z0-9_-]{22}$')


def normalize(data):
    """Replace volatile values with type placeholders for stable snapshot comparison.

    Handles: ISO timestamps, internal @auth.local emails, 22-char row IDs.
    """
    if isinstance(data, dict):
        return {k: normalize(v) for k, v in data.items()}
    if isinstance(data, list):
        return [normalize(v) for v in data]
    if isinstance(data, str):
        if _TIMESTAMP_RE.match(data):
            return 'str'
        if _AUTH_LOCAL_RE.match(data):
            return 'str'
        if _ROW_ID_RE.match(data):
            return 'str'
        return data
    return data


def normalize_row(row, keep_keys=None):
    """Normalize a row dict: replace volatile values and rename dynamic column keys.

    System keys (_id, _ctime, ...) and keys listed in keep_keys are preserved.
    Other short alphanumeric keys (column keys like 'D4Z6') are renamed to
    '_col_0', '_col_1', etc. so snapshots stay stable across runs.
    """
    if keep_keys is None:
        keep_keys = {'0000'}

    result = {}
    system_keys = sorted(k for k in row if k.startswith('_'))
    kept = sorted(k for k in row if k in keep_keys)
    dynamic = sorted(k for k in row if not k.startswith('_') and k not in keep_keys)

    for k in system_keys:
        result[k] = normalize(row[k])
    for k in kept:
        result[k] = row[k]
    for i, k in enumerate(dynamic):
        result[f'_col_{i}'] = row[k]

    return result

BASE_URL = os.environ.get('SEATABLE_SERVER')
USERNAME = os.environ.get('SEATABLE_USERNAME')
PASSWORD = os.environ.get('SEATABLE_PASSWORD')
ADMIN_USERNAME = os.environ.get('SEATABLE_ADMIN_USERNAME')
ADMIN_PASSWORD = os.environ.get('SEATABLE_ADMIN_PASSWORD')
CLEANUP_AFTER_TESTS = os.environ.get('CLEANUP_AFTER_TESTS', 'True')

assert BASE_URL is not None, 'SEATABLE_SERVER environment variable is not set'
assert USERNAME is not None, 'SEATABLE_USERNAME environment variable is not set'
assert PASSWORD is not None, 'SEATABLE_PASSWORD environment variable is not set'
assert ADMIN_USERNAME is not None, 'SEATABLE_ADMIN_USERNAME environment variable is not set'
assert ADMIN_PASSWORD is not None, 'SEATABLE_ADMIN_PASSWORD environment variable is not set'
assert CLEANUP_AFTER_TESTS in ["True", "False"], "CLEANUP_AFTER_TESTS environment variable must be either 'True' or 'False'"

user_account_operations = schemathesis.openapi.from_path('../user_account_operations.yaml')
system_admin_account_operations = schemathesis.openapi.from_path('../system_admin_account_operations.yaml')
authentication_schema = schemathesis.openapi.from_path('../authentication.yaml')
base_operations_schema = schemathesis.openapi.from_path('../base_operations.yaml')

SCHEMA_VALIDATION_CHECKS = (
    status_code_conformance,
    content_type_conformance,
    response_schema_conformance,
)

@schemathesis.hook
def after_call(context, case, response: Response):
    # TODO: Disable redirects for all tests? (to prevent issues like https://forum.seatable.com/t/seatable-4-4-out-now/4237/4)

    # Log all request URLs. You have to run pytest with '-rA' in order to see these for successful tests.
    print(f'{response.request.method} {response.request.url}')

    # Validate response against OpenAPI schema
    case.validate_response(response, checks=SCHEMA_VALIDATION_CHECKS)

@dataclass
class Base:
    """Class for storing base info"""
    workspace_id: int
    uuid: str
    # Hide base token from console output by setting repr=False
    token: str = field(repr=False)
    # Temporary API token for file uploads
    api_token: str = field(repr=False)

@dataclass
class TeamAdmin:
    """Class for storing team/org info"""
    team_id: int
    # Hide base token from console output by setting repr=False
    account_token: str = field(repr=False)

class Secret:
    """
    Class to store a secret, ensures that the value will not be printed (e.g. if an assertion fails)
    Based on https://github.com/pytest-dev/pytest/issues/8613#issuecomment-830011874
    """
    def __init__(self, value: str):
        self.value = value

    def __repr__(self):
        return "Secret(********)"

    def __str__(self):
        return "*******"

@pytest.fixture
def snapshot_json(snapshot):
    # https://github.com/tophat/syrupy#jsonsnapshotextension
    return snapshot.use_extension(JSONSnapshotExtension)

# scope='module' ensures that this functions runs only once for all tests in this module
@pytest.fixture(scope='module')
def account_token() -> str:
    body = {"username": USERNAME, "password": PASSWORD}

    operation = authentication_schema.find_operation_by_id('getAccountTokenfromUsername')
    case: Case = operation.Case(body=body)
    response = case.call()

    assert response.status_code == 200

    account_token = response.json()['token']
    assert isinstance(account_token, str)

    return Secret(account_token)

@pytest.fixture(scope='module')
def base(account_token: Secret):
    group_name = f'Automated Tests {datetime.today().strftime("%Y-%m-%d %H-%M-%S")}'
    group_id, workspace_id = create_group(account_token=account_token, group_name=group_name)

    base_name = 'Automated Tests'

    body = {"workspace_id": workspace_id, "name": base_name}
    case: Case = user_account_operations.find_operation_by_id('createBase').Case(body=body)
    response = case.call(headers={"Authorization": f"Bearer {account_token.value}"})

    assert response.status_code == 201

    base_uuid = response.json()["table"]["uuid"]
    assert isinstance(base_uuid, str)

    path_parameters = {'workspace_id': workspace_id, 'base_name': base_name}
    headers = {'Authorization': f'Bearer {account_token.value}'}

    operation = authentication_schema.find_operation_by_id('getBaseTokenWithAccountToken')
    case: Case = operation.Case(path_parameters=path_parameters)
    response = case.call(headers=headers)

    assert response.status_code == 200

    base_token = response.json()['access_token']
    assert isinstance(base_token, str)

    # Get API token for file uploads
    api_token = get_api_token(account_token, workspace_id, base_name)

    # Yield back to the test function
    yield Base(workspace_id=workspace_id, uuid=base_uuid, token=base_token, api_token=api_token.value)

    if CLEANUP_AFTER_TESTS == 'True':
        # Delete base to not cause any issues on future test runs
        path_parameters = {'workspace_id': workspace_id}
        body = {'name': base_name}

        case: Case = user_account_operations.find_operation_by_id('deleteBase').Case(path_parameters=path_parameters, body=body)
        response = case.call(headers={"Authorization": f"Bearer {account_token.value}"})

        assert response.status_code == 200

        delete_group(account_token, group_id)

def get_api_token(account_token: Secret, workspace_id: int, base_name: str) -> Secret:
    path_parameters = {'workspace_id': workspace_id, 'base_name': base_name}
    headers = {'Authorization': f'Bearer {account_token.value}'}
    case: Case = authentication_schema.find_operation_by_id('createTempApiToken').Case(path_parameters=path_parameters)
    response = case.call(headers=headers)

    assert response.status_code == 200

    api_token = response.json()['api_token']
    assert isinstance(api_token, str)

    return Secret(api_token)

@pytest.fixture(scope='module')
def workspace_id(account_token: Secret) -> Generator[int, None, None]:
    base_name = "automated-testing-ahSh2sot"

    group_name = f'Automated Tests {datetime.today().strftime("%Y-%m-%d %H-%M-%S")} {randint(1, 100)}'
    group_id, workspace_id = create_group(account_token=account_token, group_name=group_name)

    yield workspace_id

    if CLEANUP_AFTER_TESTS == 'True':
        # Delete base to not cause any issues on future test runs
        path_parameters = {'workspace_id': workspace_id}
        body = {'name': base_name}

        case: Case = user_account_operations.find_operation_by_id('deleteBase').Case(path_parameters=path_parameters, body=body)
        response = case.call(headers={"Authorization": f"Bearer {account_token.value}"})

        assert response.status_code == 200

        delete_group(account_token=account_token, group_id=group_id)

# scope='module' ensures that this functions runs only once for all tests in this module
@pytest.fixture(scope='module')
def system_admin_account_token() -> Secret:
    body = {"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}

    operation = authentication_schema.find_operation_by_id('getAccountTokenfromUsername')
    case: Case = operation.Case(body=body)
    response = case.call()

    assert response.status_code == 200

    account_token = response.json()['token']
    assert isinstance(account_token, str)

    return Secret(account_token)

@pytest.fixture
def team(system_admin_account_token: Secret) -> Generator[int, None, None]:
    team_name = f'automated-testing-org-{randint(1, 10000)}'
    team_admin_email = 'automated-testing-team-admin@seatable.io'
    team_admin_password = generate_password()

    body = {
        'org_name': team_name,
        'admin_email': team_admin_email,
        'password': team_admin_password,
        'with_workspace': True,
    }
    case: Case = system_admin_account_operations.find_operation_by_id('addTeam').Case(body=body)
    response = case.call(headers={'Authorization': f'Bearer {system_admin_account_token.value}'})

    assert response.status_code == 200

    team = response.json()
    team_id = team['org_id']
    assert isinstance(team_id, int)

    # Fetch account token for team admin
    body = {"username": team_admin_email, "password": team_admin_password}
    operation = authentication_schema.find_operation_by_id('getAccountTokenfromUsername')
    case: Case = operation.Case(body=body)
    response = case.call()

    assert response.status_code == 200

    account_token = response.json()['token']
    assert isinstance(account_token, str)

    yield TeamAdmin(team_id=team_id, account_token=account_token)

    if CLEANUP_AFTER_TESTS == 'True':
        path_parameters = {'org_id': team_id}
        case: Case = system_admin_account_operations.find_operation_by_id('deleteTeam').Case(path_parameters=path_parameters)
        response = case.call(headers={'Authorization': f'Bearer {system_admin_account_token.value}'})

@pytest.fixture
def team_name(system_admin_account_token: Secret) -> Generator[str, None, None]:
    team_name = f'automated-testing-org-{randint(1, 10000)}'

    yield team_name

    if CLEANUP_AFTER_TESTS == 'True':
        # Remove team to not cause issues on future test runs
        case: Case = system_admin_account_operations.find_operation_by_id('listTeams').Case()
        response = case.call(headers={'Authorization': f'Bearer {system_admin_account_token.value}'})
        data = response.json()

        assert response.status_code == 200

        # Find the organization we want to delete
        org_id = next((team['org_id'] for team in data['organizations'] if team['org_name'] == team_name), None)
        assert isinstance(org_id, int)

        path_parameters = {'org_id': org_id}
        case: Case = system_admin_account_operations.find_operation_by_id('deleteTeam').Case(path_parameters=path_parameters)
        response = case.call(headers={'Authorization': f'Bearer {system_admin_account_token.value}'})

def generate_password() -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(20))

def create_group(account_token: Secret, group_name: str) -> tuple[int, int]:
    """Creates a group and returns (group_id, workspace_id)"""
    body = {'name': group_name}
    headers = {'Authorization': f'Bearer {account_token.value}'}
    case: Case = user_account_operations.find_operation_by_id('createGroup') \
        .Case(body=body)
    response = case.call(headers=headers)
    assert response.status_code == 201

    group_id = response.json()['id']
    assert isinstance(group_id, int)

    # TODO: Is there an easier way to get the workspace ID of a group?
    case: Case = user_account_operations.find_operation_by_id('listWorkspaces') \
        .Case()
    response = case.call(headers=headers)

    assert response.status_code == 200

    workspaces = response.json()['workspace_list']
    workspace_id = next((w['id'] for w in workspaces if w.get('group_id', None) == group_id), None)
    assert isinstance(workspace_id, int)

    return (group_id, workspace_id)

def delete_group(account_token: Secret, group_id: int):

    if CLEANUP_AFTER_TESTS == 'True':
        path_parameters = {'group_id': group_id}
        headers = {'Authorization': f'Bearer {account_token.value}'}
        case: Case = user_account_operations.find_operation_by_id('deleteGroup') \
            .Case(path_parameters=path_parameters)
        response = case.call(headers=headers)

        assert response.status_code == 200

def free_user_slot(headers: dict):
    """Delete any leftover users to free a license slot (license allows max 3 users)."""
    case: Case = system_admin_account_operations.find_operation_by_id('listUsers').Case()
    response = case.call(headers=headers)
    for user in response.json()['data']:
        # Do not try to delete preconfigured users or staff members
        if user['contact_email'] in [USERNAME, ADMIN_USERNAME] or user['is_staff'] == True:
            continue

        path_parameters = {'user_id': user['email']}
        case: Case = system_admin_account_operations.find_operation_by_id('deleteUser') \
            .Case(path_parameters=path_parameters)
        case.call(headers=headers)
        return
