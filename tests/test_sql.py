from conftest import Base, base_operations_schema, normalize
from schemathesis import Case

from test_base_operations import create_table, append_rows


TABLE = 'test_sql'
COLUMNS = [
    {'column_name': 'name', 'column_type': 'text'},
    {'column_name': 'age', 'column_type': 'number'},
    {'column_name': 'city', 'column_type': 'text'},
]
ROWS = [
    {'name': 'Alice', 'age': 30, 'city': 'Berlin'},
    {'name': 'Bob', 'age': 25, 'city': 'Munich'},
    {'name': 'Charlie', 'age': 35, 'city': 'Berlin'},
    {'name': 'Diana', 'age': 28, 'city': 'Hamburg'},
]


def _sql(base: Base, sql: str) -> dict:
    path_parameters = {'base_uuid': base.uuid}
    body = {'sql': sql, 'convert_keys': True}
    headers = {'Authorization': f'Bearer {base.token}'}
    case: Case = base_operations_schema.get_operation_by_id('querySQL') \
        .make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()
    assert response.status_code == 200
    return response.json()


def _setup(base: Base):
    create_table(base, TABLE, COLUMNS)
    append_rows(base, TABLE, ROWS)


def test_sql_select_all(base: Base):
    _setup(base)
    data = _sql(base, f'SELECT * FROM {TABLE}')

    assert len(data['results']) == 4
    names = [r['name'] for r in data['results']]
    assert set(names) == {'Alice', 'Bob', 'Charlie', 'Diana'}


def test_sql_where(base: Base):
    data = _sql(base, f"SELECT name, age FROM {TABLE} WHERE city = 'Berlin'")

    assert len(data['results']) == 2
    names = {r['name'] for r in data['results']}
    assert names == {'Alice', 'Charlie'}


def test_sql_where_greater_than(base: Base):
    data = _sql(base, f'SELECT name FROM {TABLE} WHERE age > 28')

    names = {r['name'] for r in data['results']}
    assert names == {'Alice', 'Charlie'}


def test_sql_order_by(base: Base):
    data = _sql(base, f'SELECT name, age FROM {TABLE} ORDER BY age ASC')

    ages = [r['age'] for r in data['results']]
    assert ages == [25, 28, 30, 35]


def test_sql_order_by_desc(base: Base):
    data = _sql(base, f'SELECT name FROM {TABLE} ORDER BY age DESC')

    names = [r['name'] for r in data['results']]
    assert names == ['Charlie', 'Alice', 'Diana', 'Bob']


def test_sql_limit(base: Base):
    data = _sql(base, f'SELECT name FROM {TABLE} LIMIT 2')

    assert len(data['results']) == 2


def test_sql_count(base: Base):
    data = _sql(base, f"SELECT COUNT(*) FROM {TABLE}")

    assert data['results'][0]['COUNT(*)'] == 4


def test_sql_count_where(base: Base):
    data = _sql(base, f"SELECT COUNT(*) FROM {TABLE} WHERE city = 'Berlin'")

    assert data['results'][0]['COUNT(*)'] == 2


def test_sql_group_by(base: Base):
    data = _sql(base, f'SELECT city, COUNT(*) FROM {TABLE} GROUP BY city')

    city_counts = {r['city']: r['COUNT(*)'] for r in data['results']}
    assert city_counts['Berlin'] == 2
    assert city_counts['Munich'] == 1
    assert city_counts['Hamburg'] == 1


def test_sql_sum(base: Base):
    data = _sql(base, f'SELECT SUM(age) FROM {TABLE}')

    assert data['results'][0]['SUM(age)'] == 118


def test_sql_min_max(base: Base):
    data = _sql(base, f'SELECT MIN(age), MAX(age) FROM {TABLE}')

    assert data['results'][0]['MIN(age)'] == 25
    assert data['results'][0]['MAX(age)'] == 35


def test_sql_distinct(base: Base):
    data = _sql(base, f'SELECT DISTINCT city FROM {TABLE} ORDER BY city')

    cities = [r['city'] for r in data['results']]
    assert cities == ['Berlin', 'Hamburg', 'Munich']


def test_sql_like(base: Base):
    data = _sql(base, f"SELECT name FROM {TABLE} WHERE name LIKE 'A%'")

    assert len(data['results']) == 1
    assert data['results'][0]['name'] == 'Alice'


def test_sql_invalid_table(base: Base):
    """Query a non-existing table returns an error."""
    path_parameters = {'base_uuid': base.uuid}
    body = {'sql': 'SELECT * FROM nonexistent_table', 'convert_keys': True}
    headers = {'Authorization': f'Bearer {base.token}'}
    case: Case = base_operations_schema.get_operation_by_id('querySQL') \
        .make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 400


def test_sql_invalid_syntax(base: Base):
    """Invalid SQL syntax returns an error."""
    path_parameters = {'base_uuid': base.uuid}
    body = {'sql': 'SELEC * FORM test', 'convert_keys': True}
    headers = {'Authorization': f'Bearer {base.token}'}
    case: Case = base_operations_schema.get_operation_by_id('querySQL') \
        .make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 400
