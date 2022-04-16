from flask import Flask, request
import telegram
from credentials import bot_token, bot_user_name, URL
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import urllib
from io import BytesIO
import logging


global bot
global TOKEN
TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

cred = credentials.Certificate('./serviceAccount.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://comp7940project-34c59-default-rtdb.firebaseio.com"
})

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    # retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    chat_id = update.message.chat.id
    msg_id = update.message.message_id

    logging.info(len(update.message.photo))
    if len(update.message.photo) != 0:
        photo = update.message.photo[-1].get_file()
        shareImg(photo, chat_id)
        return 'ok'
    text = update.message.text.encode('utf-8').decode()
    print("got text message :", text)
    if text[0] == '/':
        texts = text.split(' ', 1)
        if texts[0] == '/start':
            start(chat_id)
        if texts[0] == '/comment':
            if len(texts) == 1:
                bot.sendMessage(chat_id=chat_id, text='Usage: /comment <title:comment>')
                return 'error'
            msg = comment(texts[1])
            bot.sendMessage(chat_id=chat_id, text=msg)
        if texts[0] == '/getComments':
            if len(texts) == 1:
                bot.sendMessage(chat_id=chat_id, text='Usage: /getComments <title>')
                return 'error'
            getComments(texts[1], chat_id)
        if texts[0] == '/getImgs':
            if len(texts) == 1:
                bot.sendMessage(chat_id=chat_id, text='Usage: /getImgs <number>')
                return 'error'
            getImgs(texts[1], chat_id)
    else:
        bot.sendMessage(chat_id=chat_id, text="Please use /start to get functions supported by robot", reply_to_message_id=msg_id)

    return 'ok'


def start(chat_id):
    bot.sendMessage(chat_id=chat_id, text=" Currently the robot only provides the following functions:")
    bot.sendMessage(chat_id=chat_id, text="(1) Command /comment <title:comment> : Review the TV show \"title\"")
    bot.sendMessage(chat_id=chat_id, text="(2) Command /getComments <title> :  Get comments on the TV show \"title\"")
    bot.sendMessage(chat_id=chat_id, text="(3) Command /getImgs <number> :  Get hiking photos shared by others")
    bot.sendMessage(chat_id=chat_id, text="(4) Send a hiking photo directly and share it with others")


def comment(msg):
    try:
        context_list = msg.split(":")
        logging.info(context_list)
        title = context_list[0]
        review = context_list[1]
        ref = db.reference("/TvShows")
        ref.push().set({
            "title": title,
            "review": review
        })
        return 'comment successfully'
    except (IndexError, ValueError):
        return 'Please add comments according to this format <title:comment>'


def getComments(msg, chat_id):
    try:
        ref = db.reference("/TvShows")
        comment_data = ref.get()
        title = msg
        flag = False
        for key, value in comment_data.items():
            if value["title"] == title:
                flag = True
        if flag is False:
            bot.sendMessage(chat_id=chat_id, text="There is not review on \"" + title + "\" !")
        else:
            bot.sendMessage(chat_id=chat_id, text='Here are some reviews on \"' + title + "\" :")
            for key, value in comment_data.items():
                if value["title"] == title:
                    bot.sendMessage(chat_id=chat_id, text=value["review"])
    except (IndexError, ValueError):
        bot.sendMessage(chat_id=chat_id, text='Usage: /getComment <title>')


def shareImg(pic, chat_id):
    logging.info(pic)
    logging.info(pic["file_path"])
    ref = db.reference("/hiking_img")
    ref.push().set({
        "img_id": pic["file_unique_id"],
        "img_path": pic["file_path"]
    })
    bot.sendMessage(chat_id=chat_id, text='You\'ve successfully shared an image!')


def getImgs(msg, chat_id):
    try:
        ref = db.reference("/hiking_img")
        num = int(msg)
        photo_data = ref.get()
        index = 0
        if photo_data is None:
            bot.sendMessage(chat_id=chat_id, text='Sorry, no one has shared the image yet')
            return
        bot.sendMessage(chat_id=chat_id, text='Here are some photos shared by others')
        for key, value in photo_data.items():
            num -= 1
            index += 1
            logging.info(value["img_path"])
            img = BytesIO(urllib.request.urlopen(value["img_path"]).read())
            bot.send_photo(chat_id, img)
            if num <= 0:
                break
        if num > 0:
            bot.sendMessage(chat_id=chat_id, text='Sorry, we only have ' + str(index) + ' pictures at the moment')
    except (IndexError, ValueError):
        bot.sendMessage(chat_id=chat_id, text='Usage: /getImgs <number>')


@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{URL}/{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"

@app.route('/')
def index():
    return '.'


if __name__ == '__main__':
    app.run(threaded=True)