#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Load azioni
"""
import analisi_azioni
import textfiles
import utenti

AZIONI = "Database/Azioni.txt"
AZIONI_COMPRATE = "Database/Azioni_Comprate.txt"
AZIONI_SOGLIA = "Database/Azioni_Soglia.txt"
AZIONI_BEST = "Database/Azioni_Best.txt"
AZIONI_DETECTED = "Database/Azioni_Detected.txt"
azioni_id = dict()
azioni_soglia = dict()
azioni_comprate = list()


def reload_dict(diz: dict, filename: str, nome: str):
	"""Ricarico informazioni salvate sulle azioni"""
	if textfiles.exists(filename):
		lista = textfiles.readLines(filename)
		diz.clear()
		for s in lista:
			if "___" in s:
				index = utenti.find_str(s, "___")
				aid = s[:index]
				aid = aid.replace("___", "")
				anome = s[index:]
				anome = anome.replace("___", "")
				if anome.replace('.', '', 1).isdigit():
					anome = float(anome)
				diz[aid] = anome

	else:
		textfiles.write("", filename)

	print("------------------------------")
	print(nome + " UPDATED")
	print(str(len(diz)) + " " + nome + " FOUND")
	print(diz)
	print("------------------------------")


def reload_azioni():
	"""Ricarico informazioni salvate sulle azioni"""
	reload_dict(azioni_id, AZIONI, "AZIONI")


def reload_azioni_soglia():
	"""Ricarico informazioni salvate sulla soglia delle azioni"""
	reload_dict(azioni_soglia, AZIONI_SOGLIA, "SOGLIA AZIONI")


def reload_azioni_best():
	"""Ricarico informazioni salvate sui valori migliori delle azioni"""
	reload_dict(analisi_azioni.last_best, AZIONI_BEST, "AZIONI BEST")


def reload_azioni_detected():
	"""Ricarico informazioni salvate sugli ultimi valori delle azioni"""
	reload_dict(analisi_azioni.last_detected, AZIONI_DETECTED, "AZIONI DETECTED")


def reaload_azioni_comprate():
	"""Ricarico informazioni salvate sulle azioni da vendere"""
	global azioni_comprate
	if textfiles.exists(AZIONI_COMPRATE):
		lista = textfiles.readLines(AZIONI_COMPRATE)
		# azioni_comprate.clear()
		azioni_comprate = lista
	else:
		textfiles.write("", AZIONI_COMPRATE)

	print("------------------------------")
	print("AZIONI COMPRATE UPDATED")
	print(str(len(azioni_comprate)) + " AZIONI COMPRATE FOUND")
	print("------------------------------")


def add_azioni_comprate(azione):
	global azioni_comprate
	azioni_comprate.append(azione)
	textfiles.append(azione + "\n", AZIONI_COMPRATE)
	print("Azione acquistata: " + azione)


def remove_azioni_comprate(azione):
	global azioni_comprate
	azioni_comprate.remove(azione)

	with open(AZIONI_COMPRATE, "w") as f:
		for line in azioni_comprate:
			f.write(line + "\n")
	print("Azione venduta: " + azione)


def add_to_dict(key, value, diz: dict, filename: str):
	diz[key] = value
	with open(filename, "w") as f:
		for ckey in diz:
			line = str(ckey) + "___" + str(diz[ckey])
			f.write(line + "\n")
	print("Valore impostato: " + str(key) + " = " + str(value) + ", " + filename)


def remove_from_dict(key, diz: dict, filename: str):
	diz.pop(key, None)
	with open(filename, "w") as f:
		for ckey in diz:
			line = str(ckey) + "___" + str(diz[ckey])
			f.write(line + "\n")
	print("Valore rimosso: " + str(key) + ", " + filename)


def add_azioni_soglia(azione, soglia):
	add_to_dict(azione, soglia, azioni_soglia, AZIONI_SOGLIA)


def remove_azioni_soglia(azione):
	remove_from_dict(azione, azioni_soglia, AZIONI_SOGLIA)


def add_azioni_best(azione, value):
	add_to_dict(azione, value, analisi_azioni.last_best, AZIONI_BEST)


def remove_azioni_best(azione):
	remove_from_dict(azione, analisi_azioni.last_best, AZIONI_BEST)


def add_azioni_detected(azione, value):
	add_to_dict(azione, value, analisi_azioni.last_detected, AZIONI_DETECTED)


def remove_azioni_detected(azione):
	remove_from_dict(azione, analisi_azioni.last_detected, AZIONI_DETECTED)


def get_azioni_info():
	info = ""
	keys = list(azioni_id.keys())
	keys.sort()
	for key in keys:
		if info:
			info += "\n"
		space = "          "[len(key):]
		if key in azioni_comprate:
			info += "✅ "
		else:
			info += "❌ "
		info += key + space + azioni_id[key]
	return info
