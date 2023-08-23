---
title: Models
excerpt: This page describes the different objects used in SeaTable.
category: 64e5a881a6e8f4004e8bb277
isReference: true
slug: models
---

<style>
.markdown-body {
	--markdown-title-marginTop: 2em;
}
</style>

## A Row

A rows object consists of a key:value pairs. The keys are the column_names (or the column_ids) and the values are the concrete content of the column. The following example and explanation should help to create a correct row object.

```json Example row object (with column names)
{
    "_id": "Qtf7xPmoRaiFyQPO1aENTjb",
    "_ctime": "2021-02-09T12:23:17.761+00:00",
    "_mtime": "2021-03-10T16:19:31.761+00:00",
    "_creator": "145504ae043c438cbb55f2afb084d586@auth.local",
    "_last_modifier": "145504ae043c438cbb55f2afb084d586@auth.local",
    "Book-Title": "The Great Gatsby",
    "Publishing Date": "1925-04-10",
    "Reviews": [
        {
            "row_id": "aG-P7aRoSPi_wauvv60fsA",
            "display_value": "Wallstreet Journal"
        },
        {
            "row_id": "Mr-3QnQ5Q-eeEqFBevtOkw",
            "display_value": "Google News"
        }
      ],
    "Author": [
        "145504ae043c438cbb55f2afb084d586@auth.local"
    ],
    "Cover": [
        "https://cloud.seatable.io/workspace/9463/asset/91a1ec23-2db0-4812-bbf5-5772352a4d63/images/2023-03/book-cover.png"
      ],
    "Selling Price": 48
    "Summary": "In my younger and more vulnerable years my father gave me some advice that I’ve been turning over in my mind ever since.\n\n‘Whenever you feel like criticizing any one,’ he told me, ‘just remember that all the people in this world haven’t had the advantages that you’ve had.’\n\n", 
}
```
```json Example row object (with column ids)
{
    "_id": "Qtf7xPmoRaiFyQPO1aENTjb",
    "_ctime": "2021-02-09T12:23:17.761+00:00",
    "_mtime": "2021-03-10T16:19:31.761+00:00",
    "_creator": "145504ae043c438cbb55f2afb084d586@auth.local",
    "_last_modifier": "145504ae043c438cbb55f2afb084d586@auth.local",
    "d9W1": "The Great Gatsby",
    "UYOZ": "1925-04-10",
    "J5ds": [
        {
            "row_id": "aG-P7aRoSPi_wauvv60fsA",
            "display_value": "Wallstreet Journal"
        },
        {
            "row_id": "Mr-3QnQ5Q-eeEqFBevtOkw",
            "display_value": "Google News"
        }
      ],
    "XX98": [
        "145504ae043c438cbb55f2afb084d586@auth.local"
    ],
    "d9W1": [
        "https://cloud.seatable.io/workspace/9463/asset/91a1ec23-2db0-4812-bbf5-5772352a4d63/images/2023-03/book-cover.png"
      ],
    "38WE": 48
    "Summary": "In my younger and more vulnerable years my father gave me some advice that I’ve been turning over in my mind ever since.\n\n‘Whenever you feel like criticizing any one,’ he told me, ‘just remember that all the people in this world haven’t had the advantages that you’ve had.’\n\n", 
}
```

As you can see in the example, due to the different column types, the values can have different formats and could be strings, integer, arrays or even objects. 

### Supported column types

| Column | Type | Example | Notice |
| :- | :- | :- | :- |
| `text`<br/>`email`<br/>`url` | `string` | `"Albert"` | | 
| `long-text` | `string`<br/>(markdown) | `"# Markdown syntax\n\nNew line with some **bold text**."` |
| `number`<br/>`percent`<br/>`dollar`<br/>`euro` | `integer` | `279` or `12.5344` | |
| `collaborator` | `array` | `["24...ab2@auth.local", "98...a3@auth.local"]` | | 
| `date` | `string`<br/>([ISO 8601 date and time in UTC](https://en.wikipedia.org/wiki/ISO_8601)) | ` "2021-07-01 13:59"` or <br/>`"2021-03-10T16:19:31.761+00:00"` | - seatable accepts a wide variety of date formats.<br/> - Always saved in iso format.<br/>- If "Accurate to minutes" is set, hh:mm will be ignored. | 
| `duration` | `string` | `"9:50"` or `"1:10:30"` | Depending on column setting. | 
| `single-select` | `string` | `"female"` | The exact string of the option is required. If the option doesn't exist, `option deleted` will be shown in the UI. |
| `multiple-select` | `array` | `["Option 1", "Option 2"]` | Non-existing options will be ignored. |
| `image` | `array` | `["/workspace/24/asset/.../heart.png", "https://seatable.io/logo.svg"]`| Images can be stored in two ways:<br/>- [uploading an image](https://api.seatable.io/reference/upload-file-image)<br/>- providing public URLs |
| `file` | `array` | `[{"name": "fav.ico", "size": 6746, "type": "file", "url": "..."}]` | You need to upload the file first, get its parent_path and file_relative_path first and then return to this call. | 
| `checkbox` | `boolean` | `true` | | 
| `rate` | `integer` | 4 |
| `geolocation` | `object` | `{"lng": 8.23..., "lat": 50.00...}` or<br/>`{"country_region": "Sweden"}` | Depending on column setting. |
| `formula` | `string` | `"Albert Summer"` | Contains only the result of the formula. |
| `button` | `null` | `null` | Always `null` | 
| `link` | `array` | `[{"row_id": "Mr-3QnQ5Q-eeEqFBevtOkw", "display_value": "Google News"}]` | |
| `digital-sign` | `object` | `{"username": "24...ab2@auth.local", "sign_image_url": "/digital-signs/2023-06/24...ab2@auth.local-1687426928723.png", "sign_time": "2023-06-22T09:42:08.761+00:00"}` | |  
| `_id` | `string` | `"Qtf7xPmoRaiFyQPO1aENTjb"` | Unique value inside a base and can not be changed. |
| `_ctime` | `string` | `"2021-02-09T12:23:17.761+00:00"` | Can not be changed. |
| `_mtime` | `string` | `"2021-02-09T12:23:17.761+00:00"` | Updates automatically. |
| `_archived` | `boolean` | `false` | |
| `_locked` | `boolean` | `true` or `null` | |
| `_locked_by` | `string` | `145504ae0...084d586@auth.local` | |

### Automatically filled column types

SeaTable offers some column types that are **filled automatically**. It is not possible to change the **value** of these columns by the user in the UI or with an `update row` request. These columns are:

- Column id (_id)
- Creation time (_ctime)
- Last modification time (_mtime)
- Lock status (_locked)
- Locked from person (_locked_by)
- Archived (_archived)
- Creator (_creator)
- Last modifier (_last_modifier)
- Auto number
- Button
- Formula
- Link formula

### Handling of default values

However, the **default values** of the text, number and single select column types won't be filled by the API request automatically. If you leave these fields blank, they'll also be blank after the new row is appended, which is different than the behavior on the web UI.

***

## A Link

Within SeaTable you can link a row to another row in the same table, or in another table of the same base. Links to another base are not possible. SeaTable supports all relation types like 1:1, 1:n or n:m.

> 📘 Links are bidirectional
>
> SeaTable does not know a direction of links. If you create a link from a column A to column B, it is the same like creating a link from column B to column A.

To create a link between two columns you will always need five informations. You need the two tables (identified by their name), the two columns that you want to link (identified by their row id) and the link_id. What makes it a little difficult is that the `link_id` is not the `column_id` or `column_key`. Use the [Get Metadata](/reference/get-metadata) to get the `link_id` of a link column.

```json Example object to create a link
{
  "table_name": "Table1",
  "other_table_name": "Table2",
  "link_id": "jYc7",
  "table_row_id": "Qtf7xPmoRaiFyQPO1aENTjb",
  "other_table_row_id": "aHVfgfy0RUiP8PYohm3K6w"
}
```
```json Example link object (after creation)
{
  "Qtf7xPmoRaiFyQPO1aENTjb": [
    {
      "row_id": "aHVfgfy0RUiP8PYohm3K6w",
      "display_value": "Albert"
    }
  ]
}
```



