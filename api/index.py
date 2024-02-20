import os
from flask import Flask, jsonify, request, send_from_directory
from scholarly import scholarly, ProxyGenerator
from flask import send_from_directory
from werkzeug.utils import secure_filename
import traceback
from logging import basicConfig, getLogger, INFO

app = Flask(__name__)

basicConfig(level=INFO)
log = getLogger(__name__)

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


# Optional: Setup proxy
# Uncomment the following lines if you want to use proxies.
# pg = ProxyGenerator()
# pg.FreeProxies()
# scholarly.use_proxy(pg)


@app.route("/search_author", methods=["GET"])
def search_author():
    name = request.args.get("name")
    if not name:
        return jsonify({"error": "Missing name parameter"}), 400

    try:
        search_query = scholarly.search_author(name)
        authors = []
        for _ in range(3):  # Attempt to fetch up to 3 authors
            try:
                author = next(search_query, None)
                if author is None:  # Break the loop if no more results
                    break
                authors.append(scholarly.fill(author))
            except StopIteration:
                break  # No more results
        if not authors:  # Check if authors list is empty
            return jsonify({"error": "No authors found"}), 404
        return jsonify(authors)
    except Exception as e:
        log(traceback.format_exc())
        return jsonify({"error": "An internal error has occurred!"}), 500


@app.route("/get_coauthors", methods=["GET"])
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


@app.route("/search_author_custom_url", methods=["GET"])
def search_author_custom_url():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing url parameter"}), 400

    try:
        author = scholarly.search_author_custom_url(url)
        return jsonify(author)
    except Exception as e:
        log(traceback.format_exc())
        return jsonify({"error": "An internal error has occurred!"}), 500


@app.route("/search_publications", methods=["GET"])
def search_publications():
    query = request.args.get("query")
    if not query:
        return jsonify({"error": "Missing query parameter"}), 400

    try:
        search_query = scholarly.search_pubs(query)
        publications = [
            next(search_query, None) for _ in range(5)
        ]  # Adjust range as needed
        return jsonify(publications)
    except Exception as e:
        log(traceback.format_exc())
        return jsonify({"error": "An internal error has occurred!"}), 500


@app.route("/get_related_publications", methods=["GET"])
def get_related_articles():
    pub_id = request.args.get("pub_id")
    if not pub_id:
        return jsonify({"error": "Missing pub_id parameter"}), 400

    try:
        publication = scholarly.search_pubs(pub_id)
        related_articles = scholarly.get_related_articles(publication)
        articles = [next(related_articles, None) for _ in range(5)]  # Adjust as needed
        return jsonify(articles)
    except Exception as e:
        return jsonify({"error": "An internal error has occurred!"}), 500


@app.route("/cited_by", methods=["GET"])
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


@app.route("/download_mandates_csv", methods=["GET"])
def download_mandates_csv():
    filename = secure_filename(request.args.get("filename", "mandates.csv"))
    try:
        scholarly.download_mandates_csv(filename, overwrite=True, include_links=True)
        return send_from_directory(
            directory=app.config["DOWNLOAD_FOLDER"], path=filename, as_attachment=True
        )
    except Exception as e:
        log(traceback.format_exc())
        return jsonify({"error": "An internal error has occurred!"}), 500


if __name__ == "__main__":
    app.run(debug=False)
