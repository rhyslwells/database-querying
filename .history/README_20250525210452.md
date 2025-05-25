# SQLite DB Viewer & Query Tool


A **Streamlit-based** application to upload, explore, and query **SQLite databases** entirely in memory. 

This tool supports:
* Uploading `.db` files or loading a sample database
* Executing SQL queries and viewing results
* Visualizing ER diagrams via Mermaid.js
* Downloading modified versions of the database

The [application](https://database-querying.streamlit.app/).

## Features

* **Upload or load a sample database**
  Load a bundled sample (`longlist.db`) or upload your own SQLite database.

* **Interactive SQL query interface**
  Run queries with real-time feedback and view results as DataFrames.

* **Example SQL queries**
  Predefined queries help users get started or understand the data schema.

* **ER Diagram generation**
  Visualizes database relationships using Mermaid syntax.

* **Download database**
  After executing queries or changes, download the in-memory database to disk.


