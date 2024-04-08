import os
import json
import time
from flask import Flask, jsonify, request, send_from_directory, signals
from flask_caching import Cache
from threading import Thread
from scholarly import scholarly, ProxyGenerator
from werkzeug.utils import secure_filename
import traceback
from logging import basicConfig, getLogger, INFO

app = Flask(__name__)
cachetime = 604800  # 7 days in seconds
cacheDir = "cache/"
# Flask-Caching configuration
app.config["CACHE_TYPE"] = "simple"  # Consider 'redis' or 'memcached' for production
app.config["CACHE_DEFAULT_TIMEOUT"] = (
    cachetime  # Cache duration in seconds (604800 seconds = 7 days)
)
cache = Cache(app)

basicConfig(level=INFO)
log = getLogger(__name__)


@app.after_request
def set_cache_header(response):
    """
    Modify the response to add Cache-Control headers.
    """
    # Set the Cache-Control header
    response.headers["Cache-Control"] = (
        "public, max-age=604800, stale-while-revalidate=86400"
    )
    return response


@app.route("/favicon.ico", methods=["GET"])
def favicon():
    try:
        return send_from_directory(
            os.path.join(os.path.dirname(app.root_path), ""), "favicon.ico"
        )
    except Exception as e:
        log(traceback.format_exc())
        return "An internal error has occurred!"


@app.route("/", methods=["GET"])
def index():
    return "Welcome to the scholarly API"


# https://scholarly.readthedocs.io/en/stable/quickstart.html
# Optional: Setup proxy
# Uncomment the following lines if you want to use free proxies.
# pg = ProxyGenerator()
# pg.FreeProxies()
# scholarly.use_proxy(pg)

# Uncomment the following lines if you want to use Scraper API proxies.
# pg = ProxyGenerator()
# success = pg.ScraperAPI(os.getenv("SCRAPER_API_KEY"))
# scholarly.use_proxy(pg)


def fetch_cache_author_by_id(author_id):
    try:
        author = scholarly.search_author_id(author_id)
        if not author or author is None:
            return None

        author = scholarly.fill(author)
        filled_publications = []
        for pub in author["publications"]:
            filled_pub = scholarly.fill(pub)
            filled_publications.append(filled_pub)
        author["publications"] = filled_publications

        sanitized_author_id = secure_filename(author_id) # Sanitize the author_id parameter
        with open(f"{cacheDir}id_{sanitized_author_id}.json", "w") as f:  # Use the sanitized author_id in the file path
            json.dump({"data": author, "timestamp": time.time()}, f)

        return author
    except Exception as e:
        log(traceback.format_exc())
        return None


def is_data_stale(timestamp):
    return time.time() - timestamp > cachetime


def get_author_data(author_id):
    sanitized_author_id = secure_filename(author_id.strip())
    filename = f"{cacheDir}id_{sanitized_author_id}.json"

    print(f"Checking for cache file: {filename}")

    if os.path.exists(filename):
        with open(filename, "r") as f:
            print("Cache found, checking if data is stale..")
            cache_content = json.load(f)
            # Serve cached data immediately
            data = cache_content["data"]
            if is_data_stale(cache_content["timestamp"]):
                print("Data is stale, refreshing in the background.")
                # Refresh data in the background if stale
                # if no threads started, start a new one
                thread = Thread(target=fetch_cache_author_by_id, args=(author_id,))
                thread.start()
                # thread.join()  # Wait for the thread to complete
            else:
                print("Data is fresh, serving cached data.")
            return data
    else:
        # No cache available, fetch data initially
        fetch_cache_author_by_id(author_id)
        return "Fetching data, please retry in a few moments."

def fetch_cache_author_search(name):
    sanitized_name = secure_filename(name)
    cache_file = f"{cacheDir}search_{sanitized_name}.json"
    
    search_query = scholarly.search_author(name)
    try:
        authors = []
        for _ in range(1):  # Fetch up to 1 author for simplicity
            author = next(search_query, None)
            if author is None:
                break
            author = scholarly.fill(author)
            authors.append(author)
        authors = author # return just one result instead of an array
        # Cache the results
        with open(cache_file, "w") as f:
            json.dump({"data": authors, "timestamp": time.time()}, f)
        
        return authors if authors else None
    except Exception as e:
        print(f"Error while fetching or caching author search results: {e}")
        return None
    
def get_author_search(name):
    sanitized_name = secure_filename(name.strip().lower())
    print(f"Checking for cache file: {cacheDir}search_{sanitized_name}.json")
    cache_file = f"{cacheDir}search_{sanitized_name}.json"

    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            print("Cache found, checking if data is stale..")
            cache_content = json.load(f)
            # Serve cached data immediately
            data = cache_content["data"]
            if is_data_stale(cache_content["timestamp"]):
                print("Data is stale, refreshing in the background.")
                # Refresh data in the background if stale
                # if no threads started, start a new one
                thread = Thread(target=fetch_cache_author_search, args=(name,))
                thread.start()
                # thread.join()  # Wait for the thread to complete
            else:
                print("Data is fresh, serving cached data.")
            return data
    else:
        # No cache available, fetch data initially
        fetch_cache_author_search(name)
        return "Fetching data, please retry in a few moments."

# Fetch author data by ID on start, if not already cached
#get_author_data("ynWS968AAAAJ")
# Fetch author data by name on start, if not already cached
#get_author_search("Jodie Rummer")

@app.route("/search_author", methods=["GET"])
@cache.cached(timeout=cachetime, query_string=True)
def search_author():
    name = request.args.get("name")
    if not name:
        return jsonify({"error": "Missing name parameter"}), 400
    
    author = get_author_search(name)
    if author is None:
        return jsonify({"error": "No authors found"}), 404
    
    return jsonify(author)


@app.route("/search_author_id", methods=["GET"])
def search_author_id():
    id = request.args.get("id")
    if not id:
        return jsonify({"error": "Missing id parameter"}), 400
    data = get_author_data(id)
    return jsonify(data)


# search_author_by_organization
@app.route("/search_org", methods=["GET"])
@cache.cached(timeout=cachetime, query_string=True)
def search_org():
    query = request.args.get("query")
    if not query:
        return jsonify({"error": "Missing query parameter"}), 400
    try:
        search_query = scholarly.search_keyword(query)
        publications = [
            next(search_query, None) for _ in range(5)
        ]  # Adjust range as needed
        return jsonify(publications)
    except Exception as e:
        log(traceback.format_exc())
        return jsonify({"error": "An internal error has occurred!"}), 500


@app.route("/search_keyword", methods=["GET"])
@cache.cached(timeout=cachetime, query_string=True)
def search_keyword():
    query = request.args.get("query")
    if not query:
        return jsonify({"error": "Missing query parameter"}), 400

    try:
        search_query = scholarly.search_keyword(query)
        publications = [
            next(search_query, None) for _ in range(5)
        ]  # Adjust range as needed
        return jsonify(publications)
    except Exception as e:
        log(traceback.format_exc())
        return jsonify({"error": "An internal error has occurred!"}), 500


@app.route("/get_coauthors", methods=["GET"])
@cache.cached(timeout=cachetime, query_string=True)
def get_coauthors():
    author_id = request.args.get("author_id")
    if not author_id:
        return jsonify({"error": "Missing author_id parameter"}), 400

    try:
        # Search for the author using the provided ID
        author = scholarly.search_author_id(author_id)
        # Fill the author information for the coauthors section
        author = scholarly.fill(author, sections=["coauthors"])
        # Transform coauthors list into a JSON-serializable format
        coauthors_json = [
            {
                "name": coauthor["name"],
                "affiliation": coauthor["affiliation"],
                "scholar_id": coauthor["scholar_id"],
                "filled": coauthor["filled"],
                "source": coauthor["source"],
            }
            for coauthor in author["coauthors"]
        ]
        return jsonify(coauthors_json)

    except Exception as e:
        log(traceback.format_exc())
        return jsonify({"error": "An internal error has occurred!"}), 500


@app.route("/author_publications", methods=["GET"])
@cache.cached(timeout=cachetime, query_string=True)
def author_publications():
    author_id = request.args.get("author_id")
    if not author_id:
        return jsonify({"error": "Missing author_id parameter"}), 400

    try:
        author = scholarly.search_author_id(author_id)
        publications = scholarly.fill(author, sections=["publications"])["publications"]
        return jsonify(publications)
    except Exception as e:
        log(traceback.format_exc())
        return jsonify({"error": "An internal error has occurred!"}), 500


# @app.route("/search_author_custom_url", methods=["GET"])
# @cache.cached(timeout=cachetime, query_string=True)
# def search_author_custom_url():
#    url = request.args.get("url")
#    if not url:
#        return jsonify({"error": "Missing url parameter"}), 400
#
#    try:
#        author = scholarly.search_author_custom_url(url)
#        return jsonify(author)
#    except Exception as e:
#        log(traceback.format_exc())
#        return jsonify({"error": "An internal error has occurred!"}), 500


@app.route("/search_publications", methods=["GET"])
@cache.cached(timeout=cachetime, query_string=True)
def search_publications():
    query = request.args.get("query")
    if not query:
        return jsonify({"error": "Missing query parameter"}), 400

    try:
        search_query = scholarly.search_pubs(query)
        publication = next(search_query, None)
        if publication is None:
            return jsonify({"error": "No publication found"}), 404

        # Fill the publication information
        filled_publication = scholarly.fill(publication)
        return jsonify(filled_publication)
    except Exception as e:
        log(traceback.format_exc())
        return jsonify({"error": "An internal error has occurred!"}), 500


@app.route("/get_related_publications", methods=["GET"])
@cache.cached(timeout=cachetime, query_string=True)
def get_related_articles():
    pub_id = request.args.get("pub_id")
    if not pub_id:
        return jsonify({"error": "Missing pub_id parameter"}), 400

    try:
        publication = scholarly.search_pubs(pub_id)
        # return jsonify(publication)
        related_articles = scholarly.get_related_articles(publication)
        articles = [next(related_articles, None) for _ in range(5)]  # Adjust as needed
        return jsonify(articles)
    except Exception as e:
        return jsonify({"error": "An internal error has occurred!"}), 500


@app.route("/cited_by", methods=["GET"])
@cache.cached(timeout=cachetime, query_string=True)
def cited_by():
    pub_id = request.args.get("pub_id")
    if not pub_id:
        return jsonify({"error": "Missing pub_id parameter"}), 400

    try:
        # Replace this with the actual method to retrieve a publication by its ID
        publication = scholarly.search_pubs(pub_id)  # Hypothetical method
        citedby = scholarly.citedby(publication)
        citations = []
        for _ in range(3):  # You want up to 3 citations
            try:
                citation = next(citedby, None)
                if citation is None:  # No more citations available
                    break
                citations.append(citation)
            except StopIteration:
                break  # No more citations available
        return jsonify(citations)
    except Exception as e:
        log(traceback.format_exc())
        return jsonify({"error": "An internal error has occurred!"}), 500


# @app.route("/download_mandates_csv", methods=["GET"])
# @cache.cached(timeout=cachetime, query_string=True)
# def download_mandates_csv():
#    filename = secure_filename(request.args.get("filename", "mandates.csv"))
#    try:
#        scholarly.download_mandates_csv(filename, overwrite=True, include_links=True)
#        return send_from_directory(
#            directory=app.config["DOWNLOAD_FOLDER"], path=filename, as_attachment=True
#        )
#    except Exception as e:
#        log(traceback.format_exc())
#        return jsonify({"error": "An internal error has occurred!"}), 500


if __name__ == "__main__":
    app.run(debug=False, port=5001)
