import re
from math import ceil
from gae.db import Query


class PaginationException(Exception):
    pass


class Pagination:
    _records = None
    collection = None
    on_page = 10 # show records on each page
    page = 1 # current page
    url = "" # url address of current page

    def __init__(self, request, collection, on_page, attr_name="page", url=None):
        # check collection
        if not isinstance(collection, Query):
            raise PaginationException("First parameter should be instance of google.appengine.ext.db.Query")
        self.collection = collection
        self.on_page = int(on_page)
        self.page = int(request.GET.get(attr_name, 1) or 1)
        # prepare url
        if url is None:
            url = request.path_qs
        # add new parameter to url
        if "?" in url:
            url = re.sub("([\?&])%s=[^&]*&?" % attr_name, "\\1", url).rstrip("&?")
        self.url = url
        self.attr_name = attr_name
    
    def url_with_page_number(self, page_number):
        url = self.url
        if page_number <= 1: # not show parameter for the first page
            return url
        url = url + "&" if "?" in url else url + "?"
        return "%s%s=%s" % (url, self.attr_name, page_number)

    def total_records(self):
        return self.collection.count()

    def total_pages(self):
        return int(ceil(float(self.collection.count()) / self.on_page))

    def current_page(self):
        return self.page

    def records(self):
        '''
        Return list of all objects on current page
        '''
        if self._records is None:
            offset = (self.page - 1) * self.on_page
            self._records = self.collection.fetch(self.on_page, offset)
        return self._records

    def __iter__(self):
        self._index = -1
        return self

    def next(self):
        '''
        Used for loops
        '''
        self._index = self._index + 1
        records = self.records()
        if self._index >= len(records):
            raise StopIteration
        return records[self._index]

    def has_previous(self):
        return self.current_page() > 1

    def has_next(self):
        return self.current_page() < self.total_pages()

    def previous_page_number(self):
        return self.current_page() - 1

    def next_page_number(self):
        return self.current_page() + 1

    def previous_page_url(self):
        return self.url_with_page_number(self.previous_page_number())

    def next_page_url(self):
        return self.url_with_page_number(self.next_page_number())

    def previous_page_link(self):
        return "<a href='%(address)s' class='back'>Back</a>" % {
               "address": self.previous_page_url()}

    def next_page_link(self):
        return "<a href='%(address)s' class='next'>Next</a" % {
               "address": self.next_page_url()}

    def render_pages(self):
        '''
        Return numbers of pages
        '''
        total_pages = self.total_pages()
        start_range = self.current_page() > 2 and self.current_page() - 2 or 1
        end_range   = self.current_page() < total_pages - 2 and self.current_page() + 2 or total_pages
        pages = []
        # add 'back' and 'first' links
        if self.current_page() > 1:
            pages.append("<a href='%(address)s' class='first'>First</a>" % {'address': self.url_with_page_number(1)})
            pages.append(self.previous_page_link())
        for page in range(start_range, end_range+1):
            if page == self.current_page():
                pages.append("<a href='%(address)s' class='current'>%(page)s</a>" % {'page': page, 'address': self.url_with_page_number(page)})
            else:
                pages.append("<a href='%(address)s'>%(page)s</a>" % {'page': page, 'address': self.url_with_page_number(page)})
        # add 'next' and 'last' links
        if self.current_page() < total_pages:
            pages.append(self.next_page_link())
            pages.append("<a href='%(address)s' class='last'>Last</a>" % {'address': self.url_with_page_number(total_pages)})
        # insert data to tag <p>
        pages.insert(0, "<p class='pages'>")
        pages.append("</p>")
        return "\n".join(pages)
