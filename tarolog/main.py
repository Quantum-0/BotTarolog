import datetime
import json
import logging
import os
import random
from hashlib import md5 as taro
from time import sleep

from bot.bot import Bot
from bot.handler import BotButtonCommandHandler, MessageHandler

from tarolog import texts

bot = Bot(token=os.environ.get("TOKEN"), api_url_base=os.environ.get("API_BASE_URL"), is_myteam=True)
SALT = os.environ.get("SALT", "SOME_DEFAULT_SALT_VALUE")
user_state: dict[int, str] = {}
logging.basicConfig(
    format="[%(levelname)s] <%(asctime)s>: %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


def rasklad(project_name: str) -> str:
    result = random.choice(["Карты говорят мне", "Вижу по картам", "Карты подсказали мне"])
    result += ", что "
    randomized_value = int(
        taro((SALT + project_name + str(datetime.date.today())).encode("utf-8", errors="replace")).hexdigest(), 16
    )
    result += texts.RASKLAD_RESULTS[randomized_value % len(texts.RASKLAD_RESULTS)]
    result = result.format(PROJECT_NAME=project_name)
    return result


def format_message(message, event):
    values = {"USERNAME": event.data["from"]["firstName"]}
    return message.format(**values)


def message_cb(bot, event):
    logging.info("Got message: %s", event.data)

    if event.text in ["/start", "/help"]:
        if event.message_author["userId"] in user_state:
            del user_state[event.message_author["userId"]]
        bot.send_text(
            chat_id=event.from_chat,
            text=format_message(texts.HELLO_MESSAGE, event),
            inline_keyboard_markup="[{}]".format(json.dumps(texts.HELLO_KEYBOARD)),
        )
        return

    if user_state.get(event.message_author["userId"]) == "wait_project_name":
        project_name = event.text
        bot.send_text(event.from_chat, format_message(random.choice(texts.MESSAGE_WAITING), event))
        sleep(1)
        bot.send_text(
            event.from_chat,
            format_message(rasklad(project_name), event),
            inline_keyboard_markup="[{}]".format(json.dumps(texts.AFTER_RASKLAD_KEYBOARD)),
        )
        del user_state[event.message_author["userId"]]
        return

    bot.send_text(
        chat_id=event.from_chat,
        text=format_message(texts.MESSAGE_DEFAULT, event),
    )


def buttons_answer_cb(bot, event):
    logging.info("Got inline kb callback: %s", event.data)
    match event.data["callbackData"]:
        case "about":
            bot.send_text(
                chat_id=event.data["message"]["chat"]["chatId"],
                text=format_message(texts.ABOUT_MESSAGE, event),
                inline_keyboard_markup="[{}]".format(json.dumps(texts.ABOUT_KEYBOARD)),
            )
        case "rasklad":
            bot.send_text(
                chat_id=event.data["message"]["chat"]["chatId"],
                text=format_message(texts.ASK_PROJECT_NAME, event),
            )
            user_state[event.message_author] = "wait_project_name"
        case "thanks":
            bot.send_text(
                chat_id=event.data["message"]["chat"]["chatId"],
                text=format_message(texts.UR_WELCOME, event),
                inline_keyboard_markup="[{}]".format(json.dumps(texts.ABOUT_KEYBOARD)),
            )


bot.dispatcher.add_handler(MessageHandler(callback=message_cb))
bot.dispatcher.add_handler(BotButtonCommandHandler(callback=buttons_answer_cb))


def start_bot():
    logging.info("Bot started")
    bot.self_get()
    logging.info("Bot connected")
    bot.start_polling()
    bot.idle()


if __name__ == "__main__":
    start_bot()
