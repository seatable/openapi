# SeaTable API — Issues and Inconsistencies

Issues discovered during automated API testing against SeaTable 6.0.10 and 6.1. These are server-side API behaviors — not bugs in the OpenAPI spec or test suite.

## New Issues (2026-03-20)

| # | Issue | Severity | Action Required |
|---|-------|----------|-----------------|
| 27 | appendColumns fails with link-formula columns | Medium | Yes — support link-formula in batch append |
| 28 | insertColumn rejects DD/MM/YYYY HH:mm date format | Medium | Yes — accept European date format with time |
| 29 | markBaseNotificationsAsSeen rejects JSON boolean | Medium | Yes — accept JSON boolean for `seen` |
| 30 | sendToastNotification rejects request body | Medium | Yes — align request body with spec |
| 31 | Python scheduler endpoints return 406 | Low | Investigate — may require feature flag |
| 32 | SQL INSERT via api-gateway returns "base not found" | Medium | Yes — fix INSERT handling in api-gateway |
| 33 | SQL JOIN results ignore `convert_keys: true` | Low | Yes — apply convert_keys to JOIN results |
| 34 | SQL constants `pi`/`e` not recognized standalone | Low | No — document workaround |

### 27. appendColumns fails with link-formula columns

**Severity:** Medium

`POST /api-gateway/api/v2/dtables/{base_uuid}/batch-append-columns/` returns an error when trying to append a `link-formula` column, even when valid `column_data` with `link_column_key`, `formula`, and `result_type` is provided.

Regular `insertColumn` works for link-formula columns. Only the batch endpoint fails.

**Recommendation:** Support link-formula columns in `appendColumns`, consistent with `insertColumn`.

### 28. insertColumn rejects DD/MM/YYYY HH:mm date format

**Severity:** Medium

Creating a date column with `"format": "DD/MM/YYYY HH:mm"` (European format with hours and minutes) is rejected by the API as "not meeting specifications", while `"DD/MM/YYYY"` (without time) works fine.

Other date formats with time (e.g., `"YYYY-MM-DD HH:mm"`, `"M/D/YYYY HH:mm"`) are accepted.

**Recommendation:** Accept `DD/MM/YYYY HH:mm` as a valid date format.

### 29. markBaseNotificationsAsSeen rejects JSON boolean for `seen`

**Severity:** Medium — breaks JSON API clients

`PUT /api-gateway/api/v2/dtables/{base_uuid}/notifications/` returns `400` with `"seen invalid"` when the `seen` field is sent as a JSON boolean (`true`/`false`). The API expects the form-encoded string `"true"` instead.

This also affects the singular endpoint `PUT .../notifications/{notification_id}/`.

**Recommendation:** Accept JSON booleans in addition to form-encoded strings.

### 30. sendToastNotification rejects request body

**Severity:** Medium

`POST /api-gateway/api/v2/dtables/{base_uuid}/ui-toasts/` returns `400` with `"parameters invalid"` when the request body matches the documented schema (`to_users`, `msg_type`, `detail`). The actual expected format appears to differ from the spec.

**Recommendation:** Align the API implementation with the documented request body format, or update the spec to match the actual expected format.

### 31. Python scheduler endpoints return 406

**Severity:** Low — may be environment-specific

The Python scheduler statistics endpoints (e.g., `GET /admin/statistics/by-day/`) return `406 Not Acceptable` on the test server. This may be because the Python scheduler component is not enabled or not installed in the test environment.

**Assessment:** Not necessarily a bug. If the scheduler is an optional component, the endpoints should return `503 Service Unavailable` or a clear error message instead of `406`.

### 32. SQL INSERT via api-gateway returns "base not found"

**Severity:** Medium — SQL INSERT broken via api-gateway

`POST /api-gateway/api/v2/dtables/{base_uuid}/sql/` with an `INSERT INTO` statement returns `400` with `{"error_message": "base {uuid} not found: insert on non-existent base"}`, even though the base exists and is accessible.

`UPDATE` and `DELETE` statements work correctly through the same endpoint. Only `INSERT` fails. A preceding `SELECT` on the same base does not resolve the issue.

```
SQL:    INSERT INTO `table` (`col`) VALUES ('value')
Result: 400 — "base {uuid} not found: insert on non-existent base"
```

**Tested on:** SeaTable 6.1.8

**Recommendation:** Fix INSERT handling in the api-gateway to match UPDATE/DELETE behavior.

### 33. SQL JOIN results ignore `convert_keys: true`

**Severity:** Low — inconsistent behavior

When executing an implicit JOIN query via `POST /api-gateway/api/v2/dtables/{base_uuid}/sql/` with `convert_keys: true`, the result rows use internal column key IDs (e.g., `rLfY`, `kz15`) instead of column names. For non-JOIN SELECT queries, `convert_keys: true` correctly returns column names as keys.

```
Query:   SELECT `orders`.`product`, `customers`.`name` FROM `orders`, `customers` WHERE ...
Result:  [{"rLfY": "Widget", "kz15": "Alice"}, ...]   ← internal keys instead of names
```

The column names are available in the response `metadata` array, so callers can manually map keys to names. But this is an inconsistency with non-JOIN queries where `convert_keys` works as expected.

**Recommendation:** Apply `convert_keys` mapping to JOIN result rows, consistent with non-JOIN queries.

### 34. SQL constants `pi` and `e` not recognized as standalone expressions

**Severity:** Low — parser limitation

The documented constants `pi` and `e` work correctly as function arguments (e.g., `SELECT multiply(pi, 2)` returns `6.28...`), but fail when used as standalone SELECT expressions. The parser interprets them as column names.

```
SELECT pi FROM `table`              → 400: "no such column: pi"
SELECT multiply(pi, 2) FROM `table` → 200: 6.28318...
```

**Assessment:** Edge case with a simple workaround. Document that constants must be used inside function calls.

---

## Previous Issues (reported to developers)

## Summary

| # | Issue | Severity | Action Required |
|---|-------|----------|-----------------|
| 1 | Checkbox: integer `1` stored as `false` | High | Yes — reject or coerce |
| 21 | Auth errors: 403 instead of 401 for missing/invalid tokens | Medium | Yes — return 401 |
| 3 | Rating: no range validation | Medium | Yes — reject out-of-range |
| 4 | Auto-number: overwritable via API | Medium | Yes — reject writes |
| 5 | Invalid date: silently stored as `null` | Medium | Yes — return error |
| 7 | Read-only columns: inconsistent enforcement | Medium | Yes — same as #4 |
| 9 | DELETE /links/ reports success for non-existing links | Medium | Yes — return count 0 |
| 12 | No createRowComment endpoint | Medium | Yes — re-added in 6.1 |
| 17 | addNewUser returns 403 for license limit | Medium | Yes — use 409 or 402 |
| 22 | updateColumn to link type creates broken column | Medium | Yes — validate column_data |
| 23 | Temp API-Token creation uses GET instead of POST | Low | Yes — use POST |
| 26 | getFileDownloadLink returns 400 instead of 404 | Low | Yes — return 404 |
| 24 | app_name inconsistently used as path vs body param | Low | No — document behavior |
| 25 | Base-Token endpoints return different field sets | Low | No — document behavior |
| 2 | Select columns: unknown options auto-created | Low | No — acceptable behavior |
| 6 | Geolocation: partial data accepted | Low | Yes — require both lat/lng |
| 8 | POST /rows/ ignores `convert_keys` in response | Low | No — feature request |
| 10 | Typo: "row _id not exits" | Low | Yes — fix typo |
| 11 | Multiple typos in dtable-web ("does not exits") | Low | Yes — fix typos |
| 13 | deleteUserShare missing requestBody in spec | Low | Fixed in this repo |
| 14 | createWebhook returns 200 instead of 201 | Low | Yes — return 201 |
| 15 | createGroupShare returns 200 instead of 201 | Low | Yes — return 201 |
| 16 | group_id returned as string instead of integer | Low | Yes — return integer |
| 18 | listColumns excludes auto-created Name column | Low | No — document behavior |
| 19 | deleteGroup fails silently-ish when group has bases | Low | Fixed in this repo |
| 20 | Ping endpoints: inconsistent response formats | Low | Fixed in this repo |

---

## High Severity

### 1. Checkbox: integer `1` is stored as `false`

**Severity:** High — silent data corruption

When writing `1` (integer) to a checkbox column, SeaTable stores `false` instead of `true`. Only the boolean `true` is accepted. An LLM/agent might reasonably send `1` as a truthy value.

```
Input:  { "Checkbox": 1 }
Stored: { "Checkbox": false }   ← expected: true
```

**Recommendation:** Return an error if the value is not a boolean, or coerce truthy values (`1`, `"true"`) to `true`.

---

## Medium Severity

### 21. Auth errors: 403 returned instead of 401 for missing or invalid tokens

**Severity:** Medium — incorrect HTTP semantics

Per RFC 9110, HTTP status codes have distinct meanings:

- **401 Unauthorized** = "You are not authenticated" — the request lacks valid credentials
- **403 Forbidden** = "You are authenticated, but not authorized" — the server understood the credentials but the user lacks permission

SeaTable uses 403 in cases where 401 would be correct:

| Situation | Actual | Expected |
|-----------|--------|----------|
| No token → account endpoint | 403 | **401** |
| Invalid token → account endpoint | 401 | 401 |
| No token → base endpoint | 403 | **401** |
| Invalid token → base endpoint | 403 | **401** |
| Regular user → admin endpoint | 403 | 403 |

The last case (authenticated user lacking admin privileges) correctly returns 403. But missing or invalid tokens should return 401, because the problem is failed authentication, not insufficient authorization.

This distinction matters in practice: API clients can automatically attempt a token refresh on 401, but not on 403. When both cases return 403, the client loses the ability to distinguish "re-authenticate" from "you don't have access".

**Recommendation:** Return 401 for missing or invalid tokens. Reserve 403 for authenticated users who lack permission for the requested action.

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

### 9. DELETE /links/ reports success for non-existing links

**Severity:** Medium

Unlinking a row pair that doesn't exist returns `{ deleted_links_count: 1, success: true }` instead of `{ deleted_links_count: 0 }`.

**Recommendation:** Return the actual count of deleted links.

### 12. No createRowComment endpoint

**Severity:** Medium

There is no API endpoint to create a row comment. The `create_row_comment` schema exists in `base_operations.yaml` but no POST operation is defined on `/api-gateway/api/v2/dtables/{base_uuid}/comments/` (returns 405 Method Not Allowed).

**Status:** Will be re-added in 6.2.

### 17. addNewUser returns 403 for license limit

**Severity:** Medium

`POST /api/v2.1/admin/users/` returns `403 {"error_msg": "The number of users exceeds the limit."}` when the license user limit is reached. A 403 typically means insufficient permissions, which is misleading. A 409 Conflict or 402 Payment Required would be more appropriate.

### 22. updateColumn to link type creates broken column

**Severity:** Medium — data integrity

Changing a column's type to `link` via `updateColumn` creates a broken column that shows a blank page when opening column settings in the UI. This happens regardless of whether `column_data` is provided with `table` and `other_table` values.

**Recommendation:** Validate that the required `column_data` fields for link columns are present and valid, or reject the type change with a clear error.

---

## Low Severity

### 23. Temporary API-Token creation uses GET instead of POST

**Severity:** Low — REST convention violation

`GET /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/temp-api-token/` creates a new temporary API token. By REST conventions, resource creation should use POST, not GET. GET requests should be idempotent and safe.

**Recommendation:** Change to POST. This is a breaking change, so it may need a deprecation period.

### 24. app_name inconsistently used as path parameter vs body parameter

**Severity:** Low

The `app_name` parameter is used as a body parameter when creating an API token (`POST .../api-tokens/`) but as a path parameter when updating or deleting one (`PUT/DELETE .../api-tokens/{app_name}/`).

**Assessment:** This is intentional — the name is set during creation (body) and used as identifier afterwards (path). But it could be confusing for API consumers.

### 25. Base-Token endpoints return different field sets

**Severity:** Low — inconsistent but functional

The two base-token endpoints return different response fields:

| Field | `getBaseTokenWithApiToken` | `getBaseTokenWithAccountToken` |
|-------|:-:|:-:|
| `access_token` | yes | yes |
| `dtable_uuid` | yes | yes |
| `app_name` | yes | no |
| `dtable_server` | yes | no |
| `workspace_id` | yes | no |
| `use_api_gateway` | yes | no |
| `dtable_name` | yes | no |

**Assessment:** The extra fields from the API-Token endpoint are useful context. Consider adding them to the Account-Token endpoint as well for consistency.

### 2. Single-select / multiple-select: unknown options are auto-created

**Severity:** Low

Writing a non-existing option name to a select column silently creates the option in the column configuration. No error, no warning.

```
Input:  { "Single-Select": "option xyz" }
Result: New option "option xyz" created in column definition
```

Any typo or hallucinated option name permanently modifies the column schema.

**Assessment:** Acceptable behavior in most cases. A `create_if_missing` flag (default `true` for backward compatibility) would be a nice improvement.

### 6. Geolocation: partial data accepted

**Severity:** Low — incomplete data stored

A geolocation column with `geo_format: "lng_lat"` accepts objects with only one coordinate.

```
Input:  { "Geolocation": { "lng": 11.576 } }   ← lat missing
Stored: { "Geolocation": { "lng": 11.576 } }   ← no error
```

**Recommendation:** Require both `lat` and `lng` when writing.

### 8. POST /rows/ ignores `convert_keys` in response

**Severity:** Low — feature request

When creating rows with `convert_keys: true`, the response still returns column keys instead of column names.

```
Request:  POST /rows/ { table_name, rows, convert_keys: true }
Response: { "0000": "Test", "ZBoJ": 42, ... }   ← keys, not names
```

`GET /rows/` and `GET /rows/{id}/` correctly respect `convert_keys`.

**Assessment:** Not a bug, but a reasonable feature request for consistency.

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

### 13. deleteUserShare missing requestBody

**Severity:** Low

The `deleteUserShare` operation in `user_account_operations.yaml` had no `requestBody` defined, but the API requires `email` as form data in the request body.

**Fixed in:** This repository (commit 188837f).

### 14. createWebhook returns 200 instead of 201

**Severity:** Low

`POST /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/webhooks/` returns HTTP 200 on success. Creating a resource should return 201 Created per REST conventions.

### 15. createGroupShare returns 200 instead of 201

**Severity:** Low

`POST /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/group-shares/` returns HTTP 200 on success. Should return 201 Created. For comparison, `createUserShare` correctly returns 201.

### 16. group_id returned as string instead of integer

**Severity:** Low

`POST .../group-shares/` returns `group_id` as a string (e.g., `"44"`) in the response, but it is an integer everywhere else (path parameters, `listGroupShares` response).

### 18. listColumns excludes auto-created Name column

**Severity:** Low

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

### 26. getFileDownloadLink returns 400 instead of 404 for non-existent file

**Severity:** Low — inconsistent error codes

`GET /api/v2.1/dtable/app-download-link/?path=/files/2020-01/nonexistent.txt` returns 400 with `{"error_msg": "path ... not found."}`. In contrast, `DELETE /api/v2.1/dtable/app-asset/` correctly returns 404 with `{"error_msg": "File not found."}` for the same situation.

A missing file is a 404 case, not a 400 (bad request).

**Recommendation:** Return 404 from `getFileDownloadLink` when the file does not exist, consistent with `DeleteBaseAsset`.
