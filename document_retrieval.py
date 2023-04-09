# This file contains all functions related to the repository.tudelft.nl website.
import requests
import urllib.parse
import pandas as pd
import re

from collections import Counter

from models import Document


url = "https://repository.tudelft.nl/islandora/search/"

def get_search_results(search_term):
    """ Get search results from repository.tudelft.nl, store in a dataframe and return it."""
    def is_quote_ok(s):
        """ Check if the search term is surrounded by quotes. If not, add them. """
        stack = []
        for c in s:
            if c in ["'", '"', "`"]:
                if stack and stack[-1] == c:
                    # this single-quote is close character
                    stack.pop()
                else:
                    # a new quote started
                    stack.append(c)
            else:
                # ignore it
                pass
        if len(stack) > 0:
            # print(f"s not good {s}")
            for c in stack:
                s += c
            # print(f"new s {s}")
        return s
    
    search_term = is_quote_ok(search_term)
    search_term_encoded = urllib.parse.quote(search_term)
    search_collection = ["", "?collection=research", "?collection=education", "?collection=heritage"]

    save_csv = ["?display=tud_csv", "&display=tud_csv"]

    # search in all collections for now
    search_url = url + search_term_encoded + search_collection[0] + save_csv[0]

    response = requests.get(search_url)
    # Check if the response was successful
    if response.status_code == 200:
        # Open the response content as a string buffer
        csv_buffer = response.content.decode('utf-8')
        if "No search results, nothing to export!" in csv_buffer:
            # Handle the case where the CSV file does not exist or is empty
            print('no results found for this search term')
            # results_dict[search_term] = 'no results found'
        else:
            # Read url as a pandas dataframe
            print(search_url)
            try:
                csv_data = pd.read_csv(search_url)
                return csv_data
                # results_dict[search_term] = csv_data
            except pd.errors.ParserError:
                print("something went wrong")
    else:
        print('Failed to download CSV file')

def count_topic_frequencies(df, column):
    """ Count the number of times a topic appears in a column of a DataFrame"""
    topic_counter = Counter()
    for topics in df[column]:
        if topics:
            topic_list = [topic.strip().title() for topic in topics.split(';')]
            topic_counter.update(topic_list)
    return topic_counter

def display_frequencies(counter):
    """ Format the topic frequencies for display """
    formatted_frequencies = ";".join([f"{topic} ({count})" for topic, count in counter.items()])
    return formatted_frequencies

def process_results(csv_data: pd.DataFrame):
    """ Convert DataFrame to list of Document objects """
    results = []
    csv_data = csv_data.fillna('') # convert NaN values to empty strings
    
    topic_frequencies = count_topic_frequencies(csv_data, 'subject topic')
    for _, row in csv_data.iterrows(): 
        subject_topics = row['subject topic']
        # add the number of times a topic appears in the results to the topic
        if subject_topics:
            topic_list = [topic.strip().title() for topic in subject_topics.split(';')]
            
            updated_topics = ";".join([f"{topic} ({topic_frequencies[topic]})" for topic in topic_list])
        else:
            updated_topics = ""
            
    # Replace everything between the parenthesis with 'Author' for each author in the list
        if row['author']:
            authors_cleaned = ';'.join([re.sub(r'\(.*?\)', ' (Author)', author).strip() for author in row['author'].split(';')])
        else:
            authors_cleaned = ""
            
        results.append(Document(
            uuid= row['uuid'],
            title= row['title'],
            date = row['publication year'],
            authors= authors_cleaned,
            subjects= updated_topics,
            abstract= row['abstract'],
            doctype= row['publication type'],
            publisher= row['publisher'],
            series = row['faculty'],
            collection= row['department']
        ))       

    return results

def filter_documents(documents, keywords):
    """ Filter the documents based on the selected keywords """
    filtered_documents = []
    print(f'we received {len(documents)} documents in the filter_documents function')
    print(f'we look for the following keywords: {keywords}')
    for document in documents:
            if any(keyword in document.subjects for keyword in keywords):
                filtered_documents.append(document)

    return filtered_documents

def facet_search(documents, filters):
    filtered_documents = documents.copy()
    for (filter_value, filter_type) in filters:
        for document in filtered_documents:
            if filter_value not in getattr(document, filter_type):
                filtered_documents.remove(document)

    return filtered_documents

def extract_collection_doctype(documents, facet_filters):
    collections = []
    doc_types = []
    if not any(facet_type[1] == 'collection' for facet_type in facet_filters):
        collections = [doc.collection for doc in documents if doc.collection != ""]
        collections = Counter(collections).most_common(100)

    if not any(facet_type[1] == 'doctype' for facet_type in facet_filters):
        doc_types = [doc.doctype for doc in documents if doc.doctype != ""]
        doc_types = Counter(doc_types).most_common(100)
    return collections, doc_types

def extract_common_subjects(documents, facet_filters):
    subjects = [subject for doc in documents for subject in doc.subjects.split(';')]
    subjects = [subject for subject in subjects if subject not in [f[0] for f in facet_filters]]
    unique_subjects = list(set(subjects))
    result = []
    for subject_txt in unique_subjects:
        if subject_txt.strip():
            subject = re.findall(r'^(.+?)\s*\(', subject_txt)[0].strip()
            count = int(re.findall(r'\((\d+)\)[^()]*$', subject_txt)[0])
            result.append((subject, count))
    sorted_result = sorted(set(result), key=lambda x: x[1], reverse=True)[:100]
    return sorted_result

def extract_author_counts(documents, facet_filters):
    last_names = []
    for doc in documents:
        for author in doc.authors.split('(author)'):
            last_name = author.split(', ')[0].strip()
            last_names.append(last_name)
    last_names = [last_name for last_name in last_names if last_name not in [f[0] for f in facet_filters]]
    authors = Counter(last_names).most_common(100)
    return authors
