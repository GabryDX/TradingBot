#!/usr/bin/env python
# -*- coding: utf-8 -*-

from random import randrange

from telegram import ReplyKeyboardMarkup
from telegram.constants import ParseMode

import admin
import azioni
from media import get_document_list, get_photo_list
from server_info import get_all_info
import analisi_azioni
import utenti

MARKDOWN = ParseMode.MARKDOWN
MARKDOWN_V2 = ParseMode.MARKDOWN_V2

# default_menu_keyboard = [['Azioni'], ['Dati correnti', 'Valori migliori'], ['Test', 'Info']]
# default_menu_markup = ReplyKeyboardMarkup(default_menu_keyboard, one_time_keyboard=True, resize_keyboard=True)
sub_menu = {"scegli_titolo": False, "compra_vendi": False, "compra": False, "vendi": False, "soglia": False, "soglia_value": ""}


def default_menu(messaggio):
	default_menu_keyboard = [['Menu', 'Azioni'], ['Dati correnti', 'Valori migliori']]
	if admin.is_admin(messaggio.from_user.username):
		default_menu_keyboard += [['Info']]

	default_menu_markup = ReplyKeyboardMarkup(default_menu_keyboard, one_time_keyboard=True, resize_keyboard=True)
	return default_menu_markup


async def user_command(messaggio):
	# global sub_menu

	testo = messaggio.text.lower()
	if testo == "/start" or testo == "menu":
		# text = "INIZIO"
		text = get_main_menu()
		await messaggio.reply_text(text, reply_markup=default_menu(messaggio), parse_mode=MARKDOWN_V2)
	elif testo == "azioni":
		await get_compra_vendi(messaggio)
	elif testo == "dati correnti":
		await get_dati_correnti(messaggio)
	elif testo == "valori migliori":
		await messaggio.reply_text(get_last_bests_vs_actual(), reply_markup=default_menu(messaggio),
							 parse_mode=ParseMode.HTML)
	elif testo == "test":
		await messaggio.reply_text("TEST", reply_markup=default_menu(messaggio))
	elif testo.startswith("/comandi"):
		comandi = "*COMANDI UTENTE:*\n\n*/start* Messaggio iniziale di benvenuto\n"
		comandi += "*/comandi* Lista dei comandi utente\n"
		comandi += "/*random_pic* Invia un'immagine presa causalmente dal database\n"
		comandi += "/*raspberry* Informazioni sul server raspberry"
		await messaggio.reply_text(comandi, parse_mode=MARKDOWN)
	elif testo == "torna al menu":
		await messaggio.reply_text(get_main_menu(), reply_markup=default_menu(messaggio), parse_mode=MARKDOWN_V2)
		for key in sub_menu:
			if isinstance(sub_menu[key], str):
				sub_menu[key] = ""
			else:
				sub_menu[key] = False
	elif sub_menu["scegli_titolo"]:
		await get_scegli_titolo(messaggio)
	elif sub_menu["compra_vendi"]:
		if "compra" in testo.lower():
			await get_compra_menu(messaggio)
		elif "vendi" in testo.lower():
			await get_vendi_menu(messaggio)
		elif "soglia" in testo.lower():
			await get_soglia_menu(messaggio)
	elif sub_menu["compra"]:
		await get_compra_titolo(messaggio)
	elif sub_menu["vendi"]:
		await get_vendi_titolo(messaggio)
	elif sub_menu["soglia"]:
		if sub_menu["soglia_value"] != "":
			await get_soglia_value(messaggio)
		else:
			await get_soglia_titolo(messaggio)
	if admin.is_admin(messaggio.from_user.username):
		if testo == "info":
			menu_keyboard = [['Server'], ["Ricarica Database"], ['Torna al menu']]
			menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)
			await messaggio.reply_text(text="Vuoi le informazioni sul server?", reply_markup=menu_markup)
		elif testo == "ricarica database":
			await reload_database(messaggio)
		elif testo == "server":
			try:
				await messaggio.reply_text(get_all_info(), reply_markup=default_menu(messaggio))
			except Exception as e:
				await messaggio.reply_text("Non mi trovo su server Linux in questo momento",
									 reply_markup=default_menu(messaggio))
				# messaggio.reply_text(str(e), reply_markup=default_menu_markup)
	print(sub_menu)


# elif testo.startswith("/tastiera"):
# 	messaggio.reply_text("aaa")
# 	keyboard = [['7', '8', '9'],['4', '5', '6'],['1', '2', '3'],['0']]
# 	menu_keyboard = [['MenuItem1'], ['MenuItem2']]
# 	menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)
# 	messaggio.reply_text(text='Some text here', reply_markup=menu_markup)


async def get_random_pic(messaggio):
	lista = get_photo_list()
	if len(lista) > 0:
		r = randrange(0, len(lista))
		await messaggio.reply_photo(lista[r], reply_markup=default_menu(messaggio))
	else:
		await messaggio.reply_text("Non ho meme al momento, mandamene uno.", reply_markup=default_menu(messaggio))


async def get_random_doc(messaggio):
	lista = get_document_list()
	if len(lista) > 0:
		r = randrange(0, len(lista))
		await messaggio.reply_document(lista[r], reply_markup=default_menu(messaggio))
	else:
		await messaggio.reply_text("Non ho meme al momento, mandamene uno.", reply_markup=default_menu(messaggio))


async def get_dati_correnti(messaggio):
	menu_keyboard = []
	for aid in sorted(azioni.azioni_id):
		menu_keyboard.append([aid])
	menu_keyboard.append(['Torna al menu'])
	menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)
	await messaggio.reply_text(text="Scegli un titolo per ricevere informazioni", reply_markup=menu_markup)
	sub_menu["scegli_titolo"] = True


async def get_scegli_titolo(messaggio):
	aid = messaggio.text
	if aid in sorted(azioni.azioni_id):
		result, _ = analisi_azioni.get_info(aid)
		await messaggio.reply_text(result, reply_markup=default_menu(messaggio), parse_mode=ParseMode.HTML)
	else:
		await messaggio.reply_text("Titolo non trovato", reply_markup=default_menu(messaggio), parse_mode=ParseMode.HTML)
	sub_menu["scegli_titolo"] = False


async def get_compra_vendi(messaggio):
	text = "Azioni seguite:\n\n```\n" + azioni.get_azioni_info() + "\n```"
	if admin.is_admin(messaggio.from_user.username):
		menu_keyboard = [["Compra", "Vendi"], ["Soglia"], ["Torna al menu"]]
		menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)
		await messaggio.reply_text(text, reply_markup=menu_markup, parse_mode=MARKDOWN_V2)
		sub_menu["compra_vendi"] = True
	else:
		await messaggio.reply_text(text, reply_markup=default_menu(messaggio), parse_mode=MARKDOWN_V2)


async def get_compra_menu(messaggio):
	menu_keyboard = []
	for aid in sorted(azioni.azioni_id):
		if aid not in azioni.azioni_comprate:
			menu_keyboard.append([aid])
	menu_keyboard.append(['Torna al menu'])
	menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)

	text = "Quale titolo vuoi comprare?"
	await messaggio.reply_text(text, reply_markup=menu_markup, parse_mode=MARKDOWN_V2)
	sub_menu["compra_vendi"] = False
	sub_menu["compra"] = True


async def get_vendi_menu(messaggio):
	menu_keyboard = []
	for aid in sorted(azioni.azioni_comprate):
		menu_keyboard.append([aid])
	menu_keyboard.append(['Torna al menu'])
	menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)

	text = "Quale titolo vuoi vendere?"
	await messaggio.reply_text(text, reply_markup=menu_markup, parse_mode=MARKDOWN_V2)
	sub_menu["compra_vendi"] = False
	sub_menu["vendi"] = True


async def get_compra_titolo(messaggio):
	aid = messaggio.text
	if aid in azioni.azioni_id and aid not in azioni.azioni_comprate:
		azioni.add_azioni_comprate(aid)
		text = "Titolo <b>" + aid + "</b> comprato"
		await messaggio.reply_text(text, reply_markup=default_menu(messaggio), parse_mode=ParseMode.HTML)
	else:
		await messaggio.reply_text("Titolo non trovato", reply_markup=default_menu(messaggio),
								   parse_mode=ParseMode.HTML)
	sub_menu["compra"] = False


async def get_vendi_titolo(messaggio):
	aid = messaggio.text
	if aid in azioni.azioni_id and aid in azioni.azioni_comprate:
		azioni.remove_azioni_comprate(aid)
		text = "Titolo <b>" + aid + "</b> venduto"
		await messaggio.reply_text(text, reply_markup=default_menu(messaggio), parse_mode=ParseMode.HTML)
	else:
		await messaggio.reply_text("Titolo non trovato", reply_markup=default_menu(messaggio),
								   parse_mode=ParseMode.HTML)
	sub_menu["vendi"] = False


async def get_soglia_menu(messaggio):
	menu_keyboard = []
	for aid in sorted(azioni.azioni_id):
		menu_keyboard.append([aid])
	menu_keyboard.append(['Torna al menu'])
	menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)

	text = "Scegliere un titolo a cui impostare un valore di soglia."
	await messaggio.reply_text(text, reply_markup=menu_markup, parse_mode=ParseMode.HTML)
	sub_menu["compra_vendi"] = False
	sub_menu["soglia"] = True


async def get_soglia_titolo(messaggio):
	aid = messaggio.text
	if aid in azioni.azioni_id:
		menu_keyboard = [["0", "10", "20"], ["30", "40", "50"], ["100", "150", "200"], ["Torna al menu"]]
		menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)

		text = "Impostare valore di soglia per il titolo <b>" + aid + "</b>."
		text += "\n(Valore di soglia negativo o nullo corrisponde alla rimozione di un valore di soglia)"
		await messaggio.reply_text(text, reply_markup=menu_markup, parse_mode=ParseMode.HTML)
	else:
		await messaggio.reply_text("Titolo non trovato", reply_markup=default_menu(messaggio),
								   parse_mode=ParseMode.HTML)
	# sub_menu["soglia"] = False
	sub_menu["soglia_value"] = aid


async def get_soglia_value(messaggio):
	aid = sub_menu["soglia_value"]
	value_str = messaggio.text
	if value_str.replace('.', '', 1).isdigit():
		value = float(value_str)
		if value > 0:
			print("here3")
			text = "Il valore di soglia per il titolo <b>" + aid + "</b> è stato impostato a " + value_str + "."
			azioni.add_azioni_soglia(aid, value)
		else:
			text = "Il valore di soglia per il titolo <b>" + aid + "</b> è stato rimosso."
			azioni.remove_azioni_soglia(aid)
		await messaggio.reply_text(text, reply_markup=default_menu(messaggio), parse_mode=ParseMode.HTML)
	else:
		await messaggio.reply_text("Valore numerico non trovato", reply_markup=default_menu(messaggio),
								   parse_mode=ParseMode.HTML)
	sub_menu["soglia"] = False
	sub_menu["soglia_value"] = ""


def get_last_bests_vs_actual():
	info = "<i>Valori migliori dall'accensione vs Valori attuali:</i>\n\n"
	for key in sorted(analisi_azioni.last_best):
		lb = str(float("{:.2f}".format(analisi_azioni.last_best[key])))
		ld = str(float("{:.2f}".format(analisi_azioni.last_detected[key])))
		if lb == ld:
			lb = "<u>" + lb + "</u>"
			ld = "<u>" + ld + "</u>"
		lb = "<i>" + lb + "</i>"
		info += "<b>" + azioni.azioni_id[key] + ":</b>\t\t" + lb + " / " + ld + "\n"
	return info


def get_main_menu():
	info = ""
	ordered = sorted(azioni.azioni_id)
	borsa = [x for x in ordered if "-EUR" not in x]
	crypto = [x for x in ordered if "-EUR" in x]
	listona = [borsa, crypto]
	titolo = "🔁 AZIONE    PREZZO    SOGLIA\n"
	titolo2 = "\n\n🆕 CRIPTOVALUTE"

	for lista in listona:
		if info:
			info += titolo2
		for key in lista:
			if info:
				info += "\n"
			space = "          "[len(key):]
			if key in azioni.azioni_comprate:
				info += "✅ "
			else:
				info += "❌ "

			last = "0"
			if key in analisi_azioni.last_detected:
				if analisi_azioni.last_detected[key] < 10.0:
					last = str(round(analisi_azioni.last_detected[key], 3))
				else:
					last = str(round(analisi_azioni.last_detected[key], 2))
			space2 = "          "[len(last):]

			soglia = "0"
			if key in azioni.azioni_soglia:
				soglia = str(azioni.azioni_soglia[key])

			info += key + space + last + space2 + soglia
	text = "Menu Principale:\n\n```\n" + titolo + info + "\n```"
	return text


async def reload_database(messaggio):
	admin.realod_admin()
	utenti.reload_chat_ids()
	azioni.reload_azioni()
	azioni.reaload_azioni_comprate()
	azioni.reload_azioni_soglia()
	azioni.reload_azioni_best()
	azioni.reload_azioni_detected()
	await messaggio.reply_text("<b>Database ricaricato</b>", reply_markup=default_menu(messaggio),
						 parse_mode=ParseMode.HTML)
