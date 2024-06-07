---
title: Introduction
excerpt: This is the reference for the SeaTable API. On this page you will find everything you need to use the SeaTable API.
category: 65e6ef8514da74005d339fac
isReference: true
slug: introduction
---

<style>
.markdown-body {
	--markdown-title-marginTop: 2em;
}
details > p, details > div, details > ul, details > pre {
  margin-left: 30px;
}
summary {
  font-size: 1.1rem !important;
}
</style>

The SeaTable API is organized around REST. Our API has predictable resource-oriented URLs, accepts form-encoded request bodies, returns JSON-encoded responses, and uses standard HTTP response codes, authentication, and verbs.

Take a look at our [development quick start guide](https://seatable.io/docs/?lang=auto) for concrete examples or guided first steps. Or if you are not a developer, use [SeaTable’s no-code Integrations](https://seatable.io/integrationen/?lang=auto) like Zapier, Make.com or N8n to get started with SeaTable without any coding required. Almost all resources can be found in our [Help Area](https://seatable.io/docs/?lang=auto).

## Prerequisites

Before you begin, ensure that you have a SeaTable Cloud account. If you have no account, please [register](https://seatable.io/registrierung/?lang=auto) for a free SeaTable Cloud account.

## Get started with the SeaTable API

Start experimenting with SeaTable API using this website, which lets you run SeaTable API commands directly from your browser. You need no testing environment, you can start right away to work with your bases, tables and rows via the SeaTable API.

> 👍 No user data leaves your browser
>
> Everything what you do on this website, happens solely on your browser. Every API-Request is send directly from your browser to SeaTable Cloud. Therefore you don't have to worry. You can enter and use your real credentials and tokens.

<!-- ## SeaTable API within 30 seconds

[SeaTable API within 30 seconds](https://youtu.be/aUcd1BzbaiA "@embed") -->

## Examples of what you can do with the SeaTable API

So don't let us waste time and let's start right away. The first step with every API is to think about what you want to do. Here are some examples:

<details>
  <summary><strong>Write data to a base and read it out again</strong></summary><hr>

### Step 1: Create an API-Token

The first step is to create an `API-Token` with write permission for one of your bases at SeaTable Cloud. If you don't know how to do this, check this [help article](https://seatable.io/docs/seatable-api/erzeugen-eines-api-tokens/?lang=auto). You only have to do this once! The `API-Token` keeps valid forever for this specific base. Of course you can generate as many `API-Tokens` as you want. You can even use the API to [generate additional API-Tokens](https://api.seatable.io/reference/createapitoken).

An API-Token might look like this: `1de50f1a57143bfe72873cbbd28ecb4de9eb3c61`

### Step 2: Generate Base-Token

Next you need the API-Token to [generate a Base-Token](https://api.seatable.io/reference/getbasetokenwithapitoken). The `Base-Token` is only valid for three days and exactly for the one base for which you created the API-Token. If you want to interact with your base more frequently via API, you need to repeat this step. You need the `Base-Token` to authenticate all the following API requests.

The result of the [Get Base-Token with API-Token](https://api.seatable.io/reference/getbasetokenwithapitoken) request might look like this. Write down all values, you will need them in the following. The `access_token`, this long string of characters, is what we will call a `Base-Token` in all future requests. The `dtable_uuid` is equivalent to `base_uuid`.

```json Example response with the Base-Token (access_token) and base_uuid (dtable_uuid)
{
  "app_name": "my first api token",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2ODA0NDcxMTQsamX0YWJsVZ80dWlkIjoiZmJlMTZkNzMtYjI4Zi00YWY4LWIzOWQtZDc4YzU3YTg4YjkwIiwidXNlcm5hbWUiOiIiLCJwZXJtaXNzaW9uIjoicnciLCJhcHBfbmFtZSI6InRlc3QifQ.huQz07WOQUvaJNy2bTR2iRm0-oATjaMGPAAIYtpkZjU",
  "dtable_uuid": "fb3f1d72-b28f-3af8-a29d-d78c57a88b90",
  "dtable_server": "https://cloud.seatable.io/dtable-server/",
  "dtable_socket": "https://cloud.seatable.io/",
  "dtable_db": "https://cloud.seatable.io/dtable-db/",
  "workspace_id": 234,
  "dtable_name": "My Base"
}
```

### Step 3: Get to know the structure of your base

Equipped with the `Base-Token` we can start to display the current structure of the base. Use the [Get Metadata](https://api.seatable.io/reference/getmetadata) request and pass the `Base-Token` and the `base_uuid` as parameters. The result will be a very long _metadata_ object which contains all _tables_ with all their _columns_ and _views_. The _metadata_ does not contain any data, it contains only the structure of your base.

Use the small arrows in the response box to fold the elements to get an overview of the complete object. The result might look like this:

```json Example of the metadata object
{
  "metadata": {
    "tables": [
      {
        "_id": "0000",
        "name": "Table1",
        "columns": [{
            "name": "First name",
            ..
        },
        {
            "name": "Last name",
            ..
        }],
        "views": [..]
      }
    ],
    "version": 482,
    "format_version": 7,
    "settings": {..}
  }
}
```

Note down the name of the tables and the name of the columns. You will need these values to write a new row to this table.

### Step 4: Write some data to your base

The request to [Add a row](https://api.seatable.io/reference/addrowdeprecated) to a base, requires the following information. You have to know ...

- the `Base-Token` for authentication -> ok
- the `base_uuid` to identify the base -> no problem
- the `table_name` -> you should know this from the last request
- and you have to define the row object, meaning that you have to tell the API what values you want to write to the table.

At first it looks difficult to define the row object, but in fact it is quite easy. The row object consists of key:value pairs. The key is the name of the column and the value is that what you want to write to the base. So if you want to create a line with **John Doe**, then the row object looks like this:

```json Row object, writing some values to the columns with the name First name and Last name.
{
  "First name": "John",
  "Last name": "Doe"
}
```

Easy, right? This documentation helps you to create the API request just by filling out all the input fields. The code that is generated in the right black box, is the API request that you can execute either via this page or with any programming language.

### Step 5: Get all rows of your base

Also this last step is quite easy. Use the [List rows](https://api.seatable.io/reference/listrows) request and fill all mandatory input fields. Leave all optional fields blank and hit the **Try It!** button. You should see your previously created line with John Doe now in the result list.

Congratulations! You wrote your first row to a table in a base in SeaTable via the API and then retrieved it.

<hr></details>

<details>
  <summary><strong>Create a new base, a new table and add two new columns</strong></summary><hr>

### Step 1: Generate an Account-Token

SeaTable requires a different authentication depending on whether you want to do something inside a base or outside. To create a Base, we need an account token, which we can generate with our credentials. Therefore you have to use the [Get Account-Token with Username and Password](https://api.seatable.io/reference/getaccounttokenfromusername). Fill in your username and password and hit **Try It!**. The result will be your `Account-Token` which might look like this:

```json
{
  "token": "25285a3da6fff1f7a6f9c9abc8da12dcd2bd4470"
}
```

### Step 2: Find out the workspace id

To generate a base inside SeaTable you have to tell SeaTable where the base should be created. It could be in the area of `My bases` or it could be in one of your groups. To define the target where you want to create a base you have to provide the `workspace_id`. The easiest way to determine the workspace id of a group or `My bases` is to open a base of that area in the browser and look at the URL. This [help article](https://seatable.io/docs/arbeiten-mit-gruppen/workspace-id-einer-gruppe-ermitteln/?lang=auto) explains this in more details. Open the base and write down the workspace id.

### Step 3: Create the base

Equiped with all these information it should be easy for you to create a new base. Use the request [Create base](https://api.seatable.io/reference/createbase) and fill out all the required values and hit
**Try It!**. Every new base will automatically contain a first empty table with the name `Table1`.

### Step 4: Create a table and two columns (you will need a Base-Token)

The following requests have to be executed inside the base. There the necessary API calls can be found in the area **Base operations** and you will need a [Base-Token](https://api.seatable.io/reference/getbasetokenwithapitoken) instead of an account-token. Check example no. 1 if you don't know how to create a Base-Token.

Next we [create a table](https://api.seatable.io/reference/createtable) and call it `Table 2`. You can already define as many columns as you want that should be created.
But even after the initial creation you could [append new columns](https://api.seatable.io/reference/appendcolumns-1) at every time you want. Open the base with your browser and you will immediately see the new table with the new columns.

Congratulations! You created your first base with a seconds table and some extra columns.

<hr></details>

<details>
  <summary><strong>Update the content of a specific row</strong></summary><hr>

### Step 0: Generate a Base-Token

Generate a Base-Token like in example no. 1. This will also give you the `base_uuid`.

### Step 1: Determine the row you would like to update

To [update a row](https://api.seatable.io/reference/updaterow) you need to know the row_id you want to update. You can either get the `row_id` just by [opening the row details in the browser](https://seatable.io/docs/haeufig-gestellte-fragen/was-ist-die-zeilen-id/?lang=auto) or you could use one of the various API requests to get the content of a base:

- [List Rows (with SQL)](https://api.seatable.io/reference/querysql)
- [List Rows](https://api.seatable.io/reference/listrows)
- [Base Info](https://api.seatable.io/reference/getbaseinfo)

### Step 2: Update the row

Next you have all the information to [update a row](https://api.seatable.io/reference/updaterow). You can easily update multiple values in the row specified by the `row_id`. The `row` object contains `key:value` pairs with the column name as key and the desired values.

<hr></details>

<details>
  <summary><strong>Upload a file to a file column</strong></summary><hr>

### Step 0: Prerequisites

I assume that you already have a base with a table in which a file column exists. In addition I assume that you know how to generate a [Base-Token](https://api.seatable.io/reference/getbasetokenwithapitoken) from an API-Token. If not, check out the first example.

### Step 1: Generate an upload link for this base

First we have to [generate an upload link](https://api.seatable.io/reference/getuploadlink). Be aware that this requests needs the API-Token for authentification, because technically speaking it does not happen inside a base.

The result will be look like this:

```json Temporary upload link, generated with the SeaTable-API
{
  "upload_link": "https://cloud.seafile.com/seafhttp/upload-api/83e701c8-84ba-498c-91b1-ddb3789edb7e",
  "parent_path": "/asset/a275d870-fd55-48e4-8c4a-5fd6f2549765",
  "img_relative_path": "images/2021-08",
  "file_relative_path": "files/2021-08"
}
```

This is a temporary path, where SeaTable accepts new files that can be uploaded either to an images or a files directory.

### Step 2: Upload the file

Next you have to really upload the file to the base. The right API request is [Upload a file](https://api.seatable.io/reference/uploadfile).
You have to provide the information you received from the last call. Don't get confused about `parent_path` and `parent_dir`. These are just the same values.

Here is the input you should use: (example data)

- upload_link: **83e701c8-84ba-498c-91b1-ddb3789edb7e**
- file: **(select your file)**
- parent_dir: **/asset/a275d870-fd55-48e4-8c4a-5fd6f2549765**
- relative_path: **files/2021-08**

As soon as you uploaded the file, it can be found via the [file management of the base](https://seatable.io/docs/dateien-und-bilder/das-dateimanagement-einer-base/?lang=auto).
To append the file an image or file column, you still need another API request.

### Step 3: Update an existing file/image column

Now you have to [update a row](https://api.seatable.io/reference/updaterow) and write the required information of the previously uploaded file to the right file/image column.
Do not be confused by the fact that the upload of a file and an image is different. The `row` element has to be different. In case of an image you just have to provide the internal URL of the image as an array item. In cas of a file you have to provide more informations as an object.

```json Example how to add an already uploaded image to a row:
"row": {
  "My Image Column": [
    "/workspace/24/asset/a275d870-fd55-48e4-8c4a-5fd6f2549765/images/2023-07/party.png"
  ]
}
```

```json Example how to add an already uploaded file to a row:
"row": {
  "My File Column": [
    {
    "name": "invoice.pdf",
    "size": 101454,
    "type": "file",
    "url": "/workspace/24/asset/a275d870-fd55-48e4-8c4a-5fd6f2549765/images/2023-07/invoice.pdf"
    }
  ]
}
```

<hr></details>

<details>
  <summary><strong>Get more information about your team (as team admin)</strong></summary><hr>

### Step 0: Prerequisites

The following example can only be executed as team admin. All requests require an `account-token` that you can generate with your username and password. An API-Token or a Base-Token is useless in this case because we will only execute requests from the area **Account Operations - Team Admin**.

### Step 1: Get an Account-Token

Start with the call [Get Account Token](https://api.seatable.io/reference/getaccounttokenfromusername). It requires your username and password and will return your `account-token`. Threat this token like your password, because it can be used to execute all types of account operations.

```json
{
  "token": "25285a3da6fff1f7a6f9c9abc8da12dcd2bd4470"
}
```

### Step 2: Get info about your team and your team members

As soon as you have your `account-token` it is easy to get more information about your team and your team members. Use one of the following calls:

- [Get Team Info](https://api.seatable.io/reference/getteaminfo)
- [List Team Members](https://api.seatable.io/reference/listteamusers-1)
- [List Team Bases](https://api.seatable.io/reference/listbases)

Great. Now you can get all the information of your team via API.

<hr></details>

<details>
  <summary><strong>Create a new user and enforce 2FA for this user</strong></summary><hr>

### Step 1: Get an Account-Token

Like as in the last example, start with the call [Get Account Token](https://api.seatable.io/reference/getaccounttokenfromusername).

### Step 2: Get the user id of the user

To enforce 2-Factor-Authentification (2FA) for one of your team members, you need the `email` (sometimes also call `user_id`). Every user has a unique email adress like `123456789f1e4c8d8e1c31415867317c@auth.local`. Use [List Team Members](https://api.seatable.io/reference/listteamusers-1) to get this unique value of the user you want to update.

### Step 3: Enforce 2FA

Equipped with this `email` of the user, you can [Enforce 2FA](https://api.seatable.io/reference/enforcetwofactor-1) for this user. The next time the user opens SeaTable in his browser, he has to register for 2FA.

<hr></details>
