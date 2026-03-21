"""Systematic tests for SeaTable SQL functions.

Tests all functions documented in the developer docs (docs/sql/functions.md)
and verifies that common MySQL equivalents are NOT supported.

This helps ensure:
1. Documentation accuracy — every documented function actually works
2. LLM prompt accuracy — we know exactly which functions to recommend/forbid
"""

import pytest
import requests
from conftest import Base, BASE_URL, base_operations_schema
from schemathesis import Case

from test_base_operations import create_table, append_rows


# ---------------------------------------------------------------------------
# Test data setup
# ---------------------------------------------------------------------------

TABLE = 'test_sql_functions'
COLUMNS = [
    {'column_name': 'name', 'column_type': 'text'},
    {'column_name': 'age', 'column_type': 'number'},
    {'column_name': 'city', 'column_type': 'text'},
    {'column_name': 'birthday', 'column_type': 'date', 'column_data': {'format': 'YYYY-MM-DD'}},
    {'column_name': 'score', 'column_type': 'number'},
]
ROWS = [
    {'name': 'Alice', 'age': 30, 'city': 'Berlin', 'birthday': '2000-03-15', 'score': 85.5},
    {'name': 'Bob', 'age': 25, 'city': 'Munich', 'birthday': '1998-07-22', 'score': 92.3},
    {'name': 'Charlie', 'age': 35, 'city': 'Berlin', 'birthday': '1990-12-01', 'score': 78.0},
    {'name': 'Diana', 'age': 28, 'city': 'Hamburg', 'birthday': '1995-01-30', 'score': 0},
]

_setup_done = False


def _sql(base: Base, sql: str) -> dict:
    """Execute SQL and assert 200."""
    path_parameters = {'base_uuid': base.uuid}
    body = {'sql': sql, 'convert_keys': True}
    headers = {'Authorization': f'Bearer {base.token}'}
    case: Case = base_operations_schema.find_operation_by_id('querySQL') \
        .Case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()
    assert response.status_code == 200, f"SQL failed ({response.status_code}): {response.text}\nQuery: {sql}"
    return response.json()


def _sql_error(base: Base, sql: str) -> int:
    """Execute SQL and return the status code (expecting non-200)."""
    path_parameters = {'base_uuid': base.uuid}
    body = {'sql': sql, 'convert_keys': True}
    headers = {'Authorization': f'Bearer {base.token}'}
    case: Case = base_operations_schema.find_operation_by_id('querySQL') \
        .Case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()
    return response.status_code


def _sql_write(base: Base, sql: str) -> dict:
    """Execute a write SQL (INSERT/UPDATE/DELETE) using requests directly.
    Bypasses the schemathesis after_call hook which rejects metadata:null responses.
    """
    url = f'{BASE_URL}/api-gateway/api/v2/dtables/{base.uuid}/sql/'
    headers = {'Authorization': f'Bearer {base.token}'}
    r = requests.post(url, json={'sql': sql, 'convert_keys': True}, headers=headers)
    assert r.status_code == 200, f"SQL write failed ({r.status_code}): {r.text}\nQuery: {sql}"
    return r.json()


def _sql_write_status(base: Base, sql: str) -> int:
    """Execute a write SQL and return the status code."""
    url = f'{BASE_URL}/api-gateway/api/v2/dtables/{base.uuid}/sql/'
    headers = {'Authorization': f'Bearer {base.token}'}
    r = requests.post(url, json={'sql': sql, 'convert_keys': True}, headers=headers)
    return r.status_code


def _val(data: dict):
    """Extract the single value from a single-row, single-column result."""
    return list(data['results'][0].values())[0]


def _setup(base: Base):
    global _setup_done
    if not _setup_done:
        create_table(base, TABLE, COLUMNS)
        append_rows(base, TABLE, ROWS)
        _setup_done = True


# ===================================================================
# TEXT FUNCTIONS
# ===================================================================

class TestTextFunctions:

    def test_concatenate(self, base: Base):
        _setup(base)
        data = _sql(base, f"SELECT concatenate(`name`, ' from ', `city`) FROM `{TABLE}` WHERE `name` = 'Alice'")
        assert _val(data) == 'Alice from Berlin'

    def test_exact_true(self, base: Base):
        data = _sql(base, f"SELECT exact(`name`, 'Alice') FROM `{TABLE}` WHERE `name` = 'Alice'")
        assert _val(data) is True

    def test_exact_false(self, base: Base):
        data = _sql(base, f"SELECT exact(`name`, 'alice') FROM `{TABLE}` WHERE `name` = 'Alice'")
        assert _val(data) is False

    def test_find(self, base: Base):
        data = _sql(base, f"SELECT find('li', `name`) FROM `{TABLE}` WHERE `name` = 'Alice'")
        assert _val(data) == 2

    def test_find_not_found(self, base: Base):
        data = _sql(base, f"SELECT find('xyz', `name`) FROM `{TABLE}` WHERE `name` = 'Alice'")
        # Docs say 0, but SeaTable may return None/empty for not found
        result = _val(data)
        assert result == 0 or result is None or result == ''

    def test_left(self, base: Base):
        data = _sql(base, f"SELECT left(`name`, 3) FROM `{TABLE}` WHERE `name` = 'Alice'")
        assert _val(data) == 'Ali'

    def test_len(self, base: Base):
        data = _sql(base, f"SELECT len(`name`) FROM `{TABLE}` WHERE `name` = 'Alice'")
        assert _val(data) == 5

    def test_lower(self, base: Base):
        data = _sql(base, f"SELECT lower(`name`) FROM `{TABLE}` WHERE `name` = 'Alice'")
        assert _val(data) == 'alice'

    def test_mid(self, base: Base):
        data = _sql(base, f"SELECT mid(`name`, 1, 3) FROM `{TABLE}` WHERE `name` = 'Alice'")
        assert _val(data) == 'Ali'

    def test_mid_from_middle(self, base: Base):
        data = _sql(base, f"SELECT mid(`name`, 3, 2) FROM `{TABLE}` WHERE `name` = 'Alice'")
        assert _val(data) == 'ic'

    def test_replace(self, base: Base):
        data = _sql(base, f"SELECT replace(`name`, 1, 3, 'Oli') FROM `{TABLE}` WHERE `name` = 'Alice'")
        assert _val(data) == 'Olice'

    def test_rept(self, base: Base):
        data = _sql(base, f"SELECT rept('ab', 3) FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 'ababab'

    def test_right(self, base: Base):
        data = _sql(base, f"SELECT right(`name`, 3) FROM `{TABLE}` WHERE `name` = 'Alice'")
        assert _val(data) == 'ice'

    def test_search_case_insensitive(self, base: Base):
        data = _sql(base, f"SELECT search('LI', `name`) FROM `{TABLE}` WHERE `name` = 'Alice'")
        assert _val(data) == 2

    def test_substitute(self, base: Base):
        data = _sql(base, f"SELECT substitute(`city`, 'Berlin', 'Bonn') FROM `{TABLE}` WHERE `name` = 'Alice'")
        assert _val(data) == 'Bonn'

    def test_t_with_text(self, base: Base):
        data = _sql(base, f"SELECT T(`name`) FROM `{TABLE}` WHERE `name` = 'Alice'")
        assert _val(data) == 'Alice'

    def test_trim(self, base: Base):
        data = _sql(base, f"SELECT trim('  hello  ') FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 'hello'

    def test_upper(self, base: Base):
        data = _sql(base, f"SELECT upper(`name`) FROM `{TABLE}` WHERE `name` = 'Alice'")
        assert _val(data) == 'ALICE'

    def test_value(self, base: Base):
        data = _sql(base, f"SELECT value('123') FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 123


# ===================================================================
# MATHEMATICAL FUNCTIONS
# ===================================================================

class TestMathFunctions:

    def test_abs(self, base: Base):
        _setup(base)
        data = _sql(base, f"SELECT abs(-5) FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 5

    def test_ceiling(self, base: Base):
        data = _sql(base, f"SELECT ceiling(2.14) FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 3

    def test_even(self, base: Base):
        data = _sql(base, f"SELECT even(3) FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 4

    def test_exp(self, base: Base):
        data = _sql(base, f"SELECT exp(1) FROM `{TABLE}` LIMIT 1")
        result = _val(data)
        assert abs(result - 2.71828) < 0.001

    def test_floor(self, base: Base):
        data = _sql(base, f"SELECT floor(2.86) FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 2

    def test_int(self, base: Base):
        data = _sql(base, f"SELECT int(3.14) FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 3

    def test_lg(self, base: Base):
        data = _sql(base, f"SELECT lg(100) FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 2

    def test_log(self, base: Base):
        data = _sql(base, f"SELECT log(81, 3) FROM `{TABLE}` LIMIT 1")
        assert abs(_val(data) - 4) < 0.0001

    def test_mod(self, base: Base):
        data = _sql(base, f"SELECT mod(15, 7) FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 1

    def test_odd(self, base: Base):
        data = _sql(base, f"SELECT odd(2) FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 3

    def test_power(self, base: Base):
        data = _sql(base, f"SELECT power(3, 2) FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 9

    def test_round(self, base: Base):
        data = _sql(base, f"SELECT round(3.14) FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 3

    def test_round_digits(self, base: Base):
        data = _sql(base, f"SELECT round(3.14, 1) FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 3.1

    def test_rounddown(self, base: Base):
        data = _sql(base, f"SELECT rounddown(3.19, 1) FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 3.1

    def test_roundup(self, base: Base):
        data = _sql(base, f"SELECT roundup(3.11, 1) FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 3.2

    def test_sign_positive(self, base: Base):
        data = _sql(base, f"SELECT sign(5) FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 1

    def test_sign_negative(self, base: Base):
        data = _sql(base, f"SELECT sign(-5) FROM `{TABLE}` LIMIT 1")
        assert _val(data) == -1

    def test_sqrt(self, base: Base):
        data = _sql(base, f"SELECT sqrt(81) FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 9

    def test_add(self, base: Base):
        data = _sql(base, f"SELECT add(1, 2) FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 3

    def test_subtract(self, base: Base):
        """Docs say 'substract' (typo), but actual function name is 'subtract'."""
        data = _sql(base, f"SELECT subtract(5, 3) FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 2

    def test_substract_not_supported(self, base: Base):
        """The documented spelling 'substract' does NOT work — it's a doc typo."""
        assert _sql_error(base, f"SELECT substract(5, 3) FROM `{TABLE}` LIMIT 1") == 400

    def test_multiply(self, base: Base):
        data = _sql(base, f"SELECT multiply(3, 4) FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 12

    def test_divide(self, base: Base):
        data = _sql(base, f"SELECT divide(10, 4) FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 2.5

    def test_greater(self, base: Base):
        data = _sql(base, f"SELECT greater(5, 3) FROM `{TABLE}` LIMIT 1")
        assert _val(data) is True

    def test_lessthan(self, base: Base):
        data = _sql(base, f"SELECT lessthan(2, 3) FROM `{TABLE}` LIMIT 1")
        assert _val(data) is True

    def test_greatereq(self, base: Base):
        data = _sql(base, f"SELECT greatereq(3, 3) FROM `{TABLE}` LIMIT 1")
        assert _val(data) is True

    def test_lessthaneq(self, base: Base):
        data = _sql(base, f"SELECT lessthaneq(3, 3) FROM `{TABLE}` LIMIT 1")
        assert _val(data) is True

    def test_equal(self, base: Base):
        data = _sql(base, f"SELECT equal(3, 3) FROM `{TABLE}` LIMIT 1")
        assert _val(data) is True

    def test_unequal(self, base: Base):
        data = _sql(base, f"SELECT unequal(3, 4) FROM `{TABLE}` LIMIT 1")
        assert _val(data) is True


# ===================================================================
# DATE FUNCTIONS
# ===================================================================

class TestDateFunctions:

    def test_date(self, base: Base):
        _setup(base)
        data = _sql(base, f"SELECT date(2025, 1, 3) FROM `{TABLE}` LIMIT 1")
        result = _val(data)
        assert '2025-01-03' in result

    def test_year(self, base: Base):
        data = _sql(base, f"SELECT year(`birthday`) FROM `{TABLE}` WHERE `name` = 'Alice'")
        assert _val(data) == 2000

    def test_month(self, base: Base):
        data = _sql(base, f"SELECT month(`birthday`) FROM `{TABLE}` WHERE `name` = 'Alice'")
        assert _val(data) == 3

    def test_day(self, base: Base):
        data = _sql(base, f"SELECT day(`birthday`) FROM `{TABLE}` WHERE `name` = 'Alice'")
        assert _val(data) == 15

    def test_hour(self, base: Base):
        data = _sql(base, f"SELECT hour('2025-02-14 13:14:52') FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 13

    def test_minute(self, base: Base):
        data = _sql(base, f"SELECT minute('2025-02-14 13:14:52') FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 14

    def test_second(self, base: Base):
        data = _sql(base, f"SELECT second('2025-02-14 13:14:52') FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 52

    def test_dateAdd(self, base: Base):
        data = _sql(base, f"SELECT dateAdd('2024-02-03', 2, 'days') FROM `{TABLE}` LIMIT 1")
        result = _val(data)
        assert '2024-02-05' in result

    def test_dateDif(self, base: Base):
        data = _sql(base, f"SELECT dateDif('2023-01-01', '2025-01-01', 'Y') FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 2

    def test_now(self, base: Base):
        data = _sql(base, f"SELECT now() FROM `{TABLE}` LIMIT 1")
        result = _val(data)
        assert '2026' in result or '2025' in result  # just check it returns a date string

    def test_today(self, base: Base):
        data = _sql(base, f"SELECT today() FROM `{TABLE}` LIMIT 1")
        result = _val(data)
        assert 'T00:00:00' in result or '2026' in result or '2025' in result

    def test_weekday(self, base: Base):
        data = _sql(base, f"SELECT weekday('2025-01-01', 'Monday') FROM `{TABLE}` LIMIT 1")
        result = _val(data)
        assert isinstance(result, int)
        assert 1 <= result <= 7

    def test_weeknum(self, base: Base):
        data = _sql(base, f"SELECT weeknum('2025-01-12', 11) FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 2

    def test_eomonth(self, base: Base):
        data = _sql(base, f"SELECT eomonth('2025-01-01', 1) FROM `{TABLE}` LIMIT 1")
        result = _val(data)
        assert '2025-02-28' in result

    def test_quarter(self, base: Base):
        data = _sql(base, f"SELECT quarter('2025-04-15') FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 2

    def test_isodate(self, base: Base):
        data = _sql(base, f"SELECT isodate('2025-01-01 11:00:00') FROM `{TABLE}` LIMIT 1")
        assert _val(data) == '2025-01-01'

    def test_isomonth(self, base: Base):
        data = _sql(base, f"SELECT isomonth('2025-01-01 11:00:00') FROM `{TABLE}` LIMIT 1")
        assert _val(data) == '2025-01'

    def test_hours_not_supported_in_sql(self, base: Base):
        """hours() is documented in functions.md but NOT supported in SQL queries."""
        assert _sql_error(base, f"SELECT hours('2025-02-14 13:00', '2025-02-14 15:00') FROM `{TABLE}` LIMIT 1") == 400

    def test_months(self, base: Base):
        data = _sql(base, f"SELECT months('2025-02-01', '2025-05-01') FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 3

    def test_networkdays(self, base: Base):
        data = _sql(base, f"SELECT networkdays('2025-09-08', '2025-09-10') FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 3

    def test_startofweek(self, base: Base):
        data = _sql(base, f"SELECT startofweek('2025-04-28') FROM `{TABLE}` LIMIT 1")
        result = _val(data)
        assert '2025-04-27' in result or '2025-4-27' in result

    def test_isoweeknum(self, base: Base):
        """isoweeknum is mentioned as alternative to weeknum with return_type=21."""
        data = _sql(base, f"SELECT weeknum('2025-01-12', 21) FROM `{TABLE}` LIMIT 1")
        result = _val(data)
        assert isinstance(result, int)


# ===================================================================
# LOGICAL FUNCTIONS
# ===================================================================

class TestLogicalFunctions:

    def test_if_true(self, base: Base):
        _setup(base)
        data = _sql(base, f"SELECT if(`age` > 28, 'old', 'young') FROM `{TABLE}` WHERE `name` = 'Alice'")
        assert _val(data) == 'old'

    def test_if_false(self, base: Base):
        data = _sql(base, f"SELECT if(`age` > 28, 'old', 'young') FROM `{TABLE}` WHERE `name` = 'Bob'")
        assert _val(data) == 'young'

    def test_ifs(self, base: Base):
        data = _sql(base, f"SELECT ifs(`age` > 30, 'senior', `age` > 25, 'mid', true, 'junior') FROM `{TABLE}` WHERE `name` = 'Charlie'")
        assert _val(data) == 'senior'

    def test_and(self, base: Base):
        data = _sql(base, f"SELECT and(`age` > 20, `age` < 40) FROM `{TABLE}` WHERE `name` = 'Alice'")
        assert _val(data) is True

    def test_or(self, base: Base):
        data = _sql(base, f"SELECT or(`age` > 50, `age` < 26) FROM `{TABLE}` WHERE `name` = 'Bob'")
        assert _val(data) is True

    def test_not(self, base: Base):
        data = _sql(base, f"SELECT not(`age` > 50) FROM `{TABLE}` WHERE `name` = 'Alice'")
        assert _val(data) is True

    def test_switch(self, base: Base):
        data = _sql(base, f"SELECT switch(`city`, 'Berlin', 'DE-BE', 'Munich', 'DE-BY', 'unknown') FROM `{TABLE}` WHERE `name` = 'Alice'")
        assert _val(data) == 'DE-BE'

    def test_xor(self, base: Base):
        data = _sql(base, f"SELECT xor(1, 0) FROM `{TABLE}` LIMIT 1")
        assert _val(data) is True


# ===================================================================
# STATISTICAL FUNCTIONS
# ===================================================================

class TestStatisticalFunctions:

    def test_average(self, base: Base):
        _setup(base)
        data = _sql(base, f"SELECT average(1, 2, 3, 4, 5) FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 3

    def test_counta(self, base: Base):
        data = _sql(base, f"SELECT counta(1, '', 2, '3') FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 3

    def test_countall(self, base: Base):
        data = _sql(base, f"SELECT countall(1, '', 2, '3') FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 4

    def test_countblank(self, base: Base):
        data = _sql(base, f"SELECT countblank(1, '', 2, '3') FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 1


# ===================================================================
# CONSTANTS
# ===================================================================

class TestConstants:
    """Constants pi, e, true, false work only inside functions, not standalone in SELECT."""

    def test_pi_standalone_not_supported(self, base: Base):
        """'SELECT pi' is interpreted as column name — constants only work inside functions."""
        _setup(base)
        assert _sql_error(base, f"SELECT pi FROM `{TABLE}` LIMIT 1") == 400

    def test_e_standalone_not_supported(self, base: Base):
        """'SELECT e' is interpreted as column name — constants only work inside functions."""
        assert _sql_error(base, f"SELECT e FROM `{TABLE}` LIMIT 1") == 400

    def test_pi_inside_function(self, base: Base):
        """pi works as argument inside a function."""
        data = _sql(base, f"SELECT multiply(pi, 2) FROM `{TABLE}` LIMIT 1")
        result = _val(data)
        assert abs(result - 6.28318) < 0.01

    def test_e_inside_function(self, base: Base):
        """e works as argument inside a function."""
        data = _sql(base, f"SELECT add(e, 1) FROM `{TABLE}` LIMIT 1")
        result = _val(data)
        assert abs(result - 3.71828) < 0.01


# ===================================================================
# AGGREGATE FUNCTIONS (COUNT, SUM, MIN, MAX, AVG — these are
# standard SQL and already tested in test_sql.py, but included
# here for completeness of the function matrix)
# ===================================================================

class TestAggregateFunctions:

    def test_count(self, base: Base):
        _setup(base)
        data = _sql(base, f"SELECT COUNT(*) FROM `{TABLE}`")
        assert data['results'][0]['COUNT(*)'] == 4

    def test_sum(self, base: Base):
        data = _sql(base, f"SELECT SUM(`age`) FROM `{TABLE}`")
        assert data['results'][0]['SUM(age)'] == 118

    def test_min(self, base: Base):
        data = _sql(base, f"SELECT MIN(`age`) FROM `{TABLE}`")
        assert data['results'][0]['MIN(age)'] == 25

    def test_max(self, base: Base):
        data = _sql(base, f"SELECT MAX(`age`) FROM `{TABLE}`")
        assert data['results'][0]['MAX(age)'] == 35


# ===================================================================
# MYSQL FUNCTIONS THAT SHOULD NOT WORK
# These verify that common MySQL functions are NOT supported,
# which is critical for LLM prompt engineering.
# ===================================================================

class TestMySQLFunctionsNotSupported:
    """Verify that standard MySQL functions return errors in SeaTable SQL."""

    def test_substr_not_supported(self, base: Base):
        """SUBSTR is the original error from the screenshot."""
        _setup(base)
        assert _sql_error(base, f"SELECT SUBSTR(`name`, 1, 2) FROM `{TABLE}`") == 400

    def test_substring_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT SUBSTRING(`name`, 1, 2) FROM `{TABLE}`") == 400

    def test_concat_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT CONCAT(`name`, ' ', `city`) FROM `{TABLE}`") == 400

    def test_length_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT LENGTH(`name`) FROM `{TABLE}`") == 400

    def test_char_length_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT CHAR_LENGTH(`name`) FROM `{TABLE}`") == 400

    def test_locate_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT LOCATE('li', `name`) FROM `{TABLE}`") == 400

    def test_instr_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT INSTR(`name`, 'li') FROM `{TABLE}`") == 400

    def test_lpad_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT LPAD(`name`, 10, '*') FROM `{TABLE}`") == 400

    def test_rpad_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT RPAD(`name`, 10, '*') FROM `{TABLE}`") == 400

    def test_reverse_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT REVERSE(`name`) FROM `{TABLE}`") == 400

    def test_repeat_not_supported(self, base: Base):
        """MySQL uses REPEAT, SeaTable uses rept."""
        assert _sql_error(base, f"SELECT REPEAT(`name`, 2) FROM `{TABLE}`") == 400

    def test_ucase_not_supported(self, base: Base):
        """MySQL alias for UPPER."""
        assert _sql_error(base, f"SELECT UCASE(`name`) FROM `{TABLE}`") == 400

    def test_lcase_not_supported(self, base: Base):
        """MySQL alias for LOWER."""
        assert _sql_error(base, f"SELECT LCASE(`name`) FROM `{TABLE}`") == 400

    def test_mysql_replace_not_supported(self, base: Base):
        """MySQL REPLACE(str, from, to) has different signature than SeaTable replace(str, pos, count, new)."""
        assert _sql_error(base, f"SELECT REPLACE(`name`, 'A', 'O') FROM `{TABLE}`") == 400

    # MySQL date functions
    def test_curdate_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT CURDATE() FROM `{TABLE}`") == 400

    def test_current_date_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT CURRENT_DATE() FROM `{TABLE}`") == 400

    def test_date_format_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT DATE_FORMAT(`birthday`, '%Y-%m') FROM `{TABLE}`") == 400

    def test_datediff_mysql_not_supported(self, base: Base):
        """MySQL DATEDIFF(d1, d2) vs SeaTable dateDif(d1, d2, unit)."""
        assert _sql_error(base, f"SELECT DATEDIFF('2025-01-01', '2024-01-01') FROM `{TABLE}`") == 400

    def test_date_add_mysql_not_supported(self, base: Base):
        """MySQL DATE_ADD with INTERVAL syntax."""
        assert _sql_error(base, f"SELECT DATE_ADD('2025-01-01', INTERVAL 1 DAY) FROM `{TABLE}`") == 400

    def test_date_sub_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT DATE_SUB('2025-01-01', INTERVAL 1 DAY) FROM `{TABLE}`") == 400

    def test_extract_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT EXTRACT(YEAR FROM `birthday`) FROM `{TABLE}`") == 400

    # MySQL math functions
    def test_ceil_not_supported(self, base: Base):
        """MySQL uses CEIL, SeaTable uses ceiling."""
        assert _sql_error(base, f"SELECT CEIL(2.14) FROM `{TABLE}`") == 400

    def test_truncate_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT TRUNCATE(3.14, 1) FROM `{TABLE}`") == 400

    def test_rand_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT RAND() FROM `{TABLE}`") == 400

    # MySQL logical
    def test_ifnull_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT IFNULL(`name`, 'unknown') FROM `{TABLE}`") == 400

    def test_coalesce_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT COALESCE(`name`, 'unknown') FROM `{TABLE}`") == 400

    def test_nullif_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT NULLIF(`name`, 'Alice') FROM `{TABLE}`") == 400

    def test_case_when_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT CASE WHEN `age` > 30 THEN 'old' ELSE 'young' END FROM `{TABLE}`") == 400

    # MySQL date functions with different names in SeaTable
    def test_dayofweek_not_supported(self, base: Base):
        """MySQL DAYOFWEEK() → SeaTable weekday()."""
        assert _sql_error(base, f"SELECT DAYOFWEEK(`birthday`) FROM `{TABLE}`") == 400

    def test_week_not_supported(self, base: Base):
        """MySQL WEEK() → SeaTable weeknum()."""
        assert _sql_error(base, f"SELECT WEEK(`birthday`) FROM `{TABLE}`") == 400

    def test_last_day_not_supported(self, base: Base):
        """MySQL LAST_DAY() → SeaTable eomonth()."""
        assert _sql_error(base, f"SELECT LAST_DAY(`birthday`) FROM `{TABLE}`") == 400

    # --- Additional common MySQL functions: supported or not? ---

    def test_timestampdiff_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT TIMESTAMPDIFF(DAY, '2024-01-01', '2025-01-01') FROM `{TABLE}` LIMIT 1") == 400

    def test_timestampadd_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT TIMESTAMPADD(DAY, 1, '2025-01-01') FROM `{TABLE}` LIMIT 1") == 400

    def test_dayofmonth_not_supported(self, base: Base):
        """MySQL DAYOFMONTH() → SeaTable day()."""
        assert _sql_error(base, f"SELECT DAYOFMONTH(`birthday`) FROM `{TABLE}` LIMIT 1") == 400

    def test_dayname_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT DAYNAME(`birthday`) FROM `{TABLE}` LIMIT 1") == 400

    def test_monthname_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT MONTHNAME(`birthday`) FROM `{TABLE}` LIMIT 1") == 400

    def test_cast_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT CAST(`age` AS CHAR) FROM `{TABLE}` LIMIT 1") == 400

    def test_convert_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT CONVERT(`age`, CHAR) FROM `{TABLE}` LIMIT 1") == 400

    def test_greatest_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT GREATEST(`age`, `score`) FROM `{TABLE}` LIMIT 1") == 400

    def test_least_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT LEAST(`age`, `score`) FROM `{TABLE}` LIMIT 1") == 400

    def test_log2_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT LOG2(8) FROM `{TABLE}` LIMIT 1") == 400

    def test_mysql_date_function_not_supported(self, base: Base):
        """MySQL DATE() extracts the date part from a datetime."""
        assert _sql_error(base, f"SELECT DATE(`birthday`) FROM `{TABLE}` LIMIT 1") == 400

    def test_str_to_date_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT STR_TO_DATE('01-01-2025', '%d-%m-%Y') FROM `{TABLE}` LIMIT 1") == 400

    # MySQL aggregate
    def test_group_concat_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT GROUP_CONCAT(`name`) FROM `{TABLE}`") == 400

    def test_avg_is_supported(self, base: Base):
        """AVG() IS supported as a standard SQL aggregate function (unlike most MySQL functions)."""
        _setup(base)
        data = _sql(base, f"SELECT AVG(`age`) FROM `{TABLE}`")
        assert data['results'][0]['AVG(age)'] == 29.5

    # MySQL string functions
    def test_concat_ws_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT CONCAT_WS(', ', `name`, `city`) FROM `{TABLE}`") == 400

    def test_format_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT FORMAT(`age`, 2) FROM `{TABLE}`") == 400


# ===================================================================
# SQL SYNTAX — WHERE OPERATORS
# ===================================================================

class TestWhereOperators:

    def test_where_equals(self, base: Base):
        _setup(base)
        data = _sql(base, f"SELECT `name` FROM `{TABLE}` WHERE `city` = 'Berlin'")
        names = {r['name'] for r in data['results']}
        assert names == {'Alice', 'Charlie'}

    def test_where_not_equals(self, base: Base):
        data = _sql(base, f"SELECT `name` FROM `{TABLE}` WHERE `city` != 'Berlin'")
        names = {r['name'] for r in data['results']}
        assert names == {'Bob', 'Diana'}

    def test_where_not_equals_angle_brackets(self, base: Base):
        data = _sql(base, f"SELECT `name` FROM `{TABLE}` WHERE `city` <> 'Berlin'")
        names = {r['name'] for r in data['results']}
        assert names == {'Bob', 'Diana'}

    def test_where_greater_than(self, base: Base):
        data = _sql(base, f"SELECT `name` FROM `{TABLE}` WHERE `age` > 30")
        names = {r['name'] for r in data['results']}
        assert names == {'Charlie'}

    def test_where_greater_equal(self, base: Base):
        data = _sql(base, f"SELECT `name` FROM `{TABLE}` WHERE `age` >= 30")
        names = {r['name'] for r in data['results']}
        assert names == {'Alice', 'Charlie'}

    def test_where_less_than(self, base: Base):
        data = _sql(base, f"SELECT `name` FROM `{TABLE}` WHERE `age` < 28")
        names = {r['name'] for r in data['results']}
        assert names == {'Bob'}

    def test_where_less_equal(self, base: Base):
        data = _sql(base, f"SELECT `name` FROM `{TABLE}` WHERE `age` <= 28")
        names = {r['name'] for r in data['results']}
        assert names == {'Bob', 'Diana'}

    def test_where_between(self, base: Base):
        data = _sql(base, f"SELECT `name` FROM `{TABLE}` WHERE `age` BETWEEN 26 AND 31")
        names = {r['name'] for r in data['results']}
        assert names == {'Alice', 'Diana'}

    def test_where_in(self, base: Base):
        data = _sql(base, f"SELECT `name` FROM `{TABLE}` WHERE `city` IN ('Berlin', 'Hamburg')")
        names = {r['name'] for r in data['results']}
        assert names == {'Alice', 'Charlie', 'Diana'}

    def test_where_not_in(self, base: Base):
        data = _sql(base, f"SELECT `name` FROM `{TABLE}` WHERE `city` NOT IN ('Berlin', 'Hamburg')")
        names = {r['name'] for r in data['results']}
        assert names == {'Bob'}

    def test_where_like_percent(self, base: Base):
        data = _sql(base, f"SELECT `name` FROM `{TABLE}` WHERE `name` LIKE 'A%'")
        assert len(data['results']) == 1
        assert data['results'][0]['name'] == 'Alice'

    def test_where_like_underscore(self, base: Base):
        data = _sql(base, f"SELECT `name` FROM `{TABLE}` WHERE `name` LIKE 'Bo_'")
        assert len(data['results']) == 1
        assert data['results'][0]['name'] == 'Bob'

    def test_where_and(self, base: Base):
        data = _sql(base, f"SELECT `name` FROM `{TABLE}` WHERE `city` = 'Berlin' AND `age` > 30")
        names = {r['name'] for r in data['results']}
        assert names == {'Charlie'}

    def test_where_or(self, base: Base):
        data = _sql(base, f"SELECT `name` FROM `{TABLE}` WHERE `city` = 'Munich' OR `city` = 'Hamburg'")
        names = {r['name'] for r in data['results']}
        assert names == {'Bob', 'Diana'}

    def test_where_function_in_where(self, base: Base):
        """Functions can be used in WHERE clauses."""
        data = _sql(base, f"SELECT `name` FROM `{TABLE}` WHERE left(`name`, 1) = 'A'")
        assert len(data['results']) == 1
        assert data['results'][0]['name'] == 'Alice'


# ===================================================================
# SQL SYNTAX — NULL HANDLING
# ===================================================================

TABLE_NULL = 'test_null_handling'
_null_setup_done = False


def _setup_null(base: Base):
    global _null_setup_done
    if not _null_setup_done:
        create_table(base, TABLE_NULL, [
            {'column_name': 'label', 'column_type': 'text'},
            {'column_name': 'value', 'column_type': 'number'},
            {'column_name': 'note', 'column_type': 'text'},
        ])
        append_rows(base, TABLE_NULL, [
            {'label': 'filled', 'value': 10, 'note': 'has note'},
            {'label': 'empty_note', 'value': 20},
            {'label': '', 'value': 0},
        ])
        _null_setup_done = True


class TestNullHandling:
    """Empty strings are treated as NULL in SeaTable SQL."""

    def test_is_null_for_empty_text(self, base: Base):
        _setup_null(base)
        data = _sql(base, f"SELECT `label` FROM `{TABLE_NULL}` WHERE `note` IS NULL")
        # The row with no note and the row with empty label should have note=NULL
        assert len(data['results']) >= 1

    def test_is_not_null(self, base: Base):
        data = _sql(base, f"SELECT `label` FROM `{TABLE_NULL}` WHERE `note` IS NOT NULL")
        labels = {r['label'] for r in data['results']}
        assert 'filled' in labels

    def test_empty_string_is_null(self, base: Base):
        """Empty label '' should be treated as NULL."""
        data = _sql(base, f"SELECT `value` FROM `{TABLE_NULL}` WHERE `label` IS NULL")
        assert len(data['results']) >= 1


# ===================================================================
# SQL SYNTAX — GROUP BY, HAVING, ALIASES
# ===================================================================

class TestGroupByHavingAliases:

    def test_group_by(self, base: Base):
        _setup(base)
        data = _sql(base, f"SELECT `city`, COUNT(*) FROM `{TABLE}` GROUP BY `city`")
        city_counts = {r['city']: r['COUNT(*)'] for r in data['results']}
        assert city_counts['Berlin'] == 2

    def test_group_by_having(self, base: Base):
        data = _sql(base, f"SELECT `city`, COUNT(*) FROM `{TABLE}` GROUP BY `city` HAVING COUNT(*) > 1")
        assert len(data['results']) == 1
        assert data['results'][0]['city'] == 'Berlin'

    def test_alias_column(self, base: Base):
        data = _sql(base, f"SELECT `name` AS `full_name` FROM `{TABLE}` WHERE `name` = 'Alice'")
        assert data['results'][0]['full_name'] == 'Alice'

    def test_alias_function(self, base: Base):
        data = _sql(base, f"SELECT upper(`name`) AS `upper_name` FROM `{TABLE}` WHERE `name` = 'Alice'")
        assert data['results'][0]['upper_name'] == 'ALICE'

    def test_alias_count(self, base: Base):
        data = _sql(base, f"SELECT COUNT(*) AS `total` FROM `{TABLE}`")
        assert data['results'][0]['total'] == 4


# ===================================================================
# SQL SYNTAX — LIMIT & OFFSET
# ===================================================================

class TestLimitOffset:

    def test_limit(self, base: Base):
        _setup(base)
        data = _sql(base, f"SELECT `name` FROM `{TABLE}` LIMIT 2")
        assert len(data['results']) == 2

    def test_limit_offset(self, base: Base):
        data = _sql(base, f"SELECT `name` FROM `{TABLE}` ORDER BY `name` ASC LIMIT 2 OFFSET 1")
        names = [r['name'] for r in data['results']]
        # Sorted: Alice, Bob, Charlie, Diana → offset 1: Bob, Charlie
        assert len(names) == 2
        assert names[0] == 'Bob'
        assert names[1] == 'Charlie'


# ===================================================================
# SQL SYNTAX — ORDER BY RULES
# ===================================================================

class TestOrderByRules:

    def test_order_by_asc(self, base: Base):
        _setup(base)
        data = _sql(base, f"SELECT `name`, `age` FROM `{TABLE}` ORDER BY `age` ASC")
        ages = [r['age'] for r in data['results']]
        assert ages == [25, 28, 30, 35]

    def test_order_by_desc(self, base: Base):
        data = _sql(base, f"SELECT `name`, `age` FROM `{TABLE}` ORDER BY `age` DESC")
        ages = [r['age'] for r in data['results']]
        assert ages == [35, 30, 28, 25]

    def test_order_by_column_not_in_select(self, base: Base):
        """ORDER BY column does NOT need to be in SELECT — contrary to some docs."""
        data = _sql(base, f"SELECT `name` FROM `{TABLE}` ORDER BY `age` ASC")
        names = [r['name'] for r in data['results']]
        assert names[0] == 'Bob'    # age 25
        assert names[-1] == 'Charlie'  # age 35

    def test_order_by_multiple_columns(self, base: Base):
        data = _sql(base, f"SELECT `city`, `name`, `age` FROM `{TABLE}` ORDER BY `city` ASC, `age` DESC")
        results = [(r['city'], r['name']) for r in data['results']]
        assert results[0] == ('Berlin', 'Charlie')  # Berlin, age 35
        assert results[1] == ('Berlin', 'Alice')     # Berlin, age 30


# ===================================================================
# SQL SYNTAX — DISTINCT
# ===================================================================

class TestDistinct:

    def test_distinct(self, base: Base):
        _setup(base)
        data = _sql(base, f"SELECT DISTINCT `city` FROM `{TABLE}` ORDER BY `city`")
        cities = [r['city'] for r in data['results']]
        assert cities == ['Berlin', 'Hamburg', 'Munich']


# ===================================================================
# SQL SYNTAX — QUOTING
# ===================================================================

TABLE_SPECIAL = 'test special names'
_special_setup_done = False


def _setup_special(base: Base):
    global _special_setup_done
    if not _special_setup_done:
        create_table(base, TABLE_SPECIAL, [
            {'column_name': 'full name', 'column_type': 'text'},
            {'column_name': 'date', 'column_type': 'text'},  # reserved word as column name
        ])
        append_rows(base, TABLE_SPECIAL, [
            {'full name': 'John Doe', 'date': '2025-01-01'},
        ])
        _special_setup_done = True


class TestQuoting:

    def test_backtick_table_with_spaces(self, base: Base):
        _setup_special(base)
        data = _sql(base, "SELECT `full name` FROM `test special names` LIMIT 1")
        assert _val(data) == 'John Doe'

    def test_backtick_column_with_spaces(self, base: Base):
        data = _sql(base, "SELECT `full name` FROM `test special names` WHERE `full name` = 'John Doe'")
        assert _val(data) == 'John Doe'

    def test_backtick_reserved_word_column(self, base: Base):
        """Column named 'date' (reserved word) must be backtick-quoted."""
        data = _sql(base, "SELECT `date` FROM `test special names` LIMIT 1")
        assert _val(data) == '2025-01-01'

    def test_double_quote_table_not_supported(self, base: Base):
        """Double quotes should NOT work for identifiers."""
        status = _sql_error(base, 'SELECT "full name" FROM "test special names" LIMIT 1')
        assert status == 400


# ===================================================================
# SQL SYNTAX — IMPLICIT JOINS
# ===================================================================

TABLE_JOIN_A = 'test_join_orders'
TABLE_JOIN_B = 'test_join_customers'
_join_setup_done = False


def _setup_join(base: Base):
    global _join_setup_done
    if not _join_setup_done:
        create_table(base, TABLE_JOIN_B, [
            {'column_name': 'customer_id', 'column_type': 'number'},
            {'column_name': 'customer_name', 'column_type': 'text'},
        ])
        append_rows(base, TABLE_JOIN_B, [
            {'customer_id': 1, 'customer_name': 'Alice'},
            {'customer_id': 2, 'customer_name': 'Bob'},
        ])
        create_table(base, TABLE_JOIN_A, [
            {'column_name': 'order_id', 'column_type': 'number'},
            {'column_name': 'customer_id', 'column_type': 'number'},
            {'column_name': 'product', 'column_type': 'text'},
        ])
        append_rows(base, TABLE_JOIN_A, [
            {'order_id': 100, 'customer_id': 1, 'product': 'Widget'},
            {'order_id': 101, 'customer_id': 2, 'product': 'Gadget'},
            {'order_id': 102, 'customer_id': 1, 'product': 'Gizmo'},
        ])
        _join_setup_done = True


class TestJoins:

    def test_implicit_join(self, base: Base):
        """Implicit joins (FROM T1, T2 WHERE ...) are the only supported join syntax.
        Note: In JOIN results, convert_keys does NOT map to column names.
        Use metadata to identify which key corresponds to which column.
        """
        _setup_join(base)
        data = _sql(base, f"""
            SELECT `{TABLE_JOIN_A}`.`product`, `{TABLE_JOIN_B}`.`customer_name`
            FROM `{TABLE_JOIN_A}`, `{TABLE_JOIN_B}`
            WHERE `{TABLE_JOIN_A}`.`customer_id` = `{TABLE_JOIN_B}`.`customer_id`
              AND `{TABLE_JOIN_B}`.`customer_name` = 'Alice'
        """)
        assert len(data['results']) == 2
        # Extract all values from results regardless of key names
        all_values = set()
        for r in data['results']:
            all_values.update(r.values())
        assert 'Widget' in all_values
        assert 'Gizmo' in all_values
        assert 'Alice' in all_values

    def test_inner_join_not_supported(self, base: Base):
        _setup_join(base)
        assert _sql_error(base, f"""
            SELECT `{TABLE_JOIN_A}`.`product`
            FROM `{TABLE_JOIN_A}`
            INNER JOIN `{TABLE_JOIN_B}` ON `{TABLE_JOIN_A}`.`customer_id` = `{TABLE_JOIN_B}`.`customer_id`
        """) == 400

    def test_left_join_not_supported(self, base: Base):
        assert _sql_error(base, f"""
            SELECT `{TABLE_JOIN_A}`.`product`
            FROM `{TABLE_JOIN_A}`
            LEFT JOIN `{TABLE_JOIN_B}` ON `{TABLE_JOIN_A}`.`customer_id` = `{TABLE_JOIN_B}`.`customer_id`
        """) == 400

    def test_right_join_not_supported(self, base: Base):
        assert _sql_error(base, f"""
            SELECT `{TABLE_JOIN_A}`.`product`
            FROM `{TABLE_JOIN_A}`
            RIGHT JOIN `{TABLE_JOIN_B}` ON `{TABLE_JOIN_A}`.`customer_id` = `{TABLE_JOIN_B}`.`customer_id`
        """) == 400


# ===================================================================
# SQL SYNTAX — WRITE OPERATIONS (INSERT, UPDATE, DELETE)
# ===================================================================

TABLE_WRITE = 'test_write_ops'
_write_setup_done = False


def _setup_write(base: Base):
    global _write_setup_done
    if not _write_setup_done:
        create_table(base, TABLE_WRITE, [
            {'column_name': 'item', 'column_type': 'text'},
            {'column_name': 'qty', 'column_type': 'number'},
        ])
        append_rows(base, TABLE_WRITE, [
            {'item': 'Apple', 'qty': 10},
            {'item': 'Banana', 'qty': 20},
            {'item': 'Cherry', 'qty': 30},
        ])
        _write_setup_done = True


class TestWriteOperations:

    def test_insert_via_api_gateway_not_supported(self, base: Base):
        """INSERT via SQL through api-gateway returns 'base not found' error.
        This is a known limitation — INSERT via SQL does not work through the api-gateway endpoint.
        """
        _setup_write(base)
        status = _sql_write_status(base, f"INSERT INTO `{TABLE_WRITE}` (`item`, `qty`) VALUES ('Durian', 5)")
        assert status == 400

    def test_update_set_literal_string(self, base: Base):
        _sql_write(base, f"UPDATE `{TABLE_WRITE}` SET `item` = 'Green Apple' WHERE `item` = 'Apple'")
        data = _sql(base, f"SELECT `item` FROM `{TABLE_WRITE}` WHERE `item` = 'Green Apple'")
        assert len(data['results']) == 1

    def test_update_set_literal_number(self, base: Base):
        _sql_write(base, f"UPDATE `{TABLE_WRITE}` SET `qty` = 99 WHERE `item` = 'Banana'")
        data = _sql(base, f"SELECT `qty` FROM `{TABLE_WRITE}` WHERE `item` = 'Banana'")
        assert data['results'][0]['qty'] == 99

    def test_delete_where(self, base: Base):
        _sql_write(base, f"DELETE FROM `{TABLE_WRITE}` WHERE `item` = 'Durian'")
        data = _sql(base, f"SELECT `item` FROM `{TABLE_WRITE}` WHERE `item` = 'Durian'")
        assert len(data['results']) == 0

    def test_update_set_function_not_supported(self, base: Base):
        """Functions are NOT allowed in SET clauses."""
        assert _sql_write_status(base, f"UPDATE `{TABLE_WRITE}` SET `item` = upper('test') WHERE `item` = 'Cherry'") == 400

    def test_update_set_expression_not_supported(self, base: Base):
        """Arithmetic expressions are NOT allowed in SET clauses."""
        assert _sql_write_status(base, f"UPDATE `{TABLE_WRITE}` SET `qty` = `qty` + 1 WHERE `item` = 'Cherry'") == 400

    def test_insert_function_in_values_not_supported(self, base: Base):
        """Functions are NOT allowed in INSERT VALUES."""
        assert _sql_write_status(base, f"INSERT INTO `{TABLE_WRITE}` (`item`, `qty`) VALUES (upper('fig'), 5)") == 400


# ===================================================================
# SQL SYNTAX — ARITHMETIC OPERATORS
# ===================================================================

class TestArithmeticOperators:
    """Standard SQL arithmetic operators (+, -, *, /) work in SELECT.
    Note: result keys are prefixed with table name, e.g. 'test_sql_functions.age + 10'.
    """

    def test_plus_in_select(self, base: Base):
        _setup(base)
        data = _sql(base, f"SELECT `age` + 10 FROM `{TABLE}` WHERE `name` = 'Alice'")
        assert _val(data) == 40

    def test_minus_in_select(self, base: Base):
        data = _sql(base, f"SELECT `age` - 5 FROM `{TABLE}` WHERE `name` = 'Alice'")
        assert _val(data) == 25

    def test_multiply_operator_in_select(self, base: Base):
        data = _sql(base, f"SELECT `age` * 2 FROM `{TABLE}` WHERE `name` = 'Alice'")
        assert _val(data) == 60

    def test_divide_operator_in_select(self, base: Base):
        data = _sql(base, f"SELECT `age` / 2 FROM `{TABLE}` WHERE `name` = 'Alice'")
        assert _val(data) == 15


# ===================================================================
# SQL SYNTAX — UNSUPPORTED CONSTRUCTS
# ===================================================================

class TestUnsupportedSyntax:
    """Verify that MySQL/standard SQL constructs NOT supported by SeaTable fail."""

    def test_subquery_in_where_not_supported(self, base: Base):
        _setup(base)
        assert _sql_error(base, f"SELECT `name` FROM `{TABLE}` WHERE `age` IN (SELECT MAX(`age`) FROM `{TABLE}`)") == 400

    def test_subquery_in_from_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT * FROM (SELECT `name` FROM `{TABLE}`) AS sub") == 400

    def test_union_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT `name` FROM `{TABLE}` WHERE `city` = 'Berlin' UNION SELECT `name` FROM `{TABLE}` WHERE `city` = 'Munich'") == 400

    def test_union_all_not_supported(self, base: Base):
        assert _sql_error(base, f"SELECT `name` FROM `{TABLE}` UNION ALL SELECT `name` FROM `{TABLE}`") == 400

    def test_delete_without_where_is_allowed(self, base: Base):
        """WARNING: DELETE without WHERE IS allowed and deletes ALL rows!"""
        disposable = 'test_disposable_del'
        create_table(base, disposable, [{'column_name': 'x', 'column_type': 'text'}])
        append_rows(base, disposable, [{'x': 'a'}, {'x': 'b'}])
        _sql_write(base, f"DELETE FROM `{disposable}`")
        data = _sql(base, f"SELECT * FROM `{disposable}`")
        assert len(data['results']) == 0

    def test_update_without_where_is_allowed(self, base: Base):
        """WARNING: UPDATE without WHERE IS allowed and updates ALL rows!"""
        disposable = 'test_disposable_upd'
        create_table(base, disposable, [{'column_name': 'x', 'column_type': 'text'}])
        append_rows(base, disposable, [{'x': 'a'}, {'x': 'b'}])
        _sql_write(base, f"UPDATE `{disposable}` SET `x` = 'changed'")
        data = _sql(base, f"SELECT `x` FROM `{disposable}`")
        assert all(r['x'] == 'changed' for r in data['results'])


# ===================================================================
# REMAINING FUNCTIONS — text(), countItems(), country(), isoweeknum()
# ===================================================================

TABLE_SPECIAL_COLS = 'test_special_columns'
_special_cols_setup_done = False


def _setup_special_cols(base: Base):
    global _special_cols_setup_done
    if not _special_cols_setup_done:
        create_table(base, TABLE_SPECIAL_COLS, [
            {'column_name': 'label', 'column_type': 'text'},
            {'column_name': 'tags', 'column_type': 'multiple-select', 'column_data': {
                'options': [
                    {'id': 'aa01', 'name': 'red', 'color': '#9860E5', 'textColor': '#000000'},
                    {'id': 'aa02', 'name': 'green', 'color': '#59CB74', 'textColor': '#000000'},
                    {'id': 'aa03', 'name': 'blue', 'color': '#89D2EA', 'textColor': '#000000'},
                ]
            }},
            {'column_name': 'location', 'column_type': 'geolocation', 'column_data': {
                'geo_format': 'country_region',
                'lang': 'en',
            }},
        ])
        append_rows(base, TABLE_SPECIAL_COLS, [
            {'label': 'row1', 'tags': ['red', 'green'], 'location': {'country_region': 'Germany'}},
            {'label': 'row2', 'tags': ['blue'], 'location': {'country_region': 'France'}},
            {'label': 'row3', 'tags': ['red', 'green', 'blue'], 'location': {'country_region': 'Germany'}},
        ])
        _special_cols_setup_done = True


class TestRemainingFunctions:

    def test_text_euro(self, base: Base):
        """text(number, format) converts number to formatted text."""
        _setup(base)
        data = _sql(base, f"SELECT text(150, 'euro') FROM `{TABLE}` LIMIT 1")
        result = str(_val(data))
        assert '€' in result and '150' in result

    def test_text_percent(self, base: Base):
        data = _sql(base, f"SELECT text(50, 'percent') FROM `{TABLE}` LIMIT 1")
        result = str(_val(data))
        assert '5000%' in result  # 50 → 5000% as documented

    def test_countItems_multiple_select(self, base: Base):
        """countItems() counts items in a multiple-select column."""
        _setup_special_cols(base)
        data = _sql(base, f"SELECT countItems(`tags`) FROM `{TABLE_SPECIAL_COLS}` WHERE `label` = 'row1'")
        assert _val(data) == 2

    def test_countItems_three_items(self, base: Base):
        data = _sql(base, f"SELECT countItems(`tags`) FROM `{TABLE_SPECIAL_COLS}` WHERE `label` = 'row3'")
        assert _val(data) == 3

    def test_countItems_single_item(self, base: Base):
        data = _sql(base, f"SELECT countItems(`tags`) FROM `{TABLE_SPECIAL_COLS}` WHERE `label` = 'row2'")
        assert _val(data) == 1

    def test_country(self, base: Base):
        """country() returns the country from a geolocation column."""
        _setup_special_cols(base)
        data = _sql(base, f"SELECT country(`location`) FROM `{TABLE_SPECIAL_COLS}` WHERE `label` = 'row1'")
        assert _val(data) == 'Germany'

    def test_country_different_value(self, base: Base):
        data = _sql(base, f"SELECT country(`location`) FROM `{TABLE_SPECIAL_COLS}` WHERE `label` = 'row2'")
        assert _val(data) == 'France'

    def test_isoweeknum_not_supported_in_sql(self, base: Base):
        """isoweeknum() is documented but NOT supported as standalone function in SQL.
        Use weeknum(date, 21) instead for ISO week numbers.
        """
        _setup(base)
        assert _sql_error(base, f"SELECT isoweeknum('2025-01-06') FROM `{TABLE}` LIMIT 1") == 400

    def test_isoweeknum_via_weeknum(self, base: Base):
        """ISO week numbers work via weeknum(date, 21)."""
        data = _sql(base, f"SELECT weeknum('2025-01-06', 21) FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 2


# ===================================================================
# FUNCTIONS IN DIFFERENT CLAUSES
# ===================================================================

class TestFunctionsInClauses:
    """Verify where functions can and cannot be used."""

    def test_function_in_select(self, base: Base):
        _setup(base)
        data = _sql(base, f"SELECT upper(`name`) FROM `{TABLE}` WHERE `name` = 'Alice'")
        assert _val(data) == 'ALICE'

    def test_function_in_where(self, base: Base):
        data = _sql(base, f"SELECT `name` FROM `{TABLE}` WHERE len(`name`) = 3")
        assert data['results'][0]['name'] == 'Bob'

    def test_function_in_order_by(self, base: Base):
        data = _sql(base, f"SELECT `name`, len(`name`) FROM `{TABLE}` ORDER BY len(`name`) ASC")
        names = [r['name'] for r in data['results']]
        assert names[0] == 'Bob'  # len 3

    def test_function_in_group_by(self, base: Base):
        data = _sql(base, f"SELECT left(`name`, 1) AS `initial`, COUNT(*) FROM `{TABLE}` GROUP BY left(`name`, 1)")
        initials = {r['initial'] for r in data['results']}
        assert 'A' in initials
        assert 'B' in initials

    def test_function_in_having(self, base: Base):
        data = _sql(base, f"SELECT `city`, COUNT(*) FROM `{TABLE}` GROUP BY `city` HAVING COUNT(*) >= 2")
        assert len(data['results']) == 1
        assert data['results'][0]['city'] == 'Berlin'


# ===================================================================
# DOCUMENTATION CONSISTENCY TESTS
# These tests resolve open questions from the developer docs review.
# ===================================================================

class TestDocConsistency:
    """Tests that clarify contradictions or ambiguities in the SQL docs."""

    # --- dateDif: is the unit parameter required or optional? ---

    def test_dateDif_without_unit(self, base: Base):
        """functions.md says unit is 'optional', but the comparison table says 'required'.
        This test determines which is correct."""
        _setup(base)
        data = _sql(base, f"SELECT dateDif('2023-01-01', '2025-01-01') FROM `{TABLE}` LIMIT 1")
        result = _val(data)
        # If this succeeds, unit is truly optional. The result should be in days (default).
        assert isinstance(result, (int, float))

    def test_dateDif_with_unit_D(self, base: Base):
        data = _sql(base, f"SELECT dateDif('2023-01-01', '2025-01-01', 'D') FROM `{TABLE}` LIMIT 1")
        assert _val(data) == 730 or _val(data) == 731  # leap year

    # --- average() vs AVG(): are they the same? ---

    def test_avg_aggregate(self, base: Base):
        """AVG() is a standard SQL aggregate function."""
        data = _sql(base, f"SELECT AVG(`age`) FROM `{TABLE}`")
        assert data['results'][0]['AVG(age)'] == 29.5

    def test_average_as_aggregate(self, base: Base):
        """Can average() be used as an aggregate like AVG()?"""
        data = _sql(base, f"SELECT average(`age`) FROM `{TABLE}`")
        result = _val(data)
        # If this works, average() works as aggregate on a column
        assert isinstance(result, (int, float))

    def test_average_NOT_usable_in_group_by(self, base: Base):
        """average() is a formula function, NOT an aggregate — it fails with GROUP BY."""
        assert _sql_error(base, f"SELECT `city`, average(`age`) FROM `{TABLE}` GROUP BY `city`") == 400

    def test_avg_in_group_by(self, base: Base):
        """AVG() in GROUP BY for comparison."""
        data = _sql(base, f"SELECT `city`, AVG(`age`) FROM `{TABLE}` GROUP BY `city`")
        assert len(data['results']) == 3

    # --- statistical functions: can they be used as aggregates? ---

    def test_counta_on_column(self, base: Base):
        """Can counta() be used on a column (as aggregate)?"""
        data = _sql(base, f"SELECT counta(`name`) FROM `{TABLE}`")
        result = _val(data)
        assert isinstance(result, (int, float))

    def test_countall_on_column(self, base: Base):
        """Can countall() be used on a column (as aggregate)?"""
        data = _sql(base, f"SELECT countall(`name`) FROM `{TABLE}`")
        result = _val(data)
        assert isinstance(result, (int, float))

    def test_countblank_on_column(self, base: Base):
        """Can countblank() be used on a column (as aggregate)?"""
        data = _sql(base, f"SELECT countblank(`name`) FROM `{TABLE}`")
        result = _val(data)
        assert isinstance(result, (int, float))

    # --- ILIKE: case-insensitive LIKE ---

    def test_ilike(self, base: Base):
        """ILIKE for case-insensitive matching (documented in select.md)."""
        data = _sql(base, f"SELECT `name` FROM `{TABLE}` WHERE `name` ILIKE 'alice'")
        assert len(data['results']) == 1
        assert data['results'][0]['name'] == 'Alice'

    # --- Case insensitivity of function names ---

    def test_function_name_uppercase(self, base: Base):
        """index.md says SQL is case insensitive. Do uppercase function names work?"""
        data = _sql(base, f"SELECT UPPER(`name`) FROM `{TABLE}` WHERE `name` = 'Alice'")
        assert _val(data) == 'ALICE'

    def test_function_name_mixed_case(self, base: Base):
        """Mixed case function name."""
        data = _sql(base, f"SELECT Upper(`name`) FROM `{TABLE}` WHERE `name` = 'Alice'")
        assert _val(data) == 'ALICE'

    def test_now_uppercase(self, base: Base):
        """NOW() should work the same as now()."""
        data = _sql(base, f"SELECT NOW() FROM `{TABLE}` LIMIT 1")
        result = _val(data)
        assert '202' in result  # returns a date string
