from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import urllib
from io import BytesIO


import configparser
import logging

cred = credentials.Certificate('./serviceAccount.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://comp7940project-34c59-default-rtdb.firebaseio.com"
})


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher

    # You can set this logging module, so you will know when and why things do not work as expected
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    # register a dispatcher to handle message: here we register an echo dispatcher
    echo_handler = MessageHandler(Filters.text & (~Filters.command), comment)
    dispatcher.add_handler(echo_handler)
    dispatcher.add_handler(MessageHandler(Filters.photo, photo))

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("getComments", getComments))
    dispatcher.add_handler(CommandHandler("getImgs", getImgs))

    # To start the bot:
    updater.start_polling()
    updater.idle()


def comment(update, context):
    try:
        context_list = update.message.text.split(":")
        logging.info(context_list)
        title = context_list[0]
        review = context_list[1]
        ref = db.reference("/TvShows")
        ref.push().set({
            "title": title,
            "review": review
        })
        context.bot.send_message(chat_id=update.effective_chat.id, text='comment successfully')
    except (IndexError, ValueError):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Please add comments according to this format <title:comment>')


def getComments(update: Update, context: CallbackContext) -> None:
    try:
        ref = db.reference("/TvShows")
        comment_data = ref.get()
        title = context.args[0]
        flag = False
        for key, value in comment_data.items():
            if value["title"] == title:
                flag = True
        if flag is False:
            update.message.reply_text("There is not review on\"" + title + "\" !")
        else:
            update.message.reply_text('Here are some reviews on \"' + title + "\" :")
            for key, value in comment_data.items():
                if value["title"] == title:
                    update.message.reply_text(value["review"])
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /getComment <title>')


def photo(update: Update, context: CallbackContext) -> None:
    pic = update.message.photo[-1].get_file()
    logging.info(pic)
    logging.info(pic["file_path"])
    ref = db.reference("/hiking_img")
    ref.push().set({
        "img_id": pic["file_unique_id"],
        "img_path": pic["file_path"]
    })
    update.message.reply_text('You\'ve successfully shared an image!')


def getImgs(update: Update, context: CallbackContext) -> None:
    try:
        ref = db.reference("/hiking_img")
        num = int(context.args[0])
        photo_data = ref.get()
        bot = context.bot
        index = 0
        if photo_data is None:
            update.message.reply_text('Sorry, no one has shared the image yet')
        update.message.reply_text('Here are some photos shared by others')
        for key, value in photo_data.items():
            num -= 1
            index += 1
            img = BytesIO(urllib.request.urlopen(value["img_path"]).read())
            bot.send_photo(update.message.chat_id, img)
            if num <= 0:
                break
        if num > 0:
            update.message.reply_text('Sorry, we only have ' + str(index) + ' pictures at the moment')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /getImgs <number>')


if __name__ == '__main__':
    main()