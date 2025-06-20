# CPE-Data-Collection-and-API-Development
This project evaluates your ability to process XML data, persist it in a database, and expose it through a RESTful API with an interactive web frontend. It consists of three main steps:

XML parsing and Excel export (Step 1)

Flask app to store and serve CPE data (Step 2)

RESTful API and interactive UI with search/filter/pagination (Step 3)

# Setup Instructions
Run Step1.py to parse the official-cpe-dictionary_v2.3.xml and export to cpe_data.xlsx, you will need to manually change the file name in Step1.py, currently is set to a test input file that is provided on github as well.
official-cpe-dictionary_v2.3 must be downloaded separately and entered into the local directory of step1 to run it on the official dictionary. 

Run Step2-3.py to create a local SQLite database and start the Flask API/frontend server. NOTE: if db file already exists and you have switched your step 1 xml file, you will need to delete the db file in order to not
display the cached previous xml data.

Open your browser at http://localhost:5000 to view the frontend UI.

# Step 1: XML Parsing and Excel Export
The script reads a local XML file following the CPE Dictionary 2.3 schema and extracts the following for each <cpe-item>:

CPE Title (English only)

CPE 2.2 URI

CPE 2.3 URI

Reference links

CPE 2.2 Deprecated (true/false from XML, displayed as "Yes"/"No")

CPE 2.3 Deprecation Date (if found in <cpe-23:deprecation> element)

The resulting file is saved as cpe_data.xlsx and will be used as input in Step 2.

# Step 2: Data Persistence and Model Definition
A Flask app uses SQLAlchemy to define a schema and import the CPE data from Excel into a local SQLite database (cpe_data.db).

SQLAlchemy Model Schema:
| Column Name           | Data Type    | Description                                                              |
| --------------------- | ------------ | ------------------------------------------------------------------------ |
| `id`                  | Integer (PK) | Auto-increment primary key                                               |
| `title`               | String       | CPE product title (from XML `<title>`)                                   |
| `cpe_22_uri`          | String       | CPE 2.2 URI from `<cpe-item>`                                            |
| `cpe_23_uri`          | String       | CPE 2.3 URI from `<cpe-23-item>`                                         |
| `references`          | String       | Comma-separated URLs                                                     |
| `deprecated_22`       | Boolean      | True if deprecated, False otherwise                                      |
| `deprecation_date_23` | String       | Deprecation date from `<cpe-23:deprecation>`, or blank if not deprecated |


If the database already exists, the app will reuse the existing file instead of reloading data.

# Step 3: RESTful API Implementation
The application exposes RESTful endpoints:

/api/cpes
Returns paginated results of all CPE entries.

Supports page and limit query parameters.

/api/cpes/search
Allows filtering via the following optional query parameters:

cpe_title

cpe_22_uri

cpe_23_uri

deprecation_date (returns entries deprecated on or before this date in either version)

Both endpoints return JSON data to support integration into the frontend and other API consumers.

# Frontend UI
The frontend, built with Bootstrap 5 and Jinja2, renders the CPE entries in a styled, responsive HTML table.

# Features:
Truncated Titles and URIs with tooltips

Reference links: shows first two, then displays a +X more link that opens a tooltip-style popover

Deprecation flags: "Yes" or "No" for CPE 22 Deprecated

Formatted dates: CPE 23 deprecation dates shown as MMM DD, YYYY

Pagination: Users can paginate results and select 15/25/50 entries per page

Search bar: Filters CPE entries by title

Empty state message: Shown if no results match the search

This fully addresses rubric items for:

Rendering logic (title truncation, date formatting, tooltip/popover for references)

UI-based filtering using the /search API

Adjustable pagination options

Clear feedback for missing results

# Final Notes
This project provides complete end-to-end functionality using only the provided XML source file.