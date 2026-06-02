import pytest
from conftest import Base, base_operations_schema
from schemathesis import Case

from test_base_operations import create_table, append_rows


def _headers(base):
    return {'Authorization': f'Bearer {base.token}'}


def test_listBaseNotifications(base: Base):
    case: Case = base_operations_schema.find_operation_by_id('listBaseNotifications') \
        .Case(
            path_parameters={'base_uuid': base.uuid},
            headers=_headers(base),
        )
    response = case.call()

    assert response.status_code == 200
    data = response.json()
    assert 'notification_list' in data


@pytest.mark.xfail(reason="API returns 400 'seen invalid' — expects form-encoded string 'true', not JSON boolean")
def test_markBaseNotificationsAsSeen(base: Base):
    case: Case = base_operations_schema.find_operation_by_id('markBaseNotificationsAsSeen') \
        .Case(
            path_parameters={'base_uuid': base.uuid},
            body={'seen': True},
            headers=_headers(base),
        )
    response = case.call()

    assert response.status_code == 200


def test_deleteBaseNotifications(base: Base):
    case: Case = base_operations_schema.find_operation_by_id('deleteBaseNotifications') \
        .Case(
            path_parameters={'base_uuid': base.uuid},
            headers=_headers(base),
        )
    response = case.call()

    assert response.status_code == 200


@pytest.mark.xfail(reason="API returns 400 'seen invalid' — expects form-encoded string 'true', not JSON boolean")
def test_markBaseNotificationAsSeen(base: Base):
    """Mark a single notification as seen. Requires an existing notification_id."""
    # First list notifications to get an ID
    import os, requests
    server = os.environ['SEATABLE_SERVER']
    resp = requests.get(
        f'{server}/api-gateway/api/v2/dtables/{base.uuid}/notifications/',
        headers=_headers(base),
    )
    assert resp.status_code == 200
    notifications = resp.json().get('notification_list', [])

    if not notifications:
        pytest.skip('No notifications available to mark as seen')

    notification_id = notifications[0]['id']

    case: Case = base_operations_schema.find_operation_by_id('markBaseNotificationAsSeen') \
        .Case(
            path_parameters={'base_uuid': base.uuid, 'notification_id': notification_id},
            body={'seen': True},
            headers=_headers(base),
        )
    response = case.call()

    assert response.status_code == 200


def test_sendToastNotification(base: Base):
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
