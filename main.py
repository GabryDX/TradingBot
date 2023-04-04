#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Simple Bot to reply to Telegram messages.
This is built on the API wrapper, see echobot2.py to see the same example built
on the telegram.ext bot framework.
This program is dedicated to the public domain under the CC0 license.
"""
import asyncio
import contextlib
import logging
from threading import Thread
from time import sleep

import telegram
from telegram.constants import ParseMode
from telegram.error import NetworkError, Forbidden

import admin
import azioni
import constants
import utenti
from Commands import commands
from textfiles import exists_dir
import Cronometro
import analisi_azioni
import datetime

bot = None
update_id = None
USER_FOLDER = "Users"
MEDIA_FOLDER = "Media"
DATABASE_FOLDER = "Database"
# Borsa di Milano: 9:00 - 17:30
# Borsa Americana: 15:30 - 22:00
min_time = datetime.time(9, 0)
max_time = datetime.time(22, 0)
min_time_ita = datetime.time(9, 0)
max_time_ita = datetime.time(17, 30)
min_time_usa = datetime.time(15, 30)
max_time_usa = datetime.time(22, 0)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def main():
    """Run the bot."""
    global bot
    global update_id
    # Telegram Bot Authorization Token
    bot = telegram.Bot(constants.BOT_TOKEN)

    print("\n --- AVVIO DEL BOT ---\n")
    admin.realod_admin()
    utenti.reload_chat_ids()
    azioni.reload_azioni()
    azioni.reaload_azioni_comprate()
    azioni.reload_azioni_soglia()
    azioni.reload_azioni_best()
    azioni.reload_azioni_detected()
    exists_dir(DATABASE_FOLDER)
    exists_dir(USER_FOLDER)

    # get the first pending update_id, this is so we can skip over it in case
    # we get an "Unauthorized" exception.
    try:
        update_id = (await bot.get_updates())[0].update_id
    except IndexError:
        update_id = None

    for administrator in admin.get_admins().split("\n"):
        if administrator:
            chat_id = utenti.get_chat_id_from_username(administrator)
            await bot.send_message(chat_id=chat_id, text="*BOT ACCESO*", parse_mode=ParseMode.MARKDOWN)

    logger.info("listening for new messages...")

    t1 = Thread(target=wrap_repeat_analysis, args=(bot,))
    t1.start()

    while True:  # QUESTION: is it legal
        try:
            await commands.echo(bot)
        except NetworkError:
            sleep(1)
        except Forbidden:
            # The user has removed or blocked the bot.
            update_id += 1
        except Exception as ex:
            print(ex)


async def repeat_analysis(bot_ref):
    while True:
        now = datetime.datetime.now().time()
        weekday = datetime.datetime.now().weekday()
        add_time = 0
        if min_time < now < max_time and weekday < 5:
            for aid in sorted(azioni.azioni_id):
                if (".MI" in aid and min_time_ita < now < max_time_ita) or \
                        (".MI" not in aid and min_time_usa < now < max_time_usa):
                    bought = aid in azioni.azioni_comprate
                    result, send = analisi_azioni.get_info(aid, bought=bought)
                    if send:
                        # for chat_id in utenti.get_chat_id_str().split("\n"):
                        for chat_id in utenti.chatIDs:
                            if chat_id:
                                print(chat_id)
                                await bot_ref.send_message(chat_id=chat_id, text=result, parse_mode=ParseMode.HTML)
                                Cronometro.countdown(2)
                        Cronometro.countdown(15)
                    else:
                        add_time += 1
            Cronometro.countdown(30)
            Cronometro.countdown(15 * add_time)
        else:
            Cronometro.countdown(1200)


def wrap_repeat_analysis(bot_ref):
    asyncio.run(repeat_analysis(bot_ref))


if __name__ == '__main__':
    with contextlib.suppress(KeyboardInterrupt):  # Ignore exception when Ctrl-C is pressed
        asyncio.run(main())
