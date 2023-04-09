from collections import Counter
from flask import render_template, request, abort, redirect
from document_retrieval import get_search_results, process_results, filter_documents, facet_search, extract_collection_doctype, extract_author_counts, extract_common_subjects

import math
import re

from project import create_app
from models import Document

app = create_app()
SEARCH_TERM = ''
DOCUMENT_LIST = []
SELECTED_FACETS = set()

@app.route("/")
def index():
    SELECTED_FACETS.clear()
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    global SEARCH_TERM
    global DOCUMENT_LIST
    global SELECTED_FACETS
    
    per_page = 20
    query = request.args.get("query", type=str, default=None)
    if query is None: abort(403)
    selected_keywords = request.args.get("selected_keywords", type=str, default=None)

    if selected_keywords:
        selected_keywords = selected_keywords.split(',')
    # Check if a new search is being performed in order to reset the selected keywords
    if query==SEARCH_TERM:
        clear_local_storage = False
    else:
        SEARCH_TERM = query
        DOCUMENT_LIST.clear()
        SELECTED_FACETS.clear()
        clear_local_storage = True

    facet_filter = request.args.get("facet_filter", type=str, default=None)
    facet_type = request.args.get("facet_type", type=str, default=None)
    if facet_filter:
        SELECTED_FACETS.add((facet_filter, facet_type))

    remove_facet_filter = request.args.get("remove_facet_filter", type=str, default=None)
    remove_facet_type = request.args.get("remove_facet_type", type=str, default=None)
    if remove_facet_filter:
        SELECTED_FACETS.remove((remove_facet_filter, remove_facet_type))

    if not DOCUMENT_LIST:    
        # search for documents
        results = get_search_results(query)
        if results is None:
            abort(404)
        else:
            DOCUMENT_LIST = process_results(results) # table is a list of documents

    if SELECTED_FACETS:
        filtered_documents = facet_search(DOCUMENT_LIST, SELECTED_FACETS)
    else:
        filtered_documents = DOCUMENT_LIST

    if selected_keywords:
        filtered_documents = filter_documents(DOCUMENT_LIST, selected_keywords)

    sort_type = request.args.get('sort_type', type=str, default='date')
    reverse_order = request.args.get('reverse_order', type=bool, default=False)
    filtered_documents = sorted(filtered_documents, key=lambda doc: getattr(doc, sort_type), reverse=reverse_order)
    
    total_documents = len(filtered_documents)
    print(f'total documents: {total_documents}')
    total_pages = math.ceil(total_documents / per_page)
    
    page = int(request.args.get('page', 1))
    collections, doc_types = extract_collection_doctype(DOCUMENT_LIST, SELECTED_FACETS)
    subjects = extract_common_subjects(DOCUMENT_LIST, SELECTED_FACETS)
    authors = extract_author_counts(DOCUMENT_LIST, SELECTED_FACETS)

    return render_template('search.html', documents=filtered_documents, query=query, total_documents=total_documents,
                           page = page, total_pages = total_pages, clear_local_storage=clear_local_storage,
                           facet_search=SELECTED_FACETS, subjects=subjects, authors=authors, collections=collections, doctypes=doc_types)
@app.route("/document")
def document():
    document_id = request.args.get('uuid', type=str, default=None)
    query =  request.args.get('query', type=str, default=None)
    if document_id:
        # search for document_id
        results = get_search_results(document_id)
        if results is None:
            abort(404)
        else:
            doc = process_results(results)[0] # return the first document

        return render_template('document.html', document=doc, query=query)
    else:
        return redirect('search.html', code=302)


