# Google Scholar API

This Flask application provides a RESTful API to interact with [Google Scholar](https://scholar.google.com.au/) data via the [scholarly](https://github.com/scholarly-python-package/scholarly) Python package. It enables users to search for authors, retrieve author publications, search for publications, and find citations for specific publications, all through simple HTTP requests.

# Features
- Search for authors by name
- Retrieve an author's publications
- Search for publications by query
- Get citations for a specific publication

# Installation
## Prerequisites
- Python 3.6+
- Flask
- scholarly
## Setup
1. Clone this repository to your local machine.
2. Install the required packages: `pip install Flask scholarly`

# Running the API
Navigate to the project directory and run the Flask application:
`python main.py`

The API will be available at http://localhost:5000.

# API Endpoints
https://scholarly.readthedocs.io/en/stable/scholarly.html

## Welcome Message
URL: /
Method: GET
Description: Displays a welcome message in plain text.
## Search Author
URL: /search_author?name=<author_name>
Method: GET
Description: Searches for authors by name.
Example: [/search_author?name=Jodie%20Rummer](http://127.0.0.1:5000/search_author?name=Jodie%20Rummer)
## Author Publications
URL: /author_publications?author_id=<author_id>
Method: GET
Description: Retrieves publications for a specific author.
Example: [/author_publications?author_id=ynWS968AAAAJ](http://172.0.0.1:5000/author_publications?author_id=ynWS968AAAAJ)
## Access Author Information by Custom URL
URL: /search_author_custom_url?url=<custom_url>
Method: GET
Description: Accesses author information by a custom URL.
## Search Publications
URL: /search_publications?query=<search_query>
Method: GET
Description: Searches for publications by query / specific keyword.
Example: [/search_publications?query=Epaulette%20sharks](http://172.0.0.1:5000/search_publications?query=Epaulette%20sharks)
## Find Related Articles
URL: /get_related_articles?pub_id=<publication_id>
Method: GET
Description: Finds articles related to a specific publication.
## Cited By
URL: /cited_by?pub_id=<publication_id>
Method: GET
Description: Retrieves citations for a specific publication.
Example: [/cited_by?pub_id=ynWS968AAAAJ:u5HHmVD_uO8C](http://172.0.0.1:5000/cited_by?pub_id=ynWS968AAAAJ:u5HHmVD_uO8C)
## Download Mandates CSV
URL: /download_mandates_csv?filename=<filename>
Method: GET
Description: Downloads the mandates CSV file. This endpoint is for advanced usage and may require additional setup for file serving.

# Notes
Using proxies is highly recommended to prevent Google Scholar from blocking your requests. Adjust the ProxyGenerator settings as needed for your proxy configuration.
This API is intended for educational and research purposes. Please ensure to comply with Google Scholar's terms of service.

# Contributing
Contributions are welcome! Please fork the repository and submit pull requests with any enhancements or bug fixes.

# License
This project is open-sourced and released under the [Unlicense](http://unlicense.org/).