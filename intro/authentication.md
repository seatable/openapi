---
title: Authentication
excerpt: Learn to master the authentication flows of SeaTable.
category: 64464593226b5605dde1b0e2
isReference: true
slug: authentication
---

<style>
.markdown-body {
	--markdown-title-marginTop: 2em;
}
</style>

Almost every SeaTable API requests require an authentication via authentication-header. The only exceptions are the request's **Ping** and the **Server Info Request**. These two requests don't require an authentication.

All other API-requests require an authorization header that looks like this, where different tokens can be used.

`Authorization: Bearer {{Account-Token, API-Token or Base-Token}}`

> 🚧 Self-hosted SeaTable need configuration change
> 
> The **Try It!** function of this page works out of the box with SeaTable Cloud. But if you host your own SeaTable Server you have to [change your nginx configuration](/reference/requirement-self-hosted) to use this great feature. 

> 📘 Bearer or Token?
> 
> Before version 4.0, the authentication header in SeaTable was not like `Authorization: Bearer` but `Authorization: Token`. Starting with version 4.0 both authentication headers are supported. We recommend the use of `Authorization: Bearer`, according to the official (OpenAPI 3.0 Specifiation)[https://swagger.io/docs/specification/authentication/bearer-authentication/].

## Authentication Flows in SeaTable

Initially, authentication in SeaTable can seem a bit complicated, but the following graphic should make it clearer.

![Authentication Flow in SeaTable](https://seatable.io/wp-content/uploads/2023/03/authentication-flow-in-seatable2.png)

Every account operation requires an Account-Token. Every base operation requires an Base-Token, whereby there are four different ways to generate an Base-Token.

***

## The three tokens

> 📘 Account-Token
>
> An **Account-Token** authenticates an _account API request_ (=Account Operations) like add a new base, add a group member or list all collaborators of a base. The Account-Token can be generated with the account-credentials.

> 📘 API-Token
>
> An **API-Token** is like a password to use the API requests of a single base. The main purpose of an API-Token is to generate a Base-Token.
> You can create as many API-Token per base as you want. Every API-Token can have different read or write permissions. This token is valid until you delete them.

> 📘 Base-Token
>
> A **Base-Token** authenticates a _base API request_ (=Base Operations) like add a new row, append a row or delete a row. The Base-Token can be generated in many ways. The most common way is to use an API-Token.
> The read/write permission of an Base-Token depends on the read/write permission of the API-Token or the Account-Token it's generated from. Base-Token are valid for 3 days, therefore these must be generated regularly.

Here are the differences between these three tokens:

| TOKEN         | LENGTH    | EXPIRATION | GRANTED PRIVILEGES                                                                   |
| :------------ | :-------- | :--------- | :----------------------------------------------------------------------------------- |
| Account-Token | 40 chars  | never      | account privileges (user, team-admin, system admin)                                  |
| API-Token     | 40 chars  | never      | allows generating a Base-Token for a specific base with either read or write access  |
| Base-Token    | 249 chars | 3 days     | allow executing a Base-Operation with either read or write access to a specific base |

> ❗ Keep your Tokens secure!
> 
> An Account-Token or an API-Token replaces the combination of username & password in a SeaTable API request. Once generated, such a Token is valid permanently. 
> Therefore your Tokens have the same sensibility as your username and password, so make sure keep them in a safe place!

### Token Hierarchy

If you are working with the SeaTable API for the first time, the three different API-Tokens can be confusing. With a few exceptions, the following rule should help you:

- For all account operations, you need an account token. You create this token with your credentials.
- For practically all base operations, you require a base token. You generate this from an API token.

Otherwise, it can be said that the Account-Token is the most powerful token because you can generate the other two tokens with it. With the API token, on the other hand, you can only generate a base token, and the base token can only be used to execute base operations. We call this the Token-Hierarchy of SeaTable.

### Security

Treat your tokens like passwords, so be sure to keep them secure! Do not share your secret **API-Tokens** in public accessible areas such as GitHub, client-side code, and so forth. All API requests must be made over HTTPS. Calls made over plain HTTP will fail. API requests without authentication will also fail.

### Team Admin vs. System Admin

Account-Operations differentiate between User, Team Admin and System Admin. These are the three possible roles a user can have within SeaTable. Each user always has the User permission. The Team Admin or System Admin role must also be assigned to a user, and Team Admins only exist if teams/organizations are enabled in SeaTable. This is the case with <https://cloud.seatable.io>, but is typically not the case with self-hosted SeaTable instances.

More details on SeaTable's team/organization structure and admin management can be found at <https://seatable.io/docs/>.
