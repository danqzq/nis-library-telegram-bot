from server.library_db import BOOKS, INVERTED_INDEX


def books_by_query(query_string):
    query_words = [wrd.lower() for wrd in query_string.split()]
    result = set(INVERTED_INDEX[query_words[0]])
    for wrd in query_words[1:]:
        result.intersection_update(INVERTED_INDEX[wrd])

    if result:
        return [BOOKS[x] for x in result]

    result = []
    for book in BOOKS:
        for word in query_words:
            if word not in book.title.lower():
                continue
            result.append(book)
            if len(result) >= 50:
                return result
            break

    return result


def books_by_category(category_index):
    return [book for book in BOOKS if book.category_index == category_index]


def query_result_to_string(range_start, range_end, results):
    response = ""
    for i in range(range_start, min(range_end, len(results))):
        book = results[i]
        book.book_id = i + 1
        book_entry = "{}. {}".format(book.book_id, book.title[:-1])
        if book.author != "None":
            book_entry += "- {}".format(book.author[:-1])
        if book.year != "None":
            book_entry += "({})".format(book.year[:-2])
        response += book_entry + "\n"

    return response
