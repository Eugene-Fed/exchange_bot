import sys
import requests
import os
import logging
import re

from telegram.ext import CommandHandler, MessageFilter, MessageHandler, Updater
from dotenv import load_dotenv
# from systemd.journal import JournalHandler    # для использования системных логов демона

ROOT_DIR = os.path.dirname(__file__)
# TODO - вынести все нижеперечисленные константы в файл настроек
CURRENCY_API_URL = "https://open.er-api.com/v6/latest/{cur}"  # https://www.exchangerate-api.com/docs/free
GREETINGS = ['hello', 'hi']
GOODBYES = ['goodbye', 'good bye', 'bye']


class GreetingsFilter(MessageFilter):
    def filter(self, message):
        for word in re.findall(r'\w+', message.text):
            return word.lower() in GREETINGS


class GoodbyesFilter(MessageFilter):
    def filter(self, message):
        for word in re.findall(r'\w+', message.text):
            return word.lower() in GOODBYES


def load_env():
    dotenv_path = os.path.join(ROOT_DIR, '.env')

    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    if not os.environ.get('TG_BOT_TOKEN'):
        raise EnvironmentError("You should set your `.env` file. Please check README.md.")


def start_callback(update, context):
    """Полноценные подсказки можно настроить и через ботфазер. Тут по-простому, чтобы было."""
    message = f"Hello, {update.message.from_user.first_name}!!!\n" \
              f"With this bot you can get exchange rates."
    update.message.reply_text(message)


def help_callback(update, context):
    message = f"You can use: \n/help for help\n/convert to convert your money."
    update.message.reply_text(message)


def convert_callback(update, context):
    if len(context.args) != 4:
        update.message.reply_text("To get currency convertation please write: \n"
                                  "/convert <count> <currency_code> to <currency_code>\n\n"
                                  "Example: /convert 100 USD to RUB")
    else:
        count_from, cur_from, _, cur_to = context.args

        try:
            response = requests.get(CURRENCY_API_URL.format(cur=cur_from))
            response.raise_for_status()
            currencies_info = response.json()
            update.message.reply_text(currencies_info['rates'][cur_to.upper()] * float(count_from))
        except ValueError:
            update.message.reply_text(f"The firts param should be a number, not the: `{count_from}`")
        except KeyError:
            # Чтобы не париться с отдельной проверкой первого и второго параметра по отдельности
            # TODO - реализовать вывод полного списка доступных кодов
            update.message.reply_text(f"There is no currency with code: `{cur_from.upper()}` or `{cur_to.upper()}`")
        except requests.exceptions.ConnectionError:
            logging.warning(f"Connection Error.")
            update.message.reply_text(f"Some troubles with connection. Wait a minute, please.")
        except requests.exceptions.HTTPError as ex:
            logging.error(f"Server returned: `{ex.response}`.")
            update.message.reply_text(f"Some troubles with Currencies Server.")
        except requests.exceptions.JSONDecodeError as ex:
            logging.error(f"There is no JSON in the server response:\n{str(ex)}")
            update.message.reply_text(f"Some troubles with Currencies Server.")
        except Exception as ex:
            logging.error(f"There is an unexpected error: \n{str(ex)}")
            update.message.reply_text(f"Houston, we have problems bip-bop-bop...")


def greetings_callback(update, context):
    message = f"Hello, {update.message.from_user.first_name}!"
    update.message.reply_text(message)


def goodbyes_callback(update, context):
    message = f"GoodBye, {update.message.from_user.first_name}!"
    update.message.reply_text(message)


def main():
    logging.basicConfig(
        filename=os.path.join(ROOT_DIR, 'log', 'app.log'),
        filemode='a',
        format='%(asctime)s - %(name)s - %(levelname)s: %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S',
        level=logging.INFO
    )
    # systemd_log = logging.getLogger('systemd_log')      # для использования системных логов демона
    # systemd_log.addHandler(JournalHandler())
    # systemd_log.setLevel(logging.INFO)

    try:
        load_env()
    except EnvironmentError as ex:
        logging.error(f"{str(ex)}.")
        sys.exit()

    tg_bot_token = os.environ["TG_BOT_TOKEN"]

    updater = Updater(token=tg_bot_token)
    dispatcher = updater.dispatcher

    # systemd_log.info("Bot started")  # В журнал
    logging.info("Bot started")  # В папку проекта

    # HANDLERS
    start_handler = CommandHandler('start', start_callback)
    dispatcher.add_handler(start_handler)

    help_handler = CommandHandler('help', help_callback)
    dispatcher.add_handler(help_handler)

    convert_handler = CommandHandler('convert', convert_callback)
    dispatcher.add_handler(convert_handler)

    greetings_filter = GreetingsFilter()
    greetings_handler = MessageHandler(greetings_filter, greetings_callback)
    dispatcher.add_handler(greetings_handler)

    goodbyes_filter = GoodbyesFilter()
    goodbyes_handler = MessageHandler(goodbyes_filter, goodbyes_callback)
    dispatcher.add_handler(goodbyes_handler)

    updater.start_polling()


if __name__ == '__main__':
    main()


