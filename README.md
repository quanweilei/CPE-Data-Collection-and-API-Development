# CPE-Data-Collection-and-API-Development
This assignment is designed to evaluate your ability to work with XML data, interact with databases, and build a RESTful API to expose the data.

In order to run this application you must first run Step1 to parse the xml file into an xlsx file, then run Step2-3 to create a localhost database, RESTful API, and local website.

# Step 1
This script parses a local XML file containing CPE data (version 2.3) and exports key information into an Excel spreadsheet. It uses Python’s xml.etree.ElementTree to read and navigate the XML structure, and openpyxl to generate the Excel file. The script auto-detects XML namespaces, extracts fields such as the CPE title, CPE 2.2 and 2.3 URIs, reference links, and any deprecation flags directly from the XML. Originally, the script included functionality to call the NVD API to retrieve CPE 2.3 deprecation dates, but those API calls have been commented out to avoid rate-limiting and blocking issues (I called the NVD API too frequently and got IP blocked). As a result, the “CPE 23 Deprecation Date” column in the output file will remain blank. The script produces a file named cpe_data.xlsx, which contains a structured summary of each CPE entry from the XML source. I am not very experienced with NVD API calling so I was unable to figure out how to check if the date of the CPE was deprecated (CPE 22/23 Deprecation Date).

# Step 2
In Step 2, I created a Flask application that reads the cpe_data.xlsx file generated from Step 1 and all of the data into a SQLite database using SQLAlchemy. I defined a CPE model to match the schema of the Excel file, including fields such as title, CPE 2.2 and 2.3 URIs, references, and deprecation info. If the database doesn’t already contain data, the script will populate it with those entries when the Flask app starts. A basic index page (/) is also implemented to display the data using Jinja and Bootstrap. To test I only used a population of 50 from the excel file in order to reduce runtime and setup.

This step ensures that the extracted CPE data is persistently stored and made queryable by both frontend and backend components. The structure sets up the foundation for exposing the data through a RESTful API in the next step.

The Database is automatically saved into a db file named cpe_data.db, and is stored in the same directory. If detected already existing, then flask will use that db file instead of creating one from scratch. 

Using the given schema, the SQLAlchemy schema is 

| Column Name           | Data Type    | Description                                                                   |
| --------------------- | ------------ | ----------------------------------------------------------------------------- |
| `id`                  | Integer (PK) | Auto-incrementing primary key for each entry                                  |
| `title`               | String       | The CPE product title (from the `<title>` tag in XML or “CPE Title” in Excel) |
| `cpe_22_uri`          | String       | The CPE 2.2 URI (from the `name` attribute of `<cpe-item>`)                   |
| `cpe_23_uri`          | String       | The CPE 2.3 URI (from the `name` attribute of `<cpe-23-item>`)                |
| `references`          | String       | Comma-separated reference URLs from the XML file                              |
| `deprecated_22`       | String       | Whether the CPE 2.2 URI is deprecated (true/false)                            |
| `deprecation_date_23` | String       | Deprecation date for CPE 2.3 entry (manually entered or fetched via API)      |


# Step 3
In Step 3, I implemented RESTful API endpoints to retrieve and filter the CPE data stored in the database. The /api/cpes endpoint supports pagination via optional page and limit query parameters. By default, it returns 10 entries per page.

The /api/cpes/search endpoint enables powerful query-based search. Clients can search CPEs by:

cpe_title (case-insensitive substring match)

cpe_22_uri and cpe_23_uri (partial match)

deprecation_date (returns all CPEs deprecated on or before the given date in either CPE 22 or 23)

The app uses SQLAlchemy to dynamically build queries based on whichever filters are provided. The logic ensures flexibility in search without overcomplicating the client interface. This fulfills the rubric’s expectations for filtering and search functionality, and the output is returned in JSON format for easy integration into any frontend or API consumer.

# FrontEnd
The frontend of this project is a simple HTML interface styled with Bootstrap 5, designed to interact with the backend RESTful API and present the CPE data in a user-friendly format. It includes a search bar at the top of the page that allows users to filter CPE entries by title. When a search is submitted, the query is passed to the backend and filtered results are returned and rendered. The main content is a table that displays relevant information for each CPE entry, including the title, CPE 2.2 URI, CPE 2.3 URI, reference links, deprecation status, and deprecation date. If no entries match the search criteria, a fallback message is shown indicating that no results were found. The frontend uses Flask’s Jinja2 templating engine to dynamically render the data passed from the server. The HTML template is located in the templates directory and communicates with Flask routes such as / and /api/cpes to retrieve and display data.