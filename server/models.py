import json
from server import db
from server.localization import *


class Action:
    """Class for representing actions for inline keyboard button callbacks."""
    def __init__(self, name, args=None):
        self.name = name
        self.args = args

    def load_from_json(self, json_string):
        self.__dict__ = json.loads(json_string)

    def to_json(self):
        return json.dumps(self.__dict__)


class Book:
    """Class for representing a book."""
    def __init__(self, book_id, title, category_index, author, year, place,
                 quantity, year_of_creation):
        self.book_id = book_id
        self.title = title
        self.category_index = category_index
        self.author = author
        self.year = year
        self.place = place
        self.quantity = quantity
        self.year_of_creation = year_of_creation

    def to_string(self, language):
        text = "<b>ID:</b> {}\n".format(self.book_id)
        text += f'<b>{BOOK_NAME[language]}</b>{self.title}\n<b>{BOOK_CATEGORY[language]}</b>{CATEGORIES[language][self.category_index]}\n'
        if self.author and self.author != "None":
            text += f'<b>{BOOK_AUTHOR[language]}</b>{self.author}\n'
        if self.year:
            text += f'<b>{BOOK_YEAR[language]}</b>{self.year}\n'
        if self.place and self.place != "None":
            text += f'<b>{BOOK_PLACE[language]}</b>{self.place}\n'
        if self.quantity:
            text += f'<b>{BOOK_QUANTITY[language]}</b>{self.quantity}\n'

        return text

    def to_json(self):
        return json.dumps(self.__dict__)


class User(db.Model):
    chat_id = db.Column(db.Integer, primary_key=True, unique=True)
    language = db.Column(db.Integer, default=0)
    query = db.Column(db.String(100), default="")

    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.language = 0
        self.query = ""
