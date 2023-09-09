import json
import os
import random
from time import sleep

from bot.bot import Bot
from bot.handler import BotButtonCommandHandler, MessageHandler

from tarolog import texts

bot = Bot(token=os.environ.get("TOKEN"), api_url_base=os.environ.get("API_BASE_URL"), is_myteam=True)

user_state: dict[int, str] = {}


def rasklad(project_name: str) -> str:
    result = random.choice(["Карты говорят мне", "Вижу по картам", "Карты подсказали мне"])
    result += ", что "
    result += random.choice(texts.RASKLAD_RESULTS).format(PROJECT_NAME=project_name)
    return result


def format_message(message, event):
    values = {"USERNAME": event.data["from"]["firstName"]}
    return message.format(**values)


def message_cb(bot, event):
    print("MESSAGE", event)

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
        bot.send_text(event.from_chat, random.choice(texts.MESSAGE_WAITING))
        sleep(1)
        bot.send_text(event.from_chat, rasklad(project_name))
        del user_state[event.message_author["userId"]]
        return

    bot.send_text(
        chat_id=event.from_chat,
        text=texts.MESSAGE_DEFAULT,
    )


def buttons_answer_cb(bot, event):
    print("INLINE_CALLBACK", event)
    match event.data["callbackData"]:
        case "about":
            bot.send_text(
                chat_id=event.data["message"]["chat"]["chatId"],
                text=format_message(texts.ABOUT_MESSAGE, event),
            )
        case "rasklad":
            bot.send_text(
                chat_id=event.data["message"]["chat"]["chatId"],
                text=format_message(texts.ASK_PROJECT_NAME, event),
            )
            user_state[event.message_author] = "wait_project_name"


bot.dispatcher.add_handler(MessageHandler(callback=message_cb))
bot.dispatcher.add_handler(BotButtonCommandHandler(callback=buttons_answer_cb))


def start_bot():
    print("Bot started")
    bot.self_get()
    print("Bot connected")
    bot.start_polling()
    bot.idle()


if __name__ == "__main__":
    start_bot()
