import sys
import time
import requests
import os
import json
import logging
import telegram

from telegram.ext import Updater, CommandHandler
from dotenv import load_dotenv
# from systemd.journal import JournalHandler    # для использования системных логов демона

ROOT_DIR = os.path.dirname(__file__)
CURRENCY_API_URL = "https://open.er-api.com/v6/latest/{cur}"

def load_config():
    dotenv_path = os.path.join(ROOT_DIR, '.env')
    config_path = os.path.join(ROOT_DIR, 'config', 'config.json')

    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    if not os.environ.get('TG_BOT_TOKEN'):
        raise EnvironmentError("You should set your `.env` file. Please check README.md.")

    if os.path.exists(config_path):
        return json.load(open(config_path, "r"))
    else:
        raise FileNotFoundError("File `config/config.json` not found. Please check README.md.")


def start_callback(update, context):
    print(context.args)
    user_says = " ".join(context.args)
    update.message.reply_text("User said: " + user_says)


def help_callback(update, context):
    print(context.args)
    user_says = " ".join(context.args)
    update.message.reply_text("How can I help you?")


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
        config = load_config()

    except EnvironmentError as ex:
        logging.error(f"{str(ex)}.")
        sys.exit()

    except FileNotFoundError as ex:
        logging.error(f"{str(ex)}.")
        sys.exit()

    tg_bot_token = os.environ["TG_BOT_TOKEN"]

    updater = Updater(token=tg_bot_token)
    dispatcher = updater.dispatcher

    # systemd_log.info("Bot started")  # В журнал
    logging.info("Bot started")  # В папку проекта

    ######################## Handlers ########################
    start_handler = CommandHandler('start', start_callback)
    dispatcher.add_handler(start_handler)

    help_handler = CommandHandler('help', help_callback)
    dispatcher.add_handler(help_handler)

    convert_handler = CommandHandler('convert', convert_callback)
    dispatcher.add_handler(convert_handler)

    updater.start_polling()

    # while True:
    #     try:
    #         response = requests.get(
    #             reviews_url, headers=reviews_headers, timeout=config["timeout"], params=reviews_params
    #         )
    #         response.raise_for_status()
    #         review_info = response.json()
    #
    #     except requests.exceptions.ReadTimeout:
    #         continue
    #     except requests.exceptions.ConnectionError:
    #         logging.warning(f"Connection Error. Waiting connection for {config['sleep']} seconds.")
    #         time.sleep(config["sleep"])
    #         continue
    #     except requests.exceptions.HTTPError as ex:
    #         logging.error(f"Server returned: `{ex.response}`.")
    #         break
    #     except requests.exceptions.JSONDecodeError:
    #         logging.error(f"There is no JSON in the server response. "
    #                       f"Check if DEVMAN_TOKEN and url for user_reviews are correct.")
    #         break
    #
    #     if ts := review_info.get("timestamp_to_request"):  # Проверка на Timeout сервера
    #         reviews_params["timestamp"] = ts
    #         continue
    #
    #     if attempts := review_info.get("new_attempts"):
    #         for attempt in attempts:
    #             should_be_rewrite = attempt.get("is_negative")
    #             review_message = config.get("review_messages")[0] if should_be_rewrite \
    #                 else config.get("review_messages")[1]
    #             tg_bot.send_message(
    #                 text=config.get("message").format(title=attempt.get("lesson_title"),
    #                                                   url=attempt.get("lesson_url"),
    #                                                   review=review_message),
    #                 chat_id=tg_chat_id)
    #             logging.info("Message sent")
    #     if ts := review_info.get("last_attempt_timestamp"):  # Поиск таймстампа в ответе с инфой.
    #         reviews_params["timestamp"] = ts


if __name__ == '__main__':
    main()


