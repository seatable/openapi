import pytest
from conftest import Base, base_operations_schema
from schemathesis import Case

from test_base_operations import create_table, append_rows


# Table with writable + read-only columns for all tests
COLUMNS = [
    {'column_name': 'text', 'column_type': 'text'},
    {'column_name': 'number', 'column_type': 'number'},
    {
        'column_name': 'formula-int',
        'column_type': 'formula',
        'column_data': {'formula': '1 + 2'},
    },
    {
        'column_name': 'formula-text',
        'column_type': 'formula',
        'column_data': {'formula': 'concatenate({text}, " suffix")'},
    },
    {
        'column_name': 'auto-number',
        'column_type': 'auto-number',
        'column_data': {'format': '0000', 'digits': 4},
    },
]


def _get_row(base: Base, table_name: str, row_id: str) -> dict:
    """Read back a single row with convert_keys=True."""
    path_parameters = {'base_uuid': base.uuid, 'row_id': row_id}
    query = {'table_name': table_name, 'convert_keys': True}
    headers = {'Authorization': f'Bearer {base.token}'}
    case: Case = base_operations_schema.get_operation_by_id('getRow') \
        .make_case(path_parameters=path_parameters, query=query, headers=headers)
    response = case.call()
    assert response.status_code == 200
    return response.json()


def _append_row(base: Base, table_name: str, row: dict) -> dict:
    """Append a single row and return the full row read back via getRow."""
    path_parameters = {'base_uuid': base.uuid}
    body = {'table_name': table_name, 'rows': [row]}
    headers = {'Authorization': f'Bearer {base.token}'}
    case: Case = base_operations_schema.get_operation_by_id('appendRows') \
        .make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()
    assert response.status_code == 200
    row_id = response.json()['row_ids'][0]['_id']
    return _get_row(base, table_name, row_id)


def _update_row(base: Base, table_name: str, row_id: str, row_data: dict):
    """Update a single row and assert 200."""
    path_parameters = {'base_uuid': base.uuid}
    body = {
        'table_name': table_name,
        'updates': [{'row_id': row_id, 'row': row_data}],
    }
    headers = {'Authorization': f'Bearer {base.token}'}
    case: Case = base_operations_schema.get_operation_by_id('updateRow') \
        .make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Append: read-only columns should ignore provided values
# ---------------------------------------------------------------------------

class TestAppendReadonly:

    def test_formula_ignored(self, base: Base):
        """Formula columns compute their value — provided values are ignored."""
        table_name = 'test_append_ro_formula'
        create_table(base, table_name, COLUMNS)

        row = _append_row(base, table_name, {
            'text': 'hello', 'formula-int': 999, 'formula-text': 'fake',
        })

        assert row['formula-int'] == 3, 'formula-int should be computed (1+2=3), not 999'
        assert row['formula-text'] == 'hello suffix', 'formula-text should be computed, not "fake"'

    @pytest.mark.xfail(reason='API issue #4/#7: auto-number is overwritable via append')
    def test_auto_number_ignored(self, base: Base):
        """Auto-number should be assigned automatically — provided values should be ignored."""
        table_name = 'test_append_ro_autonum'
        create_table(base, table_name, COLUMNS)

        # Insert first row to establish sequence (gets 0001)
        append_rows(base, table_name, [{'text': 'first'}])

        # Try to override auto-number
        row = _append_row(base, table_name, {'text': 'second', 'auto-number': '9999'})

        assert row['auto-number'] == '0002', \
            'auto-number should be auto-assigned 0002, not accept provided 9999'

    def test_ctime_ignored(self, base: Base):
        """System column _ctime cannot be set via append."""
        table_name = 'test_append_ro_ctime'
        create_table(base, table_name, COLUMNS)

        row = _append_row(base, table_name, {
            'text': 'test', '_ctime': '2000-01-01T00:00:00.000+00:00',
        })

        assert '2000' not in row['_ctime'], '_ctime should not be overwritten'

    def test_creator_ignored(self, base: Base):
        """System column _creator cannot be set via append."""
        table_name = 'test_append_ro_creator'
        create_table(base, table_name, COLUMNS)

        row = _append_row(base, table_name, {
            'text': 'test', '_creator': 'fake@example.com',
        })

        assert row['_creator'] != 'fake@example.com', '_creator should not be overwritten'

    def test_mtime_ignored(self, base: Base):
        """System column _mtime cannot be set via append."""
        table_name = 'test_append_ro_mtime'
        create_table(base, table_name, COLUMNS)

        row = _append_row(base, table_name, {
            'text': 'test', '_mtime': '2000-01-01T00:00:00.000+00:00',
        })

        assert '2000' not in row['_mtime'], '_mtime should not be overwritten'

    def test_last_modifier_ignored(self, base: Base):
        """System column _last_modifier cannot be set via append."""
        table_name = 'test_append_ro_lastmod'
        create_table(base, table_name, COLUMNS)

        row = _append_row(base, table_name, {
            'text': 'test', '_last_modifier': 'fake@example.com',
        })

        assert row['_last_modifier'] != 'fake@example.com', '_last_modifier should not be overwritten'


# ---------------------------------------------------------------------------
# Update: read-only columns should ignore provided values
# ---------------------------------------------------------------------------

class TestUpdateReadonly:

    def test_formula_ignored(self, base: Base):
        """Formula columns cannot be changed via update."""
        table_name = 'test_update_ro_formula'
        create_table(base, table_name, COLUMNS)
        row_id = append_rows(base, table_name, [{'text': 'original', 'number': 1}])[0]

        row_before = _get_row(base, table_name, row_id)
        _update_row(base, table_name, row_id, {'formula-int': 999, 'formula-text': 'fake'})
        row_after = _get_row(base, table_name, row_id)

        assert row_after['formula-int'] == row_before['formula-int'], 'formula-int should not change'
        assert row_after['formula-text'] == row_before['formula-text'], 'formula-text should not change'

    @pytest.mark.xfail(reason='API issue #4/#7: auto-number is overwritable via update')
    def test_auto_number_ignored(self, base: Base):
        """Auto-number should not be changeable via update."""
        table_name = 'test_update_ro_autonum'
        create_table(base, table_name, COLUMNS)
        row_id = append_rows(base, table_name, [{'text': 'original'}])[0]

        row_before = _get_row(base, table_name, row_id)
        _update_row(base, table_name, row_id, {'auto-number': '9999'})
        row_after = _get_row(base, table_name, row_id)

        assert row_after['auto-number'] == row_before['auto-number'], \
            'auto-number should not change on update'

    def test_ctime_ignored(self, base: Base):
        """System column _ctime cannot be changed via update."""
        table_name = 'test_update_ro_ctime'
        create_table(base, table_name, COLUMNS)
        row_id = append_rows(base, table_name, [{'text': 'original'}])[0]

        row_before = _get_row(base, table_name, row_id)
        _update_row(base, table_name, row_id, {'_ctime': '2000-01-01T00:00:00.000+00:00'})
        row_after = _get_row(base, table_name, row_id)

        assert row_after['_ctime'] == row_before['_ctime'], '_ctime should not change'

    def test_creator_ignored(self, base: Base):
        """System column _creator cannot be changed via update."""
        table_name = 'test_update_ro_creator'
        create_table(base, table_name, COLUMNS)
        row_id = append_rows(base, table_name, [{'text': 'original'}])[0]

        row_before = _get_row(base, table_name, row_id)
        _update_row(base, table_name, row_id, {'_creator': 'fake@example.com'})
        row_after = _get_row(base, table_name, row_id)

        assert row_after['_creator'] == row_before['_creator'], '_creator should not change'

    def test_mtime_ignored(self, base: Base):
        """System column _mtime cannot be overwritten with an arbitrary value."""
        table_name = 'test_update_ro_mtime'
        create_table(base, table_name, COLUMNS)
        row_id = append_rows(base, table_name, [{'text': 'original'}])[0]

        _update_row(base, table_name, row_id, {'_mtime': '2000-01-01T00:00:00.000+00:00'})
        row_after = _get_row(base, table_name, row_id)

        assert '2000' not in row_after['_mtime'], '_mtime should not be overwritten'

    def test_last_modifier_ignored(self, base: Base):
        """System column _last_modifier cannot be changed via update."""
        table_name = 'test_update_ro_lastmod'
        create_table(base, table_name, COLUMNS)
        row_id = append_rows(base, table_name, [{'text': 'original'}])[0]

        _update_row(base, table_name, row_id, {'_last_modifier': 'fake@example.com'})
        row_after = _get_row(base, table_name, row_id)

        assert row_after['_last_modifier'] != 'fake@example.com', '_last_modifier should not be overwritten'
