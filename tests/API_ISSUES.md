# SeaTable API — Issues and Inconsistencies

Issues discovered during automated API testing against SeaTable 6.0.10 and 6.1. These are server-side API behaviors — not bugs in the OpenAPI spec or test suite.

## Summary

| # | Issue | Severity | Action Required |
|---|-------|----------|-----------------|
| 1 | Checkbox: integer `1` stored as `false` | High | Yes — reject or coerce |
| 2 | Select columns: unknown options auto-created | Low | No — acceptable behavior |
| 3 | Rating: no range validation | Medium | Yes — reject out-of-range |
| 4 | Auto-number: overwritable via API | Medium | Yes — reject writes |
| 5 | Invalid date: silently stored as `null` | Medium | Yes — return error |
| 6 | Geolocation: partial data accepted | Low | Yes — require both lat/lng |
| 7 | Read-only columns: inconsistent enforcement | Medium | Yes — same as #4 |
| 8 | POST /rows/ ignores `convert_keys` in response | Low | No — feature request |
| 9 | DELETE /links/ reports success for non-existing links | Medium | Yes — return count 0 |
| 10 | Typo: "row _id not exits" | Low | Yes — fix typo |
| 11 | Multiple typos in dtable-web ("does not exits") | Low | Yes — fix typos |
| 12 | No createRowComment endpoint | Medium | Yes — re-added in 6.1 |
| 13 | deleteUserShare missing requestBody in spec | Low | Fixed in this repo |
| 14 | createWebhook returns 200 instead of 201 | Low | Yes — return 201 |
| 15 | createGroupShare returns 200 instead of 201 | Low | Yes — return 201 |
| 16 | group_id returned as string instead of integer | Low | Yes — return integer |
| 17 | addNewUser returns 403 for license limit | Low | Yes — use 409 or 402 |
| 18 | listColumns excludes auto-created Name column | Low | No — document behavior |
| 19 | deleteGroup fails silently-ish when group has bases | Low | Fixed in this repo |
| 20 | Ping endpoints: inconsistent response formats | Low | Fixed in this repo |

---

## Data Integrity Issues

### 1. Checkbox: integer `1` is stored as `false`

**Severity:** High — silent data corruption

When writing `1` (integer) to a checkbox column, SeaTable stores `false` instead of `true`. Only the boolean `true` is accepted. An LLM/agent might reasonably send `1` as a truthy value.

```
Input:  { "Checkbox": 1 }
Stored: { "Checkbox": false }   ← expected: true
```

**Recommendation:** Return an error if the value is not a boolean, or coerce truthy values (`1`, `"true"`) to `true`.

### 2. Single-select / multiple-select: unknown options are auto-created

**Severity:** Low

Writing a non-existing option name to a select column silently creates the option in the column configuration. No error, no warning.

```
Input:  { "Single-Select": "option xyz" }
Result: New option "option xyz" created in column definition
```

Any typo or hallucinated option name permanently modifies the column schema.

**Assessment:** Acceptable behavior in most cases. A `create_if_missing` flag (default `true` for backward compatibility) would be a nice improvement.

### 3. Rating: no range validation

**Severity:** Medium — invalid data accepted

Rating columns have a configured maximum (e.g., `rate_max_number: 7`), but the API accepts values above the maximum, zero, and negative values.

```
Input:  { "Rating": 8 }    ← max is 7
Stored: { "Rating": 8 }    ← no error
```

**Recommendation:** Reject values outside `1..rate_max_number`.

### 4. Auto-number: overwritable via API

**Severity:** Medium — sequence integrity compromised

Auto-number columns are supposed to be system-managed, but the API accepts arbitrary values via both `appendRows` and `updateRow`.

```
Input:  { "Auto-Number": "9999" }
Stored: { "Auto-Number": "9999" }   ← expected: rejected or ignored
```

**Recommendation:** Reject writes to auto-number columns.

### 5. Invalid date format: silently stored as `null`

**Severity:** Medium — silent data loss

When an invalid date string is written, the API stores `null` without returning an error. The caller has no indication that the date was rejected.

```
Input:  { "Date": "13/31/2025" }
Stored: { "Date": null }   ← no error returned
```

**Recommendation:** Return a validation error for unparseable date strings.

### 6. Geolocation: partial data accepted

**Severity:** Low — incomplete data stored

A geolocation column with `geo_format: "lng_lat"` accepts objects with only one coordinate.

```
Input:  { "Geolocation": { "lng": 11.576 } }   ← lat missing
Stored: { "Geolocation": { "lng": 11.576 } }   ← no error
```

**Recommendation:** Require both `lat` and `lng` when writing.

### 7. Read-only columns: inconsistent enforcement

**Severity:** Medium

| Column Type | Write Attempt | Result |
|-------------|---------------|--------|
| Formula | Ignored | Correct (value not stored) |
| Creator | Ignored | Correct (real creator preserved) |
| Created (ctime) | Ignored | Correct (real timestamp used) |
| Auto-Number | **Accepted** | **Value overwritten** (see #4) |

Formula, creator, and created time correctly reject writes. Auto-number does not.

**Recommendation:** Same fix as #4 — reject writes to auto-number columns.

---

## API Response Issues

### 8. POST /rows/ ignores `convert_keys` in response

**Severity:** Low — feature request

When creating rows with `convert_keys: true`, the response still returns column keys instead of column names.

```
Request:  POST /rows/ { table_name, rows, convert_keys: true }
Response: { "0000": "Test", "ZBoJ": 42, ... }   ← keys, not names
```

`GET /rows/` and `GET /rows/{id}/` correctly respect `convert_keys`.

**Assessment:** Not a bug, but a reasonable feature request for consistency.

### 9. DELETE /links/ reports success for non-existing links

**Severity:** Medium

Unlinking a row pair that doesn't exist returns `{ deleted_links_count: 1, success: true }` instead of `{ deleted_links_count: 0 }`.

**Recommendation:** Return the actual count of deleted links.

### 10. Typo: "row _id not exits"

**Severity:** Low

When requesting a non-existing row via `GET /rows/{id}/`, the error message reads:

```
"row _id not exits"   ← should be "row not found"
```

### 11. Multiple typos in dtable-web

**Severity:** Low

Several source files contain the typo "does not exits" instead of "does not exist":

- `seahub/api2/endpoints/dtable_third_party_accounts.py:200` — `"Account %s does not exits."`
- `seahub/api2/endpoints/dtable_view_external_links.py:207` — `"View external link does not exits."`
- `seahub/base/accounts.py:203,210,713` — `"User matching query does not exits."`

---

## Missing Operations

### 12. No createRowComment endpoint

**Severity:** Medium

There is no API endpoint to create a row comment. The `create_row_comment` schema exists in `base_operations.yaml` but no POST operation is defined on `/api-gateway/api/v2/dtables/{base_uuid}/comments/` (returns 405 Method Not Allowed).

**Status:** Will be re-added in 6.1.

---

## OpenAPI Spec Issues

### 13. deleteUserShare missing requestBody

The `deleteUserShare` operation in `user_account_operations.yaml` had no `requestBody` defined, but the API requires `email` as form data in the request body.

**Fixed in:** This repository (commit 188837f).

---

## Inconsistent Response Behavior

### 14. createWebhook returns 200 instead of 201

`POST /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/webhooks/` returns HTTP 200 on success. Creating a resource should return 201 Created per REST conventions.

### 15. createGroupShare returns 200 instead of 201

`POST /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/group-shares/` returns HTTP 200 on success. Should return 201 Created. For comparison, `createUserShare` correctly returns 201.

### 16. group_id returned as string instead of integer

`POST .../group-shares/` returns `group_id` as a string (e.g., `"44"`) in the response, but it is an integer everywhere else (path parameters, `listGroupShares` response).

### 17. addNewUser returns 403 for license limit

`POST /api/v2.1/admin/users/` returns `403 {"error_msg": "The number of users exceeds the limit."}` when the license user limit is reached. A 403 typically means insufficient permissions, which is misleading. A 409 Conflict or 402 Payment Required would be more appropriate.

### 18. listColumns excludes auto-created Name column

`GET /api-gateway/api/v2/dtables/{base_uuid}/columns/` only returns explicitly created columns when a table was created with a custom columns array via `createTable`. The auto-created default `Name` column is not included.

**Assessment:** Not necessarily a bug, but the behavior should be documented.

### 19. deleteGroup returns misleading error when group contains bases

**Severity:** Low

`DELETE /api/v2.1/groups/{group_id}/` returns `400` with `"Cannot delete group with bases"` if the group still contains bases. The error is correct but undocumented — callers need to delete or move all bases first.

**Fixed in:** This repository — added documentation note to `deleteGroup` in all three specs.

### 20. Ping endpoints: inconsistent response formats

**Severity:** Low

The five ping endpoints return three different response formats:

| Endpoint | Content-Type | Body |
|----------|-------------|------|
| `GET /api2/ping/` | `application/json` | `"pong"` (JSON string) |
| `GET /api2/auth/ping/` | `application/json` | `"pong"` (JSON string) |
| `GET /dtable-server/ping/` | `text/html` | `pong` (plain text) |
| `GET /dtable-db/ping/` | `application/json` | `{"ret": "pong"}` (JSON object) |
| `GET /api-gateway/api/v2/ping/` | `application/json` | `{"ret": "pong"}` (JSON object) |

**Recommendation:** Harmonize all ping endpoints to return the same format — ideally `application/json` with `{"ret": "pong"}` for consistency with dtable-db and api-gateway.

**Workaround:** OpenAPI spec in this repository has been adjusted to match actual behavior.
