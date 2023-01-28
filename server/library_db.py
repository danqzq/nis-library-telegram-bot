from collections import defaultdict

import openpyxl as xl

from server.models import Book
from server.constants import TABLES_PATH, EXCEL_TABLES


BOOKS = []
INVERTED_INDEX = defaultdict(list)


def initialize():
    for i, table in enumerate(EXCEL_TABLES):
        workbook = xl.load_workbook(filename=TABLES_PATH + table)
        ws = workbook.active

        for row in ws.rows:
            if str(row).lower() == "none" or row[0].value is None:
                continue
            try:
                book_id = int(row[0].value[:row[0].value.find(".")])
            except ValueError:
                continue
            book = Book(book_id, str(row[4].value), i, str(row[3].value),
                        str(row[6].value), str(row[5].value),
                        str(row[7].value), str(row[8].value))
            BOOKS.append(book)

    for i, book in enumerate(BOOKS):
        for word in book.title.split():
            word = word.strip(".,!?-:/\\")
            INVERTED_INDEX[word.lower()].append(i)


initialize()
