import datetime
import json
import logging
import random
from hashlib import md5 as taro
from time import sleep

from bot.bot import Bot
from bot.handler import BotButtonCommandHandler, MessageHandler

from tarolog import texts
from tarolog.metrics import update_metrics
from tarolog.settings import settings

bot = Bot(token=settings.BOT_TOKEN, api_url_base=settings.API_BASE_URL, is_myteam=True)

user_state: dict[int, str] = {}

logging.basicConfig(
    format="[%(levelname)s] <%(asctime)s>: %(message)s",
    level=logging.getLevelName(settings.Logging.LEVEL),
    datefmt="%Y-%m-%d %H:%M:%S",
)


def send_message(event, text, inline_keyboard=None):
    formatted_text = format_message(text, event)
    reply_to_chat = event.from_chat  # or event.data["message"]["chat"]["chatId"] ?
    logging.info("Send reply: %s", formatted_text)
    bot.send_text(reply_to_chat, formatted_text, inline_keyboard_markup=inline_keyboard)


def rasklad(project_name: str) -> str:
    result = random.choice(["Карты говорят мне", "Вижу по картам", "Карты подсказали мне"])
    result += ", что "
    randomized_value = int(
        taro((settings.SALT + project_name + str(datetime.date.today())).encode("utf-8", errors="replace")).hexdigest(),
        16,
    )
    result += texts.RASKLAD_RESULTS[randomized_value % len(texts.RASKLAD_RESULTS)]
    result = result.format(PROJECT_NAME=project_name)
    return result


def format_message(message, event):
    values = {"USERNAME": event.data["from"]["firstName"]}
    return message.format(**values)


def message_cb(bot: Bot, event):
    logging.info("Got message: %s", event.data)

    update_metrics(event.message_author["userId"])

    if event.text in ["/start", "/help"]:
        if event.message_author["userId"] in user_state:
            del user_state[event.message_author["userId"]]
        send_message(event, texts.HELLO_MESSAGE, "[{}]".format(json.dumps(texts.HELLO_KEYBOARD)))
        return

    if user_state.get(event.message_author["userId"]) == "wait_project_name":
        project_name = event.text
        send_message(event, random.choice(texts.MESSAGE_WAITING))
        sleep(1)
        send_message(event, rasklad(project_name), "[{}]".format(json.dumps(texts.AFTER_RASKLAD_KEYBOARD)))
        del user_state[event.message_author["userId"]]
        return

    send_message(event, texts.MESSAGE_DEFAULT)


def buttons_answer_cb(bot: Bot, event):
    logging.info("Got inline keyboard callback: %s", event.data)
    update_metrics(event.message_author)
    match event.data["callbackData"]:
        case "about":
            send_message(event, texts.ABOUT_MESSAGE, "[{}]".format(json.dumps(texts.ABOUT_KEYBOARD)))
        case "rasklad":
            send_message(event, texts.ASK_PROJECT_NAME)
            user_state[event.message_author] = "wait_project_name"
        case "thanks":
            send_message(event, texts.UR_WELCOME, "[{}]".format(json.dumps(texts.ABOUT_KEYBOARD)))


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
