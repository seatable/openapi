import io
import requests
from conftest import Base, BASE_URL, base_operations_schema
from schemathesis import Case

import schemathesis

file_operations_schema = schemathesis.openapi.from_path('../file_operations.yaml')

from test_base_operations import create_table, append_rows


TABLE = 'test_files'
COLUMNS = [
    {'column_name': 'Name', 'column_type': 'text'},
    {'column_name': 'Attachment', 'column_type': 'file'},
    {'column_name': 'Image', 'column_type': 'image'},
]


def _api_headers(base: Base) -> dict:
    return {'Authorization': f'Token {base.api_token}'}


def _base_headers(base: Base) -> dict:
    return {'Authorization': f'Bearer {base.token}'}


def test_get_upload_link(base: Base):
    """Get an upload link for the base."""
    case: Case = file_operations_schema.find_operation_by_id('getUploadLink') \
        .Case()
    response = case.call(headers=_api_headers(base))

    assert response.status_code == 200
    data = response.json()
    assert 'upload_link' in data
    assert 'parent_path' in data
    assert 'img_relative_path' in data
    assert 'file_relative_path' in data


def test_upload_and_download_file(base: Base):
    """Upload a file, verify download link works, then delete it."""
    # Step 1: Get upload link
    case: Case = file_operations_schema.find_operation_by_id('getUploadLink') \
        .Case()
    response = case.call(headers=_api_headers(base))
    assert response.status_code == 200

    upload_data = response.json()
    upload_link = upload_data['upload_link']
    parent_path = upload_data['parent_path']
    file_relative_path = upload_data['file_relative_path']

    # Step 2: Upload a small text file
    file_content = b'Hello, SeaTable!'
    files = {'file': ('test-upload.txt', io.BytesIO(file_content), 'text/plain')}
    form_data = {
        'parent_dir': parent_path,
        'relative_path': file_relative_path,
        'replace': '0',
    }

    upload_response = requests.post(
        f'{upload_link}?ret-json=1',
        headers=_api_headers(base),
        files=files,
        data=form_data,
    )
    assert upload_response.status_code == 200
    uploaded = upload_response.json()
    assert len(uploaded) == 1
    assert uploaded[0]['name'] == 'test-upload.txt'
    assert uploaded[0]['size'] == len(file_content)

    # Step 3: Get download link
    file_path = f'/{file_relative_path}/test-upload.txt'
    query = {'path': file_path}
    case: Case = file_operations_schema.find_operation_by_id('getFileDownloadLink') \
        .Case(query=query)
    response = case.call(headers=_api_headers(base))
    assert response.status_code == 200

    download_link = response.json()['download_link']
    assert 'test-upload.txt' in download_link

    # Step 4: Download and verify content
    download_response = requests.get(download_link)
    assert download_response.status_code == 200
    assert download_response.content == file_content

    # Step 5: Delete the file
    case: Case = file_operations_schema.find_operation_by_id('DeleteBaseAsset') \
        .Case(query={'path': file_path})
    response = case.call(headers=_api_headers(base))
    assert response.status_code == 200
    assert response.json()['success'] is True


def test_upload_image(base: Base):
    """Upload an image and attach it to a row."""
    create_table(base, TABLE, COLUMNS)

    # Step 1: Get upload link
    case: Case = file_operations_schema.find_operation_by_id('getUploadLink') \
        .Case()
    response = case.call(headers=_api_headers(base))
    assert response.status_code == 200

    upload_data = response.json()
    upload_link = upload_data['upload_link']
    parent_path = upload_data['parent_path']
    img_relative_path = upload_data['img_relative_path']
    workspace_id = base.workspace_id

    # Step 2: Upload a minimal 1x1 PNG
    # Smallest valid PNG: 1x1 pixel, red
    png_bytes = (
        b'\x89PNG\r\n\x1a\n'  # PNG signature
        b'\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x02\x00\x00\x00\x90wS\xde'
        b'\x00\x00\x00\x0cIDATx'
        b'\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05'
        b'\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    files = {'file': ('test-image.png', io.BytesIO(png_bytes), 'image/png')}
    form_data = {
        'parent_dir': parent_path,
        'relative_path': img_relative_path,
        'replace': '0',
    }

    upload_response = requests.post(
        f'{upload_link}?ret-json=1',
        headers=_api_headers(base),
        files=files,
        data=form_data,
    )
    assert upload_response.status_code == 200
    uploaded = upload_response.json()
    assert uploaded[0]['name'] == 'test-image.png'

    # Step 3: Attach image to a row via appendRows
    image_url = f'/workspace/{workspace_id}{parent_path}/{img_relative_path}/test-image.png'
    rows = [{'Name': 'With Image', 'Image': [image_url]}]
    append_rows(base, TABLE, rows)

    # Step 4: Verify the row has the image
    sql = f"SELECT Name, Image FROM {TABLE} WHERE Name = 'With Image'"
    body = {'sql': sql, 'convert_keys': True}
    path_parameters = {'base_uuid': base.uuid}
    headers = _base_headers(base)
    case: Case = base_operations_schema.find_operation_by_id('querySQL') \
        .Case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()
    assert response.status_code == 200
    results = response.json()['results']
    assert len(results) == 1
    assert len(results[0]['Image']) == 1
    assert 'test-image.png' in results[0]['Image'][0]


def test_download_link_nonexistent_file(base: Base):
    """Requesting download link for non-existent file returns an error."""
    case: Case = file_operations_schema.find_operation_by_id('getFileDownloadLink') \
        .Case(query={'path': '/files/2020-01/nonexistent.txt'})
    response = case.call(headers=_api_headers(base))

    assert response.status_code == 400


def test_delete_nonexistent_file(base: Base):
    """Deleting a non-existent file returns an error."""
    case: Case = file_operations_schema.find_operation_by_id('DeleteBaseAsset') \
        .Case(query={'path': '/files/2020-01/nonexistent.txt'})
    response = case.call(headers=_api_headers(base))

    assert response.status_code == 404
