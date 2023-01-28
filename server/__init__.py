import os

from telebot import TeleBot
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask('')
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///db.sqlite3"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bot = TeleBot(os.getenv("TOKEN"))

from server.constants import TABLES_PATH, EXCEL_TABLES
from server.localization import *
