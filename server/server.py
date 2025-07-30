from flask import Flask, request

app = Flask(__name__)

"""
Searches the database of pages given various search criteria.
"""
@app.get("/search")
def search():
    query = request.args.get('q', default=None)
    num_results = query.args.get('n', default=10)

"""
Sorts a collection in the database by relevance to a given list of search terms
"""
def sort_by_relevance(terms: list):
    pass