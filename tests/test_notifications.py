import time
from typing import Generator

import pytest
from conftest import Base, Secret, authentication_schema, base_operations_schema, user_account_operations
from schemathesis import Case
from syrupy.assertion import SnapshotAssertion
from syrupy.matchers import path_type

from test_base_operations import create_table, append_rows


def _headers(base):
    return {'Authorization': f'Bearer {base.token}'}


def test_listBaseNotifications(base: Base, snapshot_json: SnapshotAssertion):
    case: Case = base_operations_schema.find_operation_by_id('listBaseNotifications') \
        .Case(
            path_parameters={'base_uuid': base.uuid},
            headers=_headers(base),
        )
    response = case.call()

    assert response.status_code == 200
    assert snapshot_json == response.json()


def test_sendToastNotification(base: Base, snapshot_json: SnapshotAssertion):
    """Send a toast notification. Requires at least one recipient user."""
    import os, requests
    # Get the test user's internal user_id
    server = os.environ['SEATABLE_SERVER']
    account_token = os.environ.get('_ACCOUNT_TOKEN', '')
    if not account_token:
        resp = requests.post(f'{server}/api2/auth-token/',
            data={'username': os.environ['SEATABLE_USERNAME'], 'password': os.environ['SEATABLE_PASSWORD']})
        account_token = resp.json()['token']

    resp = requests.get(f'{server}/api2/account/info/', headers={'Authorization': f'Token {account_token}'})
    user_id = resp.json().get('email', '')

    case: Case = base_operations_schema.find_operation_by_id('sendToastNotification') \
        .Case(
            path_parameters={'base_uuid': base.uuid},
            body={
                'to_user': user_id,
                'toast_type': 'toast',
                'detail': {'table_id': '0000', 'msg': 'Hello from test'},
            },
            headers=_headers(base),
        )
    response = case.call()

    assert response.status_code == 200
    assert snapshot_json == response.json()


@pytest.fixture
def admin_base(base: Base, account_token: Secret, system_admin_account_token: Secret) -> Generator[tuple[Base, str], None, None]:
    """Share the base with the sys-admin and yield the admin's view of it together with the admin's user ID.

    dtable-server does not notify users about their own changes, so notification tests have the test user
    assign the sys-admin and read the resulting notifications with the admin's base token.
    """
    admin_headers = {'Authorization': f'Bearer {system_admin_account_token.value}'}

    case: Case = user_account_operations.find_operation_by_id('getAccountInfo').Case()
    response = case.call(headers=admin_headers)
    assert response.status_code == 200
    admin_email = response.json()['email']

    share_path_parameters = {'workspace_id': base.workspace_id, 'base_name': base.name}
    case: Case = user_account_operations.find_operation_by_id('createUserShare') \
        .Case(path_parameters=share_path_parameters, body={'email': admin_email, 'permission': 'rw'})
    response = case.call(headers={'Authorization': f'Bearer {account_token.value}'})
    assert response.status_code == 201

    try:
        case: Case = authentication_schema.find_operation_by_id('getBaseTokenWithAccountToken') \
            .Case(path_parameters=share_path_parameters)
        response = case.call(headers=admin_headers)
        assert response.status_code == 200
        admin_base = Base(
            workspace_id=base.workspace_id, uuid=base.uuid, name=base.name,
            token=response.json()['access_token'], api_token='',
        )

        yield admin_base, admin_email

        # Start every test with an empty notification list for the admin
        case: Case = base_operations_schema.find_operation_by_id('deleteBaseNotifications') \
            .Case(path_parameters={'base_uuid': base.uuid}, headers=_headers(admin_base))
        assert case.call().status_code == 200
    finally:
        case: Case = user_account_operations.find_operation_by_id('deleteUserShare') \
            .Case(path_parameters=share_path_parameters, body={'email': admin_email})
        response = case.call(headers={'Authorization': f'Bearer {account_token.value}'})
        assert response.status_code == 200


def _create_selected_collaborator_notification(base: Base, admin_base: Base, admin_email: str, table_name: str) -> dict:
    """Assign the admin in a collaborator column with enable_send_notification and return the admin's notifications."""
    create_table(base, table_name, [
        {'column_name': 'text', 'column_type': 'text'},
        {'column_name': 'collaborator', 'column_type': 'collaborator', 'column_data': {'enable_send_notification': True}},
    ])
    append_rows(base, table_name, [{'text': 'notify target', 'collaborator': [admin_email]}])

    # dtable-server creates collaborator notifications asynchronously (checked every 2 seconds)
    case: Case = base_operations_schema.find_operation_by_id('listBaseNotifications') \
        .Case(path_parameters={'base_uuid': base.uuid}, headers=_headers(admin_base))
    deadline = time.monotonic() + 10
    while True:
        response = case.call()
        assert response.status_code == 200
        data = response.json()
        if data['notification_list'] or time.monotonic() > deadline:
            return data
        time.sleep(0.5)


def _list_notifications(base: Base) -> dict:
    case: Case = base_operations_schema.find_operation_by_id('listBaseNotifications') \
        .Case(path_parameters={'base_uuid': base.uuid}, headers=_headers(base))
    response = case.call()
    assert response.status_code == 200
    return response.json()


NOTIFICATION_MATCHER = path_type({
    r'notification_list\..*\.id': (int,),
    r'notification_list\..*\.username': (str,),
    r'notification_list\..*\.created_at': (str,),
    r'notification_list\..*\.detail\.author': (str,),
    r'notification_list\..*\.detail\.row_id': (str,),
    r'notification_list\..*\.detail\.table_id': (str,),
}, regex=True)


def test_listBaseNotifications_selected_collaborator(
    base: Base, admin_base: tuple[Base, str], snapshot_json: SnapshotAssertion,
):
    admin, admin_email = admin_base
    data = _create_selected_collaborator_notification(
        base, admin, admin_email, 'test_listBaseNotifications_selected_collaborator',
    )

    assert snapshot_json(matcher=NOTIFICATION_MATCHER) == data


def test_markBaseNotificationAsSeen(base: Base, admin_base: tuple[Base, str], snapshot_json: SnapshotAssertion):
    admin, admin_email = admin_base
    data = _create_selected_collaborator_notification(base, admin, admin_email, 'test_markBaseNotificationAsSeen')
    assert len(data['notification_list']) == 1
    notification = data['notification_list'][0]
    assert notification['seen'] == 0

    # The body is form-encoded: requests would send a Python bool as "True", but the API only accepts "true"
    case: Case = base_operations_schema.find_operation_by_id('markBaseNotificationAsSeen') \
        .Case(
            path_parameters={'base_uuid': base.uuid, 'notification_id': notification['id']},
            body={'seen': 'true'},
            headers=_headers(admin),
        )
    response = case.call()

    assert response.status_code == 200
    assert snapshot_json == response.json()

    # Notification is now marked as seen
    assert snapshot_json(matcher=NOTIFICATION_MATCHER) == _list_notifications(admin)


def test_markBaseNotificationsAsSeen(base: Base, admin_base: tuple[Base, str], snapshot_json: SnapshotAssertion):
    admin, admin_email = admin_base
    data = _create_selected_collaborator_notification(base, admin, admin_email, 'test_markBaseNotificationsAsSeen')
    assert len(data['notification_list']) == 1
    assert data['notification_list'][0]['seen'] == 0

    # The body is form-encoded: requests would send a Python bool as "True", but the API only accepts "true"
    case: Case = base_operations_schema.find_operation_by_id('markBaseNotificationsAsSeen') \
        .Case(
            path_parameters={'base_uuid': base.uuid},
            body={'seen': 'true'},
            headers=_headers(admin),
        )
    response = case.call()

    assert response.status_code == 200
    assert snapshot_json == response.json()

    # All notifications are now marked as seen
    assert snapshot_json(matcher=NOTIFICATION_MATCHER) == _list_notifications(admin)


def test_deleteBaseNotifications(base: Base, admin_base: tuple[Base, str], snapshot_json: SnapshotAssertion):
    admin, admin_email = admin_base
    data = _create_selected_collaborator_notification(base, admin, admin_email, 'test_deleteBaseNotifications')
    assert len(data['notification_list']) == 1

    case: Case = base_operations_schema.find_operation_by_id('deleteBaseNotifications') \
        .Case(
            path_parameters={'base_uuid': base.uuid},
            headers=_headers(admin),
        )
    response = case.call()

    assert response.status_code == 200
    assert snapshot_json == response.json()

    # All notifications are gone
    assert snapshot_json == _list_notifications(admin)
