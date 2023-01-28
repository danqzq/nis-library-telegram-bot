import os
from threading import Thread

from server import app, bot


@app.route('/')
def home():
    return ':)'


def run():
    app.run(host=os.getenv("HOST_ADDRESS"), port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()


keep_alive()
bot.infinity_polling()
