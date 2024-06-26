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
2. Install the required packages:`pip install Flask scholarly` or `pip3 install -r requirements.txt` 

# Running the API in development mode
Navigate to the project directory and run the Flask application:
`python ./api/index.py` or `python3 ./api/index.py`

The API will be available at http://localhost:5000.

`pm2 start ./api/index.py --interpreter python3 --name scholarly`

# Using Proxies

## Free Proxies
Just uncomment the proxy code

## To use scraperapi.com

Uncomment the proxy code and add an environment variable.

For Temporary Use: You can set an environment variable in your current terminal session. The exact command depends on your shell. For most Unix-like systems (like macOS or Linux), you can use:
`export SCRAPER_API_KEY='your_scraperapi_key_here'`

If you're using Windows Command Prompt, the command will be:
`set SCRAPER_API_KEY=your_scraperapi_key_here`
And for PowerShell:
`$env:SCRAPER_API_KEY="your_scraperapi_key_here"`

For Permanent Use: Add the export or set command to your shell's profile script (like .bashrc, .bash_profile, .zshrc, etc.), so the environment variable is automatically set in future terminal sessions.

Or use dotenv
```
from dotenv import load_dotenv
load_dotenv()
```

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

Parameter: name

Example: [/search_author?name=Jodie%20Rummer](http://127.0.0.1:5000/search_author?name=Jodie%20Rummer)
## Get Author
URL: /search_author_id?id=<author_name>

Method: GET

Description: Searches for authors by id.

Parameter: id

Example: [/search_author_id?id=ynWS968AAAAJ](http://127.0.0.1:5000/search_author_id?id=ynWS968AAAAJ)
## Search Organisation
URL: /search_org?query=<query>

Method: GET

Description: Searches author by organisation.

Parameter: query

Example: [/search_org?query=James%20Cook%20University](http://127.0.0.1:5000/search_org?query=James%20Cook%20University)
## Search Keyword
URL: /search_keyword?query=<query>

Method: GET

Description: Searches keyword.

Parameter: query

Example: [/search_keyword?query=test](http://127.0.0.1:5000/search_org?query=test)
## Get Coauthors
URL: /get_coauthors

Method: GET

Description: Retrieves collaborators for a specific author.

Parameter: author_id

Example: [/get_coauthors?author_id=ynWS968AAAAJ](http://172.0.0.1:5000/get_coauthors?author_id=ynWS968AAAAJ)
## Author Publications
URL: /author_publications?author_id=<author_id>

Method: GET

Description: Retrieves publications for a specific author.

Parameter: author_id

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
## Find Related publications
URL: /get_related_publications?pub_id=<publication_id>

Method: GET

Description: Find articles related to a specific publication.

Example: [/get_related_publications?pub_id=4DMP91E08xMC](http://172.0.0.1:5000/get_related_publications?pub_id=4DMP91E08xMC)
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
This API is intended for educational and research purposes. Please ensure that you comply with Google Scholar's terms of service.

# Contributing
Contributions are welcome! Please fork the repository and submit pull requests with any enhancements or bug fixes.

```
python -m venv venv
source venv/bin/activate
```

# License
This open-sourced project is released under the [Unlicense](http://unlicense.org/).
