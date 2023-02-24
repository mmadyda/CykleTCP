#!/usr/bin/python
#-*- coding: utf-8 -*-
from __future__ import division
import RPi.GPIO as GPIO
from time import sleep
from datetime import datetime
from datetime import date
from termcolor import colored
from random import randint

import threading
import math
import MySQLdb
import urllib2
import serial
import time
import sys
import datetime


import socket
import fcntl
import struct

#sys.stdout = open('log', 'w')


maszyna = "ST_" #nazwa maszyny/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
miejsce = "SKOCZOW" #miejsce posadowienia maszyny/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#EDYTOWALNE:
czas_wysylania = 100 #maksymalnu czas cyklu maszyny///////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# czasy trwania sygnalow przerwan
czas_syg_wtrysk = 0.3
czas_syg_wybrak = 0.3
czas_syg_auto = 0.3

nazwa_bazy = "techniplast"
haslo_bazy = "technitools192"
ip_bazy = "10.0.1.215"
user_bazy = "marek"
tabela_bazy = "cykle_szybkie"


klawiatura = 2
przerwanie_uart = 13  #pin do ktrego arduino wyzwala przerwanie UART ------------------------------ zmienione na 13
pierwsze_uart = True
wtrysk = 21 #pin do ktorego wchodzi przerwanie wtrysku
wybrak = 20 #pin do ktorego wchodzi przerwanie wybraku
przerwanie_auto = 12 #przerwanie włączenia automatu i resetowania klawiatury --------------------- zmienione na 12

czas_dla_operatora = 60  #czas po ktorym wysylany jest brak operatora
cykle_operatora = False #sprawdzanie czy pojawily sie cykle po czasie operatora

dolna_granica_wsp = 1 #minimalna ilosc wyslan w czasie wysylania/////////////////////////////////////////////////////////////////////////////////////////////////////
gorna_granica_wsp = 2 #maksymalna ilosc wyslan w czasie wysylania////////////////////////////////////////////////////////////////////////////////////////////////////

wtrysk_s = 0
pop_wtrysk_s = 0

wybrak_s = 0

przycisk = "P1" #poczatkowy stan przycisku

cykl_s = 0
cykl_e = 0
czas_cyklu_s = 0

wsp_wys_s = 1 #wspolczynnik wysylania szybkiego dla przyciskow = czas_wysylania/sredni czas cyklu jest ekwiwalentem ilosci cyklu pomiedzy czasem wysylania


s_postoj_n = 0

s_awaria_m = 0
s_awaria_f = 0
s_przezbrajanie = 0
s_proby_tech = 0
s_brak_zaop = 0
s_postoj = 0



pierwsze_uruchomienie = True

ser = serial.Serial("/dev/ttyAMA0",baudrate=9600,timeout=1,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS)


#bylo ser = serial.Serial("/dev/ttyAMA0",baudrate=115200,timeout=3)


def wyslij_s():
	#while True:
		threading.Timer(czas_wysylania,wyslij_s).start()
		#time.sleep(czas_wysylania) 
		#now = datetime.datetime.now()
		#print colored("PETLA START DATA: "+str(now.strftime("%Y-%m-%d %H:%M:%S"))+"",'cyan')
		#print colored("czas wysylania "+str(czas_wysylania)+" s",'cyan')
		global nazwa_bazy
		global haslo_bazy
		global ip_bazy
		global user_bazy
		global tabela_bazy
		
		global wtrysk_s
		global wybrak_s
		global czas_cyklu_s
		global pop_wtrysk_s
		
		global cykl_s
		global cykl_e
		
		#global czas_wysylania
		global wsp_wys_s
		
		global s_postoj_n
		global s_awaria_m
		global s_awaria_f
		global s_przezbrajanie
		global s_proby_tech
		global s_brak_zaop
		global s_postoj
		
		
		global dolna_granica_wsp
		global gorna_granica_wsp
		
		global przycisk

		
		zapytanie_SQL = ""
		
		#inkrementacja wszystkich wartosci przed sprawdzeniem czy jest internet
		if przycisk == "P1":
			if wtrysk_s <= pop_wtrysk_s:
				s_postoj_n = s_postoj_n +1
		if przycisk == "P2":
			s_awaria_m = s_awaria_m + 1
		if przycisk == "P3":
			s_awaria_f = s_awaria_f+1
		if przycisk == "P4":
			s_przezbrajanie = s_przezbrajanie+1
		if przycisk == "P5":
			s_proby_tech = s_proby_tech+1
		if przycisk == "P6":
			s_brak_zaop = s_brak_zaop+1
		if przycisk == "P7":
			s_postoj = s_postoj+1
		
		pop_wtrysk_s = wtrysk_s
		#sprawdzenie czy jest internet
		if internet_on() == False:
				print("WYSYLANIE: czekam na internet...\n")
				#continue
				return
			
		conn = MySQLdb.connect(passwd=haslo_bazy,db=nazwa_bazy,host=ip_bazy,port=3306,user=user_bazy)
		cursor = conn.cursor()
		
		if przycisk == "P1":

			
			czas_wtrysk_s = 0
			if wtrysk_s != 0:
				if (czas_cyklu_s/wtrysk_s) > czas_wysylania:
					czas_wtrysk_s = 0
					print('czas cyklu jest wiekszy niz czas wysylania')
				else:
					czas_wtrysk_s = (czas_cyklu_s/wtrysk_s)
					
				if czas_wtrysk_s != 0:
					#sprawdzenie czy wspolczynnik wysylania miesci sie w dopuszczalnych granicach
					if czas_wysylania/czas_wtrysk_s > gorna_granica_wsp:
						wsp_wys_s = wsp_wys_s
					elif czas_wysylania/czas_wtrysk_s < dolna_granica_wsp:
						wsp_wys_s = wsp_wys_s
					else:
						if czas_wysylania/czas_wtrysk_s > 1:
							wsp_wys_s = czas_wysylania/czas_wtrysk_s
						else:
							wsp_wys_s = wsp_wys_s
				czas_cyklu_s = 0
			rzecz_wtrysk_s = wtrysk_s - wybrak_s
			if rzecz_wtrysk_s < 0:
				rzecz_wtrysk_s = 0
			#conn = MySQLdb.connect(passwd="Pro2017#",db="14443643_projekt",host="89.161.232.241",port=3306,user="14443643_projekt")

			#dodano sprawdzanie czy nie było operatora i wpisywanie 0 w czas cyklu
			if s_postoj_n > 0:
				zapytanie_SQL = "INSERT INTO `"+nazwa_bazy+"`.`"+tabela_bazy+"` (`miejsce`, `maszyna`, `wtrysk`, `wybrak`, `postoj_n`, `awaria_m`, `awaria_f`, `przezbrajanie`, `proby_tech`, `brak_zaop`, `postoj`, `czas_cyklu`) VALUES ('"+miejsce+"', '"+maszyna+"', '"+str(rzecz_wtrysk_s)+"', '"+str(wybrak_s)+"', '"+str(s_postoj_n*wsp_wys_s)+"', '0', '0', '0', '0', '0', '0', '0')"
				cursor.execute(zapytanie_SQL)
				print colored("WYSYLANIE "+zapytanie_SQL+"\n",'green')
				pierwsze_uruchomienie = True
				czas_cyklu_s = 0
				cykl_s = 0
				cykl_e = 0
				
			else:
				zapytanie_SQL = "INSERT INTO `"+nazwa_bazy+"`.`"+tabela_bazy+"` (`miejsce`, `maszyna`, `wtrysk`, `wybrak`, `postoj_n`, `awaria_m`, `awaria_f`, `przezbrajanie`, `proby_tech`, `brak_zaop`, `postoj`, `czas_cyklu`) VALUES ('"+miejsce+"', '"+maszyna+"', '"+str(rzecz_wtrysk_s)+"', '"+str(wybrak_s)+"', '"+str(s_postoj_n*wsp_wys_s)+"', '0', '0', '0', '0', '0', '0', '"+str(czas_wtrysk_s)+"')"
				cursor.execute(zapytanie_SQL)
				print colored("WYSYLANIE "+zapytanie_SQL+"\n",'green')
			
			print colored("wspolczynnik wysylania s = " +str(wsp_wys_s),'red')
			wtrysk_s = 0
			pop_wtrysk_s = 0
			wybrak_s = 0
			s_postoj_n = 0
		if przycisk == "P2":
			#s_awaria_m = 1
			zapytanie_SQL = "INSERT INTO `"+nazwa_bazy+"`.`"+tabela_bazy+"` (`miejsce`, `maszyna`, `wtrysk`, `wybrak`, `postoj_n`, `awaria_m`, `awaria_f`, `przezbrajanie`, `proby_tech`, `brak_zaop`, `postoj`, `czas_cyklu`) VALUES ('"+miejsce+"', '"+maszyna+"', '0', '0', '0', '"+str(s_awaria_m*wsp_wys_s)+"', '0', '0', '0', '0', '0', '0')"
			cursor.execute(zapytanie_SQL)
			print colored("JEST AWARIA MASZYNY\n",'green')
			print colored("WYSYLANIE "+zapytanie_SQL+"\n",'green')
			pierwsze_uruchomienie = True
			czas_cyklu_s = 0
			cykl_s = 0
			cykl_e = 0
			wtrysk_s = 0
			pop_wtrysk_s = 0
			
		if przycisk == "P3":
			#s_awaria_f = 1
			zapytanie_SQL = "INSERT INTO `"+nazwa_bazy+"`.`"+tabela_bazy+"` (`miejsce`, `maszyna`, `wtrysk`, `wybrak`, `postoj_n`, `awaria_m`, `awaria_f`, `przezbrajanie`, `proby_tech`, `brak_zaop`, `postoj`, `czas_cyklu`) VALUES ('"+miejsce+"', '"+maszyna+"', '0', '0', '0', '0', '"+str(s_awaria_f*wsp_wys_s)+"', '0', '0', '0', '0', '0')"
			cursor.execute(zapytanie_SQL)
			print colored("JEST AWARIA FORMY\n",'green')
			print colored("WYSYLANIE "+zapytanie_SQL+"\n",'green')
			pierwsze_uruchomienie = True
			czas_cyklu_s = 0
			cykl_s = 0
			cykl_e = 0
			wtrysk_s = 0
			pop_wtrysk_s = 0
		
		if przycisk == "P4":
			#s_przezbrajanie = 1
			zapytanie_SQL = "INSERT INTO `"+nazwa_bazy+"`.`"+tabela_bazy+"` (`miejsce`, `maszyna`, `wtrysk`, `wybrak`, `postoj_n`, `awaria_m`, `awaria_f`, `przezbrajanie`, `proby_tech`, `brak_zaop`, `postoj`, `czas_cyklu`) VALUES ('"+miejsce+"', '"+maszyna+"', '0', '0', '0', '0', '0', '"+str(s_przezbrajanie*wsp_wys_s)+"', '0', '0', '0', '0')"
			cursor.execute(zapytanie_SQL)
			print colored("JEST PRZEZBRAJANIE\n",'green')
			print colored("WYSYLANIE "+zapytanie_SQL+"\n",'green')
			pierwsze_uruchomienie = True
			czas_cyklu_s = 0
			cykl_s = 0
			cykl_e = 0
			wtrysk_s = 0
			pop_wtrysk_s = 0
			
		if przycisk == "P5":
			#s_proby_tech = 1
			zapytanie_SQL = "INSERT INTO `"+nazwa_bazy+"`.`"+tabela_bazy+"` (`miejsce`, `maszyna`, `wtrysk`, `wybrak`, `postoj_n`, `awaria_m`, `awaria_f`, `przezbrajanie`, `proby_tech`, `brak_zaop`, `postoj`, `czas_cyklu`) VALUES ('"+miejsce+"', '"+maszyna+"', '0', '0', '0', '0', '0', '0', '"+str(s_proby_tech*wsp_wys_s)+"', '0', '0', '0')"
			cursor.execute(zapytanie_SQL)
			print colored("JEST PROBY\n",'green')
			print colored("WYSYLANIE "+zapytanie_SQL+"\n",'green')
			pierwsze_uruchomienie = True
			czas_cyklu_s = 0
			cykl_s = 0
			cykl_e = 0
			wtrysk_s = 0
			pop_wtrysk_s = 0
			
		if przycisk == "P6":
			#s_brak_zaop = 1
			zapytanie_SQL = "INSERT INTO `"+nazwa_bazy+"`.`"+tabela_bazy+"` (`miejsce`, `maszyna`, `wtrysk`, `wybrak`, `postoj_n`, `awaria_m`, `awaria_f`, `przezbrajanie`, `proby_tech`, `brak_zaop`, `postoj`, `czas_cyklu`) VALUES ('"+miejsce+"', '"+maszyna+"', '0', '0', '0', '0', '0', '0', '0', '"+str(s_brak_zaop*wsp_wys_s)+"', '0', '0')"
			cursor.execute(zapytanie_SQL)
			print colored("JEST BRAK ZAOPATRZENIA\n",'green')
			print colored("WYSYLANIE "+zapytanie_SQL+"\n",'green')
			pierwsze_uruchomienie = True
			czas_cyklu_s = 0
			cykl_s = 0
			cykl_e = 0
			wtrysk_s = 0
			pop_wtrysk_s = 0
			
		if przycisk == "P7":
			#s_postoj = 1
			zapytanie_SQL = "INSERT INTO `"+nazwa_bazy+"`.`"+tabela_bazy+"` (`miejsce`, `maszyna`, `wtrysk`, `wybrak`, `postoj_n`, `awaria_m`, `awaria_f`, `przezbrajanie`, `proby_tech`, `brak_zaop`, `postoj`, `czas_cyklu`) VALUES ('"+miejsce+"', '"+maszyna+"', '0', '0', '0', '0', '0', '0', '0', '0', '"+str(s_postoj*wsp_wys_s)+"', '0')"
			cursor.execute(zapytanie_SQL)
			print colored("JEST POSTOJ\n",'green')
			print colored("WYSYLANIE "+zapytanie_SQL+"\n",'green')
			pierwsze_uruchomienie = True
			czas_cyklu_s = 0
			cykl_s = 0
			cykl_e = 0
			wtrysk_s = 0
			pop_wtrysk_s = 0
		
		czysc_przyciski_s()#wyzerowanie obliczonych wartosci 
		conn.commit()

		cursor.close()
		conn.close()
		
		





def inter_wtrysk(channel):
		global wtrysk_s
		global wtrysk_s
		global cykl_s
		global cykl_e
		global czas_cyklu_s
		global pierwsze_uruchomienie
		global cykle_operatora
		global s_postoj_n
		
		#if przycisk == "P1":
		#dodanie petli sprawdzajacej stan wejscia
		timeout_wtrysk = time.time() + czas_syg_wtrysk
		stan_wtrysk = True
		print colored('WTRYSK: sprawdzenie czy stan niski jest przez '+str(czas_syg_wtrysk)+' s','yellow')
		sleep(0.2)
		while True:
			if (GPIO.input(wtrysk) is not GPIO.LOW):
				stan_wtrysk = False
			if time.time() > timeout_wtrysk:
				break
			
		#zmiana było if True, sprawdzenie czy przycisk jest w stanie niskim przez 1s
		if stan_wtrysk:

			#obliczenie bierzacego czasu cykli i dodanie go do sredniej
			cykl_e = time.time()
			czas_obecnego_cyklu = (cykl_e-cykl_s)
			czas_cyklu_s = czas_cyklu_s+czas_obecnego_cyklu

				
			cykl_s = time.time()	
			wtrysk_s = wtrysk_s+1
			print colored("WTRYSK czas cyklu: " + str(czas_obecnego_cyklu) + ' liczba cykli do wyslania: '+ str(wtrysk_s), 'magenta')
			#print("cykl_s: "+ str(wtrysk_s))
			pierwsze_uruchomienie = False
			cykle_operatora = False
		else:
			print colored('WTRYSK: za krotki sygnal','yellow')
		return

def inter_wybrak(channel):
		global wybrak_s
		global cykle_operatora
		global s_postoj_n

		timeout_wybrak = time.time() + czas_syg_wybrak
		stan_wybrak = True
		print colored('WYBRAK: sprawdzenie czy stan niski jest przez '+str(czas_syg_wybrak)+' s', 'yellow')
		sleep(0.2)
		while True:
			if (GPIO.input(wybrak) is not GPIO.LOW):
				stan_wybrak = False
				pass
			if time.time() > timeout_wybrak:
				break
		#if przycisk == "P1":
		if stan_wybrak:
			wybrak_s = wybrak_s+1
			print colored("WYBRAK: liczba wybrakow: " + str(wybrak_s), 'magenta')
			# print("wybrak_s: "+ str(wybrak_s))
			cykle_operatora = False
		else:
			print colored('WYBRAK: za krotki sygnal', 'yellow')
		return

def internet_on():
		try:
				urllib2.urlopen('http://216.58.192.142', timeout=1)
				return True
		except urllib2.URLError as err:
				return False
def uart(channel):
		global przycisk
		global pierwsze_uart
		global ser

		#ser = serial.Serial("/dev/ttyAMA0",baudrate=9600,timeout=1,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS)
		pierwsze_uart = False #usuniecie linijki powoduje brak reakcji na pierwszy uart
		local_przycisk = ""
		if 	pierwsze_uart != True:
			read = str(ser.readline())
			local_przycisk = read[-2:]
			print colored("serial interrupt: '" +local_przycisk +"'",'red')
			if "P1" in local_przycisk:
				print colored("jest P1-PRACA",'red')
				przycisk = local_przycisk
				print colored("serial accept: '" +przycisk+"'",'red')
				return
			if "P2" in local_przycisk:
				print colored("jest P2-AWARIA MASZYNY",'red')
				przycisk = local_przycisk
				print colored("serial accept: '" +przycisk+"'",'red')
				return
			if "P3" in local_przycisk:
				print colored("jest P3-AWARIA FORMY",'red')
				przycisk = local_przycisk
				print colored("serial accept: '" +przycisk+"'",'red')
				return
			if "P4" in local_przycisk:
				print colored("jest P4-PRZEZBRAJANIE",'red')
				przycisk = local_przycisk
				print colored("serial accept: '" +przycisk+"'",'red')
				return
			if "P5" in local_przycisk:
				print colored("jest P5-PROBY",'red')
				przycisk = local_przycisk
				print colored("serial accept: '" +przycisk+"'",'red')
				return
			if "P6" in local_przycisk:
				print colored("jest P6-BRAK ZAOPATRZENIA",'red')
				przycisk = local_przycisk
				print colored("serial accept: '" +przycisk+"'",'red')
				return
			if "P7" in local_przycisk:
				print colored("jest P7-POSTOJ",'red')
				przycisk = local_przycisk
				print colored("serial accept: '" +przycisk+"'",'red')
				return
		pierwsze_uart = False

def czysc_przyciski_s():
	global s_awaria_m
	global s_awaria_f
	global s_przezbrajanie
	global s_proby_tech
	global s_brak_zaop
	global s_postoj
		
	s_awaria_m = 0
	s_awaria_f = 0
	s_przezbrajanie = 0
	s_proby_tech = 0
	s_brak_zaop = 0
	s_postoj = 0
	

def reset_kl(chanel):
	global ser
	global przycisk
	ser.write('resetKL\n')
	time.sleep(0.1)
	ser.write('guzikiON\n')
	przycisk = "P1" #poczatkowy stan przycisku
	print colored("PRZERWANIE PROGRAMOWE RESET KLAWIATURY przycisk = "+przycisk,'yellow')

def reset_kl_automat(chanel):
	global ser
	global przycisk

	timeout_auto = time.time() + czas_syg_auto
	stan_auto = True
	print colored('AUTOMAT: sprawdzenie czy stan niski jest przez '+str(czas_syg_auto)+' s', 'yellow')
	sleep(0.2)
	while True:
		if (GPIO.input(przerwanie_auto) is not GPIO.LOW):
			stan_auto = False
		if time.time() > timeout_auto:
			break

	if stan_auto:
		ser.write('resetKL\n')
		time.sleep(0.1)
		ser.write('guzikiON\n')
		przycisk = "P1" #poczatkowy stan przycisku
		print colored("PRZERWANIE Z WTRYSKARKI RESET KLAWIATURY przycisk = "+przycisk,'red')
	else:
		print colored('AUTOMAT: za krotki sygnal', 'yellow')
	return

	
def start_klawiatury():
	global ser
	global przycisk
	ser.write('resetKL\n')
	time.sleep(0.1)
	ser.write('guzikiON\n')
	przycisk = "P1" #poczatkowy stan przycisku
	print colored("START KLAWIATURY przycisk ="+przycisk,'red')
	
	
	


def addEventGPIO():	
	GPIO.add_event_detect(wtrysk,GPIO.FALLING,callback = inter_wtrysk,bouncetime=8000)#watek wtryskow
	time.sleep(1)
	GPIO.add_event_detect(wybrak,GPIO.FALLING,callback = inter_wybrak,bouncetime=8000)#watek wybrakow
	time.sleep(1)
	GPIO.add_event_detect(przerwanie_uart,GPIO.FALLING,callback = uart,bouncetime=300)#przerwanie uart klawiatury
	time.sleep(1)
	GPIO.add_event_detect(przerwanie_auto,GPIO.FALLING,callback = reset_kl_automat,bouncetime=300) #reset klawiatury
	time.sleep(1)
	
def removeEventGPIO():
	GPIO.remove_event_detect(wtrysk)
	GPIO.remove_event_detect(wybrak)
	GPIO.remove_event_detect(przerwanie_uart)
	GPIO.remove_event_detect(przerwanie_auto)
	
def runGPIO():
	#GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(wtrysk,GPIO.IN,pull_up_down=GPIO.PUD_UP)
	GPIO.setup(wybrak,GPIO.IN,pull_up_down=GPIO.PUD_UP)
	GPIO.setup(przerwanie_uart,GPIO.IN,pull_up_down=GPIO.PUD_UP)
	GPIO.setup(przerwanie_auto,GPIO.IN,pull_up_down=GPIO.PUD_UP)
	GPIO.setup(klawiatura,GPIO.OUT)
	GPIO.output(klawiatura,GPIO.HIGH)
	
def wyslij_date():
	threading.Timer(60,wyslij_date).start()
	now = datetime.datetime.now()
	try:
		rasp_hostname = socket.gethostname()
		rasp_ip_address = get_ip_address('eth0')
	except:
		print('nie udalo sie pobrac adresu IP')

	print colored("INFO: "+str(now.strftime("%Y-%m-%d %H:%M:%S"))+" czas wysylania: "+str(czas_wysylania)+" s",'cyan')
	print colored('Nazwa hosta: ' + str(rasp_hostname) + ' adres IP: ' + str(rasp_ip_address), 'cyan')

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

try:
	rasp_hostname = socket.gethostname()
	rasp_ip_address = get_ip_address('eth0')
except:
	print('nie udalo sie pobrac adresu IP')

print colored('URUCHAMIANIE maszyna: '+str(maszyna)+' miejsce: '+str(miejsce)+'\nnazwa hosta: '+str(rasp_hostname)+' adres IP: '+str(rasp_ip_address)+'\n','green')
	
runGPIO()
addEventGPIO()
wyslij_s()#uruchomienie watku wysylania danych na serwer
wyslij_date()
start_klawiatury()




		
		

