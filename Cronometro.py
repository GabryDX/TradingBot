import time


# Conto alla rovescia che si comporta come time.sleep(t)
# ma mostra un contatore in console
def countdown(t):
	while t:
		mins, secs = divmod(t, 60)
		timeformat = '{:02d}:{:02d}'.format(mins, secs)
		print(timeformat, end='\r')
		time.sleep(1)
		t -= 1
	print('00:00\n')


# Sostituisce time.sleep(tempo) senza bloccare il thread
def stopwatch(attesa):
	# print('INIZIO STOPWATCH')
	now = time.time()
	future = now + attesa
	uscita = True
	while uscita:
		if time.time() > future:
			# print('FINE STOPWATCH')
			uscita = False


# Sostituisce time.sleep(tempo) senza bloccare il thread
def stopwatchTest(attesa):
	now = time.time()
	future = now + attesa
	while True:
		if time.time() > future:
			break
