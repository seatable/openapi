---
title: Status Codes
excerpt: The HTTP response codes indicate success or error.
category: 6570d48363242f007fc436cf
isReference: true
slug: errors
---

<style>
.markdown-body {
	--markdown-title-marginTop: 2em;
}
</style>

SeaTable uses conventional HTTP response codes to indicate the success or failure of an API request. In general:

- Codes in the 2xx range indicate success.
- Codes in the 4xx range indicate an error that failed given information provided (e.g., a required parameter was omitted, a charge failed, etc.). Most 4xx errors include an error code that briefly explains the error reported.
- Codes in the 5xx range indicate an error with SeaTable's servers (these are rare).

## Success codes

| HTTPS status code | Description                                 |
| :---------------- | :------------------------------------------ |
| **200 - OK**      | SeaTable successfully processed the request |

## Error codes

| HTTPS status code                      | Description                                                                                      |
| :------------------------------------- | :----------------------------------------------------------------------------------------------- |
| **400 - Bad Request**                  | The request was unacceptable, often due to missing a required parameter.                         |
| **401 - Unauthorized**                 | No valid token provided or wrong format of the authorization header.                             |
| **402 - Request Failed**               | The parameters were valid but the request failed.                                                |
| **403 - Forbidden**                    | The provided token key doesn&#x27;t have permissions to perform the request.                     |
| **404 - Not Found**                    | The requested resource doesn&#x27;t exist.                                                       |
| **429 - Too Many Requests**            | Too many requests hit the API too quickly. We recommend an exponential backoff of your requests. |
| **500, 502, 503, 504 - Server Errors** | Something went wrong on SeaTable&#x27;s end.                                                     |
