class Document:
    def __init__(self, uuid, title, date, authors, subjects, abstract, doctype, publisher, series, collection):
        self.uuid = uuid
        self.title = title
        self.date = date
        self.authors = authors
        self.subjects = subjects
        self.abstract = abstract
        self.doctype = doctype
        self.publisher = publisher
        self.series = series
        self.collection = collection