import json
import pickle
import sys
import socket
import threading

import paho
import pymysql
import configparser
from infi.systray.win32_adapter import GetSystemMetrics
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.textinput import TextInput
import paho.mqtt.client as mqtt
from termcolor import colored
import time
from datetime import datetime as czas
import datetime
import os
import kivy
from kivy.uix.rst import RstDocument
from kivy.uix.stacklayout import StackLayout
from kivy.core.window import Window
from kivy.app import App
from kivy.uix.button import Button
from kivy.config import Config
from kivy import utils
from ping3 import ping, verbose_ping
import ctypes  # An included library with Python install.
from adafruit_rplidar import RPLidar

from pynput.keyboard import Key
#2022
# Disable



def blockPrint():
    sys.stdout = open(os.devnull, 'w')
# Restore
def enablePrint():
    sys.stdout = sys.__stdout__

#blockPrint()

# wpisać w konsoli pycharm
# pip install pyinstaller
# pyinstaller --icon=data/icon.ico app.py
# pyinstaller --onefile --icon=data/img/icon.ico app.py
# *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],


#       SUBSKRYPCJA MQTT:
# SKOCZOW/MAGAZYN/#
# SKOCZOW/NASTAWIACZ/#
# SKOCZOW/JAKOSC/#
# SKOCZOW/BRYGADZISTA/#
# SKOCZOW/NARZEDZIOWNIA/#
# SKOCZOW/UTRZYMANIE/#

wersja = '21.02.2023'

screen_width = GetSystemMetrics(0)
screen_height = GetSystemMetrics(1)

print("SCREEN Width =", screen_width)
print("SCREEN Height =", screen_height)
    # wymiary okna
win_width = 500
win_height = screen_height - 70
# ZMIENIAĆ WERSJĘ PROGRAMU

kivy.require('1.10.1')
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '700')
Config.set('graphics', 'fullscreen', 0)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('graphics', 'resizable', 0)  # 0 being off 1 being on as in true/false
Config.window_icon = os.path.join('data', 'img', 'icon.ico')

brak_conf = False

# Do wyświeltenia IP komputera na belce
sIP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sIP.connect(("10.0.0.1", 80))
LOCAL_IP = sIP.getsockname()[0]

print(LOCAL_IP)
sIP.close()

ping_server = 0

# IP obecnego komputera

TCP_PORT = 519
BUFFER_SIZE = 16

#######################################################################################################################
# EDYTOWALNE:
'''
maszyna = "TEST"  # nazwa maszyny///////////////////////////////////////////////////////////////////////////////////////
miejsce = "SKOCZOW"  # miejsce posadowienia maszyny/////////////////////////////////////////////////////////////////////
czas_wysylania = 60  # maksymalnu czas cyklu maszyny////////////////////////////////////////////////////////////////////

dolna_granica_wsp = 1  # MINIMALNA LICZBA CYKLI POMIEDZY WYSLANIAMI DO BAZY domyślnie 1
gorna_granica_wsp = 2  # MAKSYMALNA LICZBA CYKLI  POMIEDZY WYSLANIAMI DO BAZY domyślnie 2
'''
# czasy trwania sygnalow przerwan

# załadowanie ustawień z pliku

def internet_on():
    global ping_server
    # urlopen("https://www.google.com/", timeout=5)
    try:
        ping_server = ping('10.0.0.1')
        if ping_server is not None:
            if ping_server > 0:
                return True
            else:
                ping_server = 0
                return False

        else:
            ping_server = 0
            return False
    except:
        return False

config = configparser.ConfigParser()
if os.path.exists(os.path.join('data', 'app.ini')):
    config.read(os.path.join('data', 'app.ini'))

    maszyna = str(config['DEFAULT']['maszyna'])  # nazwa maszyny
    miejsce = str(config['DEFAULT']['miejsce'])  # miejsce posadowienia maszyny
    czas_wysylania = int(config['DEFAULT']['czas_wysylania'])  # maksymalnu czas cyklu maszyny

    dolna_granica_wsp = int(
        config['DEFAULT']['dolna_granica_wsp'])  # MINIMALNA LICZBA CYKLI POMIEDZY WYSLANIAMI DO BAZY domyślnie 1
    gorna_granica_wsp = int(
        config['DEFAULT']['gorna_granica_wsp'])  # MAKSYMALNA LICZBA CYKLI  POMIEDZY WYSLANIAMI DO BAZY domyślnie 2
    czas_reset = int(config['DEFAULT']['czas_reset'])  #czas pomiędzy resetem programu
    zmieniaj_okna = config.getboolean('DEFAULT', 'zmieniaj_okna')
    czas_zmiana_okna = int(config['DEFAULT']['czas_zmiana_okna'])
else:
    brak_conf = True
    maszyna = "IP"  # nazwa maszyny///////////////////////////////////////////////////////////////////////////////////////
    miejsce = "SKOCZOW"  # miejsce posadowienia maszyny/////////////////////////////////////////////////////////////////////
    czas_wysylania = 20  # maksymalnu czas cyklu maszyny////////////////////////////////////////////////////////////////////

    dolna_granica_wsp = 1  # MINIMALNA LICZBA CYKLI POMIEDZY WYSLANIAMI DO BAZY domyślnie 1
    gorna_granica_wsp = 2  # MAKSYMALNA LICZBA CYKLI  POMIEDZY WYSLANIAMI DO BAZY domyślnie 2
    czas_reset = 3600  #czas pomiędzy resetem programu

    zmieniaj_okna = True #przełączaj okna w programie
    czas_zmiana_okna = 15 #czas przełączania okien

if maszyna == "IP":
    maszyna = str(LOCAL_IP)

nazwa_bazy = "techniplast"
haslo_bazy = "technitools192"
ip_bazy = "10.0.1.215"
port_bazy = 3306
user_bazy = "marek"
tabela_bazy = "cykle_szybkie"
zapytanie_pop_data = "SELECT max(data_g) FROM techniplast.cykle_szybkie where maszyna = '"+maszyna+"';"
pop_insert_date = ""

#zewnetrzne ip 91.225.157.226:6666
#wewnetrzne ip 10.0.1.215:3306

##mqttBroker = 'ee329ce5903f4b4eaf2470a31b104117.s2.eu.hivemq.cloud'
##mqttUser = "Techniplast"
##mqttPassword = "Techniplast34"
##mqttPort = 8883
##mqttClient = mqtt.Client(maszyna, protocol=paho.mqtt.client.MQTTv31)
##mqttClient.tls_set(tls_version=paho.mqtt.client.ssl.PROTOCOL_TLS)
##mqttClient.tls_insecure_set(True)
##mqttClient.username_pw_set(mqttUser, mqttPassword)

mqttBroker = 'broker.hivemq.com'
mqttPort = 1883
mqttClient = mqtt.Client(maszyna, protocol=paho.mqtt.client.MQTTv31)


if internet_on():
    if mqttClient.is_connected():
        mqttClient.disconnect()
        try:
            mqttClient.connect(mqttBroker, port=mqttPort)
        except:
            print("MQTT brak połączenia")
    else:
        print("MQTT brak połączenia")



wtrysk_s = 0
pop_wtrysk_s = 0

wybrak_s = 0

przycisk = "P1"  # poczatkowy stan przycisku




cykl_s = 0
cykl_e = 0
czas_cyklu_s = 0

wsp_wys_s = 1  # wspolczynnik wysylania szybkiego dla przyciskow = czas_wysylania/sredni czas cyklu jest ekwiwalentem ilosci cyklu pomiedzy czasem wysylania

s_postoj_n = 0
s_awaria_m = 0
s_awaria_f = 0
s_przezbrajanie = 0
s_susz_m = 0
s_proby_tech = 0
s_brak_zaop = 0
s_brak_oper = 0
s_postoj = 0

wc_magazyn = False
wc_nastawiacz = False
wc_jakosc = False
wc_brygadzista = False
wc_narzedziowiec = False
wc_utrzymanie  = False
dat_magazyn = ''
dat_nastawiacz = ''
dat_jakosc = ''
dat_brygadzista = ''
dat_narzedziowiec = ''
dat_utrzymanie = ''

pierwsze_uruchomienie = True
stop_application = False
text_console_length = 5000

data_z_pliku = False
start_text = f'''
[b][color=#009EE0]TECHNITOOLS[/color][/b]

:[color=#FFFFFF]Autor[/color]:      [color=#FFFFFF]Marek Madyda[/color]
:[color=#FFFFFF]Wersja programu[/color]:        [color=#FFFFFF]{wersja}[/color]
:[color=#FFFFFF]Dane z pliku[/color]:       [color=#FFFFFF]app.ini[/color]
:[color=#FFFFFF]Nazwa maszyny[/color]:      [color=#FFFFFF]{maszyna}[/color]
:[color=#FFFFFF]Miejsce posadowienia[/color]:       [color=#FFFFFF]{miejsce}[/color] (SKOCZOW,USTRON,KONIAKOW)
:[color=#FFFFFF]czas wysyłania[/color]:         [color=#FFFFFF]{czas_wysylania}[/color] (20,30,60,90,100,120)
:[color=#FFFFFF]max cykl[/color]:       [color=#FFFFFF]{dolna_granica_wsp}[/color]    (1)
:[color=#FFFFFF]min cykl[/color]:       [color=#FFFFFF]{gorna_granica_wsp}[/color]    (2)
:[color=#FFFFFF]czas resetu[/color]:        [color=#FFFFFF]{czas_reset}[/color]    (3600)
:[color=#FFFFFF]zmieniaj okna[/color]:      [color=#FFFFFF]{zmieniaj_okna}[/color]    (True)
:[color=#FFFFFF]czas zmiana okna[/color]:       [color=#FFFFFF]{czas_zmiana_okna}[/color]    (10)
        '''


try:
    pkl_file = open(os.path.join('data', 'data.pkl'), 'rb')
    pref = pickle.load(pkl_file)
    przycisk = pref['przycisk']
    wtrysk_s = int(pref['wtrysk_s'])
    wybrak_s = int(pref['wybrak_s'])
    wsp_wys_s = float(pref['wsp_wys_s'])
    wc_magazyn = bool(pref['wc_magazyn'])
    wc_nastawiacz = bool(pref['wc_nastawiacz'])
    wc_jakosc = bool(pref['wc_jakosc'])
    wc_brygadzista = bool(pref['wc_brygadzista'])
    wc_narzedziowiec = bool(pref['wc_narzedziowiec'])
    wc_utrzymanie = bool(pref['wc_utrzymanie'])
    dat_magazyn = str(pref['data_magazyn'])
    dat_nastawiacz = str(pref['data_nastawiacz'])
    dat_jakosc = str(pref['data_jakosc'])
    dat_brygadzista = str(pref['data_brygadzista'])
    dat_narzedziowiec = str(pref['data_narzedziowiec'])
    dat_utrzymanie = str(pref['data_utrzymanie'])

    data_z_pliku = True


except:
    print('brak pliku ustawień')



class KonsolaPage(StackLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.console_size = 0.6
        self.console = RstDocument(text='',
                                   background_color=(
                                       51 / 255.0, 51 / 255.0, 51 / 255.0, 1))  # create a text input instance

        self.info_on_color = 'on_blue'
        self.info_console_on_color = '#33ccff'
        self.add_widget(self.console)

    def print_console(self, str, color):
        global text_console_length
        self.console.text = self.console.text[-text_console_length:]
        self.console.text = self.console.text + f'''
[color={color}]{str}[/color]
    '''
        self.console.scroll_y = 0


konsola_page = KonsolaPage()

class WywolaniaPage(StackLayout):
    def __init__(self, **kwargs):
        global mqttPrzywolajTematy
        global mqttKasujTematy
        super().__init__(**kwargs)
        self.console_size = 0.6
        self.console = RstDocument(text='',
                                   size_hint=(1, self.console_size),
                                   background_color=(
                                       51 / 255.0, 51 / 255.0, 51 / 255.0, 1))  # create a text input instance

        self.info_on_color = 'on_blue'
        self.info_console_on_color = '#33ccff'
        self.check_color = "#92D050"





        self.liczba_przyciskow = 6.0

        self.wcisnieto_magazyn = False
        self.wcisnieto_nastawiacz = False
        self.wcisnieto_jakosc = False
        self.wcisnieto_brygadzista = False
        self.wcisnieto_narzedziowiec = False
        self.wcisnieto_utrzymanie = False

        self.data_magazyn = ''
        self.data_nastawiacz = ''
        self.data_jakosc = ''
        self.data_brygadzista = ''
        self.data_narzedziowiec = ''
        self.data_utrzymanie = ''

        self.btn_przywolaj_magazyn = Button(text="Przywołaj\nMagazyn", size_hint=(1, 1.0 / self.liczba_przyciskow))
        self.btn_przywolaj_magazyn.bind(on_touch_down=self.btn_przywolaj_magazyn_action)

        self.btn_przywolaj_nastawiacza = Button(text="Przywołaj\nNastawiacza", size_hint=(1, 1.0 / self.liczba_przyciskow))
        self.btn_przywolaj_nastawiacza.bind(on_touch_down=self.btn_przywolaj_nastawiacza_action)

        self.btn_przywolaj_jakosc = Button(text="Przywołaj\nKontrolę jakości", size_hint=(1, 1.0 / self.liczba_przyciskow))
        self.btn_przywolaj_jakosc.bind(on_touch_down=self.btn_przywolaj_jakosc_action)

        self.btn_przywolaj_brygadziste = Button(text="Przywołaj\nBrygadzistę", size_hint=(1, 1.0 / self.liczba_przyciskow))
        self.btn_przywolaj_brygadziste.bind(on_touch_down=self.btn_przywolaj_brygadziste_action)

        self.btn_przywolaj_narzedziowca = Button(text="Przywołaj\nNarzędziowca", size_hint=(1, 1.0 / self.liczba_przyciskow))
        self.btn_przywolaj_narzedziowca.bind(on_touch_down=self.btn_przywolaj_narzedziowca_action)

        self.btn_przywolaj_utrzymanie = Button(text="Przywołaj\nUtrzymanie ruchu", size_hint=(1, 1.0 / self.liczba_przyciskow))
        self.btn_przywolaj_utrzymanie.bind(on_touch_down=self.btn_przywolaj_utrzymanie_action)

        self.btn_przywolaj_magazyn.font_size = "28sp"
        self.btn_przywolaj_nastawiacza.font_size = "28sp"
        self.btn_przywolaj_jakosc.font_size = "28sp"
        self.btn_przywolaj_brygadziste.font_size = "28sp"
        self.btn_przywolaj_narzedziowca.font_size = "28sp"
        self.btn_przywolaj_utrzymanie.font_size = "28sp"

        self.btn_przywolaj_magazyn.valign = 'center'
        self.btn_przywolaj_nastawiacza.valign = 'center'
        self.btn_przywolaj_jakosc.valign = 'center'
        self.btn_przywolaj_brygadziste.valign = 'center'
        self.btn_przywolaj_narzedziowca.valign = 'center'
        self.btn_przywolaj_utrzymanie.valign = 'center'

        self.btn_przywolaj_magazyn.halign = 'center'
        self.btn_przywolaj_nastawiacza.halign = 'center'
        self.btn_przywolaj_jakosc.halign = 'center'
        self.btn_przywolaj_brygadziste.halign = 'center'
        self.btn_przywolaj_narzedziowca.halign = 'center'
        self.btn_przywolaj_utrzymanie.halign = 'center'

        self.add_widget(self.btn_przywolaj_magazyn)
        self.add_widget(self.btn_przywolaj_nastawiacza)
        self.add_widget(self.btn_przywolaj_jakosc)
        self.add_widget(self.btn_przywolaj_brygadziste)
        self.add_widget(self.btn_przywolaj_narzedziowca)
        self.add_widget(self.btn_przywolaj_utrzymanie)

        self.default_button_color = self.btn_przywolaj_magazyn.background_color
        self.default_background_normal = self.btn_przywolaj_magazyn.background_normal
        if(data_z_pliku):
            self.przyciski_z_pliku()

    def btn_przywolaj_magazyn_action(self, instance, touch):
        if not self.btn_przywolaj_magazyn.collide_point(touch.x, touch.y):
            return
        if touch.button == 'left' and self.wcisnieto_magazyn == False:
            self.wcisnieto_magazyn = True
            now = czas.now()
            self.data_magazyn = now.strftime("%H:%M:%S")
            self.btn_przywolaj_magazyn.background_normal = ''
            self.btn_przywolaj_magazyn.background_color = utils.get_color_from_hex(self.check_color)
            self.btn_przywolaj_magazyn.text = "Przywołaj\nMagazyn "+self.data_magazyn

        elif touch.button == 'right' and self.wcisnieto_magazyn == True:
            self.wcisnieto_magazyn = False
            self.btn_przywolaj_magazyn.background_color = self.default_button_color
            self.btn_przywolaj_magazyn.background_normal = self.default_background_normal
            self.btn_przywolaj_magazyn.text="Przywołaj\nMagazyn"
        self.reconnectMQTT()
        self.wyslij_MQTT()


    def btn_przywolaj_nastawiacza_action(self, instance, touch):
        if not self.btn_przywolaj_nastawiacza.collide_point(touch.x, touch.y):
            return
        if touch.button == 'left' and self.wcisnieto_nastawiacz == False:
            self.wcisnieto_nastawiacz = True
            now = czas.now()
            self.data_nastawiacz = now.strftime("%H:%M:%S")
            self.btn_przywolaj_nastawiacza.background_normal = ''
            self.btn_przywolaj_nastawiacza.background_color = utils.get_color_from_hex(self.check_color)
            self.btn_przywolaj_nastawiacza.text = "Przywołaj\nNastawiacza "+self.data_nastawiacz
        elif touch.button == 'right' and self.wcisnieto_nastawiacz == True:
            self.wcisnieto_nastawiacz = False
            self.btn_przywolaj_nastawiacza.background_color = self.default_button_color
            self.btn_przywolaj_nastawiacza.background_normal = self.default_background_normal
            self.btn_przywolaj_nastawiacza.text = "Przywołaj\nNastawiacza"
        self.reconnectMQTT()
        self.wyslij_MQTT()





    def btn_przywolaj_jakosc_action(self, instance, touch):
        if not self.btn_przywolaj_jakosc.collide_point(touch.x, touch.y):
            return
        if touch.button == 'left' and self.wcisnieto_jakosc == False:
            self.wcisnieto_jakosc = True
            now = czas.now()
            self.data_jakosc = now.strftime("%H:%M:%S")
            self.btn_przywolaj_jakosc.background_normal = ''
            self.btn_przywolaj_jakosc.background_color = utils.get_color_from_hex(self.check_color)
            self.btn_przywolaj_jakosc.text = "Przywołaj\nKontrolę jakości "+ self.data_jakosc
        elif touch.button == 'right' and self.wcisnieto_jakosc == True:
            self.wcisnieto_jakosc = False
            self.btn_przywolaj_jakosc.background_color = self.default_button_color
            self.btn_przywolaj_jakosc.background_normal = self.default_background_normal
            self.btn_przywolaj_jakosc.text = "Przywołaj\nKontrolę jakości"
        self.reconnectMQTT()
        self.wyslij_MQTT()



    def btn_przywolaj_brygadziste_action(self, instance, touch):
        if not self.btn_przywolaj_brygadziste.collide_point(touch.x, touch.y):
            return
        if touch.button == 'left' and self.wcisnieto_brygadzista == False:
            self.wcisnieto_brygadzista = True
            now = czas.now()
            self.data_brygadzista = now.strftime("%H:%M:%S")
            self.btn_przywolaj_brygadziste.background_normal = ''
            self.btn_przywolaj_brygadziste.background_color = utils.get_color_from_hex(self.check_color)
            self.btn_przywolaj_brygadziste.text = "Przywołaj\nBrygadzistę "+self.data_brygadzista
        elif touch.button == 'right'  and self.wcisnieto_brygadzista == True:
            self.wcisnieto_brygadzista = False
            self.btn_przywolaj_brygadziste.background_color = self.default_button_color
            self.btn_przywolaj_brygadziste.background_normal = self.default_background_normal
            self.btn_przywolaj_brygadziste.text = "Przywołaj\nBrygadzistę"
        self.reconnectMQTT()
        self.wyslij_MQTT()




    def btn_przywolaj_narzedziowca_action(self, instance, touch):
        if not self.btn_przywolaj_narzedziowca.collide_point(touch.x, touch.y):
            return
        if touch.button == 'left' and self.wcisnieto_narzedziowiec == False:
            self.wcisnieto_narzedziowiec = True
            now = czas.now()
            self.data_narzedziowiec = now.strftime("%H:%M:%S")
            self.btn_przywolaj_narzedziowca.background_normal = ''
            self.btn_przywolaj_narzedziowca.background_color = utils.get_color_from_hex(self.check_color)
            self.btn_przywolaj_narzedziowca.text = "Przywołaj\nNarzędziowca "+ self.data_narzedziowiec
        elif touch.button == 'right' and self.wcisnieto_narzedziowiec == True:
            self.wcisnieto_narzedziowiec = False
            self.btn_przywolaj_narzedziowca.background_color = self.default_button_color
            self.btn_przywolaj_narzedziowca.background_normal = self.default_background_normal
            self.btn_przywolaj_narzedziowca.text = "Przywołaj\nNarzędziowca"
        self.reconnectMQTT()
        self.wyslij_MQTT()




    def btn_przywolaj_utrzymanie_action(self, instance, touch):
        if not self.btn_przywolaj_utrzymanie.collide_point(touch.x, touch.y):
            return
        if touch.button == 'left' and self.wcisnieto_utrzymanie == False:
            self.wcisnieto_utrzymanie = True
            now = czas.now()
            self.data_utrzymanie = now.strftime("%H:%M:%S")
            self.btn_przywolaj_utrzymanie.background_normal = ''
            self.btn_przywolaj_utrzymanie.background_color = utils.get_color_from_hex(self.check_color)
            self.btn_przywolaj_utrzymanie.text = "Przywołaj\nUtrzymanie ruchu "+self.data_utrzymanie
        elif touch.button == 'right'  and self.wcisnieto_utrzymanie == True:
            self.wcisnieto_utrzymanie = False
            self.btn_przywolaj_utrzymanie.background_color = self.default_button_color
            self.btn_przywolaj_utrzymanie.background_normal = self.default_background_normal
            self.btn_przywolaj_utrzymanie.text = "Przywołaj\nUtrzymanie ruchu"
        self.reconnectMQTT()
        self.wyslij_MQTT()

    def wyslij_MQTT(self):
        now = czas.now()

        #czas_n = now.strftime("%H:%M:%S")
        czas_n = now.isoformat()
        dane_mqtt = {"MASZYNA": maszyna,
                     "MAGAZYN": self.wcisnieto_magazyn,
                     "NASTAWIACZ": self.wcisnieto_nastawiacz,
                     "JAKOSC": self.wcisnieto_jakosc,
                     "BRYGADZISTA": self.wcisnieto_brygadzista,
                     "NARZEDZIOWIEC": self.wcisnieto_narzedziowiec,
                     "UTRZYMANIE": self.wcisnieto_utrzymanie,
                     "DATA": czas_n}

        json_mqtt = json.dumps(dane_mqtt)
        mqttClient.publish(miejsce + '/POWIADOMIENIA', json_mqtt)

        print(
            colored('MQTT wysylanie: ' +miejsce + '/POWIADOMIENIA '+json_mqtt, on_color=self.info_on_color))
        konsola_page.print_console('MQTT wysylanie: ' +miejsce + '/POWIADOMIENIA '+json_mqtt,
                                   konsola_page.info_console_on_color)


    def default_buttons_color(self):
        self.btn_przywolaj_magazyn.background_color = self.default_button_color
        self.btn_przywolaj_nastawiacza.background_color = self.default_button_color
        self.btn_przywolaj_jakosc.background_color = self.default_button_color
        self.btn_przywolaj_brygadziste.background_color = self.default_button_color
        self.btn_przywolaj_narzedziowca.background_color = self.default_button_color
        self.btn_przywolaj_utrzymanie.background_color = self.default_button_color
        self.btn_przywolaj_kasuj.background_color = self.default_button_color


        self.btn_przywolaj_magazyn.background_normal = self.default_background_normal
        self.btn_przywolaj_nastawiacza.background_normal = self.default_background_normal
        self.btn_przywolaj_jakosc.background_normal = self.default_background_normal
        self.btn_przywolaj_brygadziste.background_normal = self.default_background_normal
        self.btn_przywolaj_narzedziowca.background_normal = self.default_background_normal
        self.btn_przywolaj_utrzymanie.background_normal = self.default_background_normal
        self.btn_przywolaj_kasuj.background_normal = self.default_background_normal

        self.btn_przywolaj_magazyn.text="Przywołaj\nMagazyn"
        self.btn_przywolaj_nastawiacza.text="Przywołaj\nNastawiacza"
        self.btn_przywolaj_jakosc.text="Przywołaj\nKontrolę jakości"
        self.btn_przywolaj_brygadziste.text="Przywołaj\nBrygadzistę"
        self.btn_przywolaj_narzedziowca.text="Przywołaj\nNarzędziowca"
        self.btn_przywolaj_utrzymanie.text="Przywołaj\nUtrzymanie ruchu"
        self.btn_przywolaj_kasuj.text="Kasuj\nPrzywołanie"

    def reconnectMQTT(self):
        global mqttPort
        #print(colored('połączenie MQTT: ' + str(mqttClient.is_connected()), on_color=self.info_on_color))
        #konsola_page.print_console('połączenie MQTT: ' + str(mqttClient.is_connected()), konsola_page.info_console_on_color)
        try:
            if mqttClient.is_connected():
                mqttClient.disconnect()
            mqttClient.connect(mqttBroker, port=mqttPort)

        except:
            print(colored('MATT brak połączenia', on_color=self.info_on_color))
            konsola_page.print_console('MQTT brak połączenia', '#ff0000')

    def przyciski_z_pliku(self):
        if wc_magazyn:
            self.btn_przywolaj_magazyn.background_normal = ''
            self.btn_przywolaj_magazyn.background_color = utils.get_color_from_hex(self.check_color)
            self.btn_przywolaj_magazyn.text = "Przywołaj\nMagazyn "+dat_magazyn
            self.wcisnieto_magazyn = True
        if wc_nastawiacz:
            self.btn_przywolaj_nastawiacza.background_normal = ''
            self.btn_przywolaj_nastawiacza.background_color = utils.get_color_from_hex(self.check_color)
            self.btn_przywolaj_nastawiacza.text = "Przywołaj\nNastawiacza "+dat_nastawiacz
            self.wcisnieto_nastawiacz = True
        if wc_jakosc:
            self.btn_przywolaj_jakosc.background_normal = ''
            self.btn_przywolaj_jakosc.background_color = utils.get_color_from_hex(self.check_color)
            self.btn_przywolaj_jakosc.text = "Przywołaj\nKontrolę jakości "+dat_jakosc
            self.wcisnieto_jakosc = True
        if wc_brygadzista:
            self.btn_przywolaj_brygadziste.background_normal = ''
            self.btn_przywolaj_brygadziste.background_color = utils.get_color_from_hex(self.check_color)
            self.btn_przywolaj_brygadziste.text = "Przywołaj\nBrygadzistę "+dat_brygadzista
            self.wcisnieto_brygadzista = True
        if wc_narzedziowiec:
            self.btn_przywolaj_narzedziowca.background_normal = ''
            self.btn_przywolaj_narzedziowca.background_color = utils.get_color_from_hex(self.check_color)
            self.btn_przywolaj_narzedziowca.text = "Przywołaj\nNarzędziowca "+dat_narzedziowiec
            self.wcisnieto_narzedziowiec = True
        if wc_utrzymanie:
            self.btn_przywolaj_utrzymanie.background_normal = ''
            self.btn_przywolaj_utrzymanie.background_color = utils.get_color_from_hex(self.check_color)
            self.btn_przywolaj_utrzymanie.text = "Przywołaj\nUtrzymanie ruchu "+dat_utrzymanie
            self.wcisnieto_utrzymanie = True





class WtryskarkaPage(StackLayout):
    def __init__(self, **kwargs):
        global brak_conf
        global stop_application
        global wersja
        global przycisk
        global wtrysk_s
        global wybrak_s
        global wsp_wys_s
        global start_text

        super().__init__(**kwargs)
        self.info_on_color = 'on_blue'
        self.info_console_on_color = '#33ccff'

        self.cols = 1
        self.console_size = 0.6
        self.liczba_przyciskow = 10.0
        Window.bind(on_request_close=self.exit_check)
        Window.bind(on_resize=self.on_window_resize)


        self.console = RstDocument(text='',
                                   size_hint=(1, self.console_size),
                                   background_color=(
                                       51 / 255.0, 51 / 255.0, 51 / 255.0, 1))  # create a text input instance

        self.counter = 0

        self.btn_praca = Button(text='Praca', size_hint=(1, 1.0 / self.liczba_przyciskow))
        self.btn_praca.bind(on_press=self.btn_praca_action)

        self.btn_proby = Button(text="Próby technologiczne", size_hint=(1, 1.0 / self.liczba_przyciskow))
        self.btn_proby.bind(on_press=self.btn_proby_action)

        self.btn_postoj = Button(text="Postój planowany", size_hint=(1, 1.0 / self.liczba_przyciskow))
        self.btn_postoj.bind(on_press=self.btn_postoj_action)

        self.btn_przezbrajanie = Button(text="Przezbrajanie", size_hint=(1, 1.0 / self.liczba_przyciskow))
        self.btn_przezbrajanie.bind(on_press=self.btn_przezbrajanie_action)

        self.btn_susz_m = Button(text="Suszenie materiału", size_hint=(1, 1.0 / self.liczba_przyciskow))
        self.btn_susz_m.bind(on_press=self.btn_susz_m_action)

        self.btn_awaria_m = Button(text="Awaria maszyny", size_hint=(1, 1.0 / self.liczba_przyciskow))
        self.btn_awaria_m.bind(on_press=self.btn_awaria_m_action)

        self.btn_awaria_f = Button(text="Awaria formy", size_hint=(1, 1.0 / self.liczba_przyciskow))
        self.btn_awaria_f.bind(on_press=self.btn_awaria_f_action)

        self.btn_brak_zaop = Button(text="Brak zaopatrzenia", size_hint=(1, 1.0 / self.liczba_przyciskow))
        self.btn_brak_zaop.bind(on_press=self.btn_brak_zaop_action)

        self.btn_brak_oper = Button(text="Brak operatora", size_hint=(1, 1.0 / self.liczba_przyciskow))
        self.btn_brak_oper.bind(on_press=self.btn_brak_oper_action)

        self.btn_nie_zgloszono = Button(text="Nie zgłoszono", size_hint=(1, 1.0 / self.liczba_przyciskow))

        # self.btn_wybrak_op = Button(text="Wada detalu", size_hint=(1, 1.0 / self.liczba_przyciskow))
        # self.btn_wybrak_op.bind(on_press=self.btn_postoj_action)
        ##Przywoływanie ##Przywoływanie ##Przywoływanie ##Przywoływanie ##Przywoływanie ##Przywoływanie ##Przywoływanie


        self.btn_praca.font_size = "28sp"
        self.btn_awaria_m.font_size = "28sp"
        self.btn_awaria_f.font_size = "28sp"
        self.btn_przezbrajanie.font_size = "28sp"
        self.btn_proby.font_size = "28sp"
        self.btn_susz_m.font_size = "28sp"
        self.btn_brak_zaop.font_size = "28sp"
        self.btn_postoj.font_size = "28sp"
        self.btn_brak_zaop.font_size = "28sp"
        self.btn_brak_oper.font_size = "28sp"
        self.btn_nie_zgloszono.font_size = "28sp"

        # self.btn_wybrak_op.font_size = "20sp"
        self.default_button_color = self.btn_praca.background_color
        self.default_background_normal = self.btn_praca.background_normal

        # self.default_button_color = utils.get_color_from_hex("009EE0")
        # self.default_background_normal = 'white'
        # włączenie przycisku PRACA
        if przycisk == 'P1':
            self.btn_praca_action(None)
        elif przycisk == 'P2':
            self.btn_proby_action(None)
        elif przycisk == 'P3':
            self.btn_postoj_action(None)
        elif przycisk == 'P4':
            self.btn_przezbrajanie_action(None)
        elif przycisk == 'P5':
            self.btn_suszenie_m_action(None)
        elif przycisk == 'P6':
            self.btn_awaria_m_action(None)
        elif przycisk == 'P7':
            self.btn_awaria_f_action(None)
        elif przycisk == 'P8':
            self.btn_brak_zaop_action(None)
        elif przycisk == 'P9':
            self.btn_brak_oper_action(None)
        elif przycisk == 'P10':
            self.btn_nie_zgloszono_color()
        else:
            self.btn_praca_action(None)

        self.text_error = '''
        
Brak pliku konfiguracyjnego app.ini w folderze data.
Przykład pliku:

[DEFAULT]
maszyna = TEST
miejsce = SKOCZOW
czas_wysylania = 20
dolna_granica_wsp = 1
gorna_granica_wsp = 2
        '''
        if brak_conf:
            text_error = TextInput(text=self.text_error)
            self.add_widget(text_error)
            stop_application = True
            # Window.bind(on_request_close=app.on_close)
            return

        self.add_widget(self.btn_praca)
        self.add_widget(self.btn_proby)
        self.add_widget(self.btn_postoj)
        self.add_widget(self.btn_przezbrajanie)
        self.add_widget(self.btn_susz_m)
        self.add_widget(self.btn_awaria_m)
        self.add_widget(self.btn_awaria_f)
        self.add_widget(self.btn_brak_zaop)
        self.add_widget(self.btn_brak_oper)
        self.add_widget(self.btn_nie_zgloszono)


        # self.add_widget(self.btn_wybrak_op)# przycisk wady detalu

        return

    def exit_check(self, *args):
        global stop_application
        if stop_application:
            return False
        return True  # block app's exit
        self.counter += 1
        if self.counter < 5:
            self.text = str(self.counter)
            return True  # block app's exit
        else:
            return False  # let the app close

    def on_window_resize(self, window, width, height):
        global win_width
        global win_height
        Window.size = (win_width, win_height)
        pass

    def btn_praca_action(self, instance):
        global przycisk
        przycisk = 'P1'
        print(colored('P1 -> PRACA', on_color=self.info_on_color))
        konsola_page.print_console('P1 -> PRACA', self.info_console_on_color)
        self.default_buttons_color()
        self.btn_praca.background_normal = ''
        self.btn_praca.background_color = utils.get_color_from_hex("#608934")

    def btn_proby_action(self, instance):
        global przycisk
        przycisk = 'P2'
        print(colored('P2 -> PROBY TECHNOLOGICZNE', on_color=self.info_on_color))
        konsola_page.print_console('P2 -> PROBY TECHNOLOGICZNE', self.info_console_on_color)
        self.default_buttons_color()
        self.btn_proby.background_normal = ''
        self.btn_proby.background_color = utils.get_color_from_hex("#92D050")
    def btn_postoj_action(self, instance):
        global przycisk
        przycisk = 'P3'
        print(colored('P3 -> POSTOJ', on_color=self.info_on_color))
        konsola_page.print_console('P3 -> POSTOJ', self.info_console_on_color)
        self.default_buttons_color()
        self.btn_postoj.background_normal = ''
        self.btn_postoj.background_color = utils.get_color_from_hex("#BFBFBF")

    def btn_przezbrajanie_action(self, instance):
        global przycisk
        przycisk = 'P4'
        print(colored('P4 -> PRZEZBRAJANIE', on_color=self.info_on_color))
        konsola_page.print_console('P4 -> PRZEZBRAJANIE', self.info_console_on_color)
        self.default_buttons_color()
        self.btn_przezbrajanie.background_normal = ''
        self.btn_przezbrajanie.background_color = utils.get_color_from_hex("#1F618D")

    def btn_susz_m_action(self, instance):
        global przycisk
        przycisk = 'P5'
        print(colored('P5 -> SUSZENIE MATERIAŁU', on_color=self.info_on_color))
        konsola_page.print_console('P5 -> SUSZENIE MATERIAŁU', self.info_console_on_color)
        self.default_buttons_color()
        self.btn_susz_m.background_normal = ''
        self.btn_susz_m.background_color = utils.get_color_from_hex("#8d6e63")

    def btn_awaria_m_action(self, instance):
        global przycisk
        przycisk = 'P6'
        print(colored('P6 -> AWARIA MASZYNY', on_color=self.info_on_color))
        konsola_page.print_console('P6 -> AWARIA MASZYNY', self.info_console_on_color)
        self.default_buttons_color()
        self.btn_awaria_m.background_normal = ''
        self.btn_awaria_m.background_color = utils.get_color_from_hex("#7B241C")

    def btn_awaria_f_action(self, instance):
        global przycisk
        przycisk = 'P7'
        print(colored('P67 -> AWARIA FORMY', on_color=self.info_on_color))
        konsola_page.print_console('P7 -> AWARIA FORMY', self.info_console_on_color)
        self.default_buttons_color()
        self.btn_awaria_f.background_normal = ''
        self.btn_awaria_f.background_color = utils.get_color_from_hex("#C0392B")

    def btn_brak_zaop_action(self, instance):
        global przycisk
        przycisk = 'P8'
        print(colored('P8 -> BRAK ZAOPATRZENIA', on_color=self.info_on_color))
        konsola_page.print_console('P8 -> BRAK ZAOPATRZENIA', self.info_console_on_color)
        self.default_buttons_color()
        self.btn_brak_zaop.background_normal = ''
        self.btn_brak_zaop.background_color = utils.get_color_from_hex("#CEC250")
    def btn_brak_oper_action(self, instance):
        global przycisk
        przycisk = 'P9'
        print(colored('P9 -> BRAK OPERATORA', on_color=self.info_on_color))
        konsola_page.print_console('P9 -> BRAK OPERATORA', self.info_console_on_color)
        self.default_buttons_color()
        self.btn_brak_oper.background_normal = ''
        self.btn_brak_oper.background_color = utils.get_color_from_hex("#8E44AD")

    def btn_nie_zgloszono_color(self):
        global przycisk
        przycisk = 'P10'
        print(colored('P10-> NIE ZGLOSZONO', on_color=self.info_on_color))
        konsola_page.print_console('P10 -> NIE ZGLOSZONO', self.info_console_on_color)
        self.default_buttons_color()
        self.btn_nie_zgloszono.background_normal = ''
        self.btn_nie_zgloszono.background_color = utils.get_color_from_hex("#FF0000")

        ###############################################################################################################



    def default_buttons_color(self):
        self.btn_praca.background_color = self.default_button_color
        self.btn_awaria_m.background_color = self.default_button_color
        self.btn_awaria_f.background_color = self.default_button_color
        self.btn_przezbrajanie.background_color = self.default_button_color
        self.btn_susz_m.background_color = self.default_button_color
        self.btn_proby.background_color = self.default_button_color
        self.btn_brak_zaop.background_color = self.default_button_color
        self.btn_brak_oper.background_color = self.default_button_color
        self.btn_postoj.background_color = self.default_button_color
        self.btn_nie_zgloszono.background_color = self.default_button_color

        self.btn_praca.background_normal = self.default_background_normal
        self.btn_awaria_m.background_normal = self.default_background_normal
        self.btn_awaria_f.background_normal = self.default_background_normal
        self.btn_przezbrajanie.background_normal = self.default_background_normal
        self.btn_susz_m.background_normal = self.default_background_normal
        self.btn_proby.background_normal = self.default_background_normal
        self.btn_brak_zaop.background_normal = self.default_background_normal
        self.btn_brak_oper.background_normal = self.default_background_normal
        self.btn_postoj.background_normal = self.default_background_normal
        self.btn_nie_zgloszono.background_normal = self.default_background_normal


wtryskarka_page = WtryskarkaPage()
wywolania_page = WywolaniaPage()

class App(App):
    def __init__(self):
        super().__init__()

        self.title = f'{maszyna} {miejsce} {czas_wysylania}s {LOCAL_IP} WERSJA: {wersja}'
        self.icon = os.path.join('data', 'img', 'icon.png')



    def TCP_IP(self):
        global stop_application
        global przycisk
        global wtryskarka_page
        global wywolania_page
        # Create a TCP/IP socket

        while True:
            if stop_application:
                break
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Bind the socket to the address given on the command line
            server_address = (LOCAL_IP, TCP_PORT)
            try:
                sock.bind(server_address)
            except:
                print('duplikat programu zostanie on zamknięty')
                os._exit(0)
                ctypes.windll.user32.MessageBoxW(0, "Ponowne uruchomienie programu\nprogram zostanie wyłączony", "Duplikat programu", 0)
                stop_application = True



            print(colored('Start serwera TCP/IP {} port {}'.format(*sock.getsockname()), 'magenta'))
            konsola_page.print_console('Start serwera TCP/IP {} port {}'.format(*sock.getsockname()), '#ff00ff')
            sock.listen(1)

            while True:
                if stop_application:
                    break
                # print('Oczekiwanie na połączenie')
                connection, client_address = sock.accept()

                print(colored(f'LanTick połączył się IP: {client_address[0]}, port: {client_address[1]}', 'magenta'))
                konsola_page.print_console(f'LanTick połączył się IP: {client_address[0]}, port: {client_address[1]}',
                                   '#ff00ff')
                try:
                    # print('połączony klient:', client_address)
                    while True:
                        if stop_application:
                            break
                        data = connection.recv(BUFFER_SIZE)
                        sygnal = data.decode()
                        if sygnal == 'wtrysk':
                            # print(colored(f'WTRYSK', 'blue'))
                            self.inter_wtrysk()
                            raise Exception('Restart servera-wtrysk')
                        elif sygnal == 'wybrak':
                            # print(colored(f'WYBRAK', 'red'))
                            self.inter_wybrak()
                            raise Exception('Restart servera-wybrak')
                        elif sygnal == 'automat':
                            #AUTOMAT KIEDY PRÓBY
                            if przycisk == "P2":
                                print(colored(f'AUTOMAT W CZASIE PRÓB--> przycisk P2', 'green'))
                                konsola_page.print_console(f'AUTOMAT W CZASIE PRÓB--> przycisk P2', '#9966ff')
                                raise Exception('Restart servera-automat')
                            else:
                                #AUTOMAT BEZ PRÓB
                                print(colored(f'AUTOMAT --> wlaczenie przycisku P1', 'green'))
                                konsola_page.print_console(f'AUTOMAT --> wlaczenie przycisku P1', '#9966ff')
                                wtryskarka_page.btn_praca_action(None)
                                raise Exception('Restart servera-automat')

                        else:
                            break

                except Exception as e:
                    print(colored(f'Wyjątek w funkcji TCP_IP: {str(e)}', 'red'))
                    konsola_page.print_console(f'Wyjątek w funkcji TCP_IP: {str(e)}', '#ff0000')
                    connection.close()
                    break


    def czysc_przyciski(self):
        global s_awaria_m
        global s_awaria_f
        global s_przezbrajanie
        global s_susz_m
        global s_proby_tech
        global s_brak_zaop
        global s_brak_oper
        global s_postoj

        s_awaria_m = 0
        s_awaria_f = 0
        s_przezbrajanie = 0
        s_susz_m = 0
        s_proby_tech = 0
        s_brak_zaop = 0
        s_brak_oper = 0
        s_postoj = 0

        # zliczanie cykli wtrysku

    def inter_wtrysk(self):
        global wtrysk_s
        global wtrysk_s
        global cykl_s
        global cykl_e
        global czas_cyklu_s
        global pierwsze_uruchomienie
        global s_postoj_n
        kolor = 'blue'
        console_color = '#33ccff'

        # if przycisk == "P1":
        # dodanie petli sprawdzajacej stan wejscia

        # obliczenie bierzacego czasu cykli i dodanie go do sredniej
        cykl_e = time.time()
        czas_obecnego_cyklu = (cykl_e - cykl_s)
        czas_cyklu_s = czas_cyklu_s + czas_obecnego_cyklu

        cykl_s = time.time()
        wtrysk_s = wtrysk_s + 1

        print(colored("WTRYSK czas cyklu: " + str(czas_obecnego_cyklu) + ' liczba cykli do wyslania: ' + str(wtrysk_s),
                      kolor))

        konsola_page.print_console(
            "WTRYSK czas cyklu: " + str(czas_obecnego_cyklu) + ' liczba cykli do wyslania: ' + str(wtrysk_s),
            console_color)
        # print("cykl_s: "+ str(wtrysk_s))
        pierwsze_uruchomienie = False

        return

    def inter_wybrak(self):
        global wybrak_s
        global s_postoj_n
        kolor = 'red'
        console_color = '#ff9933'

        wybrak_s = wybrak_s + 1
        print(colored("WYBRAK: liczba wybrakow: " + str(wybrak_s), kolor))
        konsola_page.print_console("WYBRAK: liczba wybrakow: " + str(wybrak_s), console_color)

        # print("wybrak_s: "+ str(wybrak_s))

        return

    def wyslij_dane_SQL(self):
        global czas_wysylania
        global stop_application


        # wyjście z funkcji jesli zamykanie okna
        if stop_application:
            return

        self.thread_SQL = threading.Timer(czas_wysylania, self.wyslij_dane_SQL)
        self.thread_SQL.start()


        kolor = 'green'
        console_color = '#ccff33'
        console_info_color = '#944dff'
        # while True:
        # threading.Timer(czas_wysylania, wyslij_dane_SQL).start()
        # time.sleep(czas_wysylania)
        # now = datetime.datetime.now()
        # print colored("PETLA START DATA: "+str(now.strftime("%Y-%m-%d %H:%M:%S"))+"",'cyan')
        # print colored("czas wysylania "+str(czas_wysylania)+" s",'cyan')

        global nazwa_bazy
        global haslo_bazy
        global ip_bazy
        global port_bazy
        global user_bazy
        global tabela_bazy
        global zapytanie_pop_data
        global pop_insert_date

        global wtrysk_s
        global wybrak_s
        global czas_cyklu_s
        global pop_wtrysk_s

        global cykl_s
        global cykl_e

        # global czas_wysylania
        global wsp_wys_s

        global s_postoj_n
        global s_awaria_m
        global s_awaria_f
        global s_przezbrajanie
        global s_susz_m
        global s_proby_tech
        global s_brak_zaop
        global s_brak_oper
        global s_postoj

        global dolna_granica_wsp
        global gorna_granica_wsp

        global przycisk

        zapytanie_SQL = ""

        # inkrementacja wszystkich wartosci przed sprawdzeniem czy jest internet
        if przycisk == "P1" or przycisk == "P10":
            if wtrysk_s <= pop_wtrysk_s:
                s_postoj_n = s_postoj_n + 1
        if przycisk == "P2":
            s_proby_tech = s_proby_tech + 1
        if przycisk == "P3":
            s_postoj = s_postoj + 1
        if przycisk == "P4":
            s_przezbrajanie = s_przezbrajanie + 1
        if przycisk == "P5":
            s_susz_m = s_susz_m + 1
        if przycisk == "P6":
            s_awaria_m = s_awaria_m + 1
        if przycisk == "P7":
            s_awaria_f = s_awaria_f + 1
        if przycisk == "P8":
            s_brak_zaop = s_brak_zaop + 1
        if przycisk == "P9":
            s_brak_oper = s_brak_oper + 1


        pop_wtrysk_s = wtrysk_s
        # sprawdzenie czy jest internet
        if internet_on() == False:
            print(colored(f"WYSYLANIE: czekam na sieć lan ping bramy: 10.0.0.1: {ping_server}\n", kolor))
            konsola_page.print_console(f"WYSYLANIE: czekam na sieć lan ping bramy: 10.0.0.1: {ping_server}\n", console_color)
            # continue
            return

        # Biblioteka pymysql
        conn = pymysql.connect(passwd=haslo_bazy, db=nazwa_bazy, host=ip_bazy, port=port_bazy, user=user_bazy)

        cursor = conn.cursor()

        cursor.execute(zapytanie_pop_data)
        records = cursor.fetchall()
        for row in records:
            pop_insert_date = row[0]

        ## Jeśli nie ma wcześniejszych wpisów to data obecna
        if pop_insert_date is None:
            cursor.execute("select now()")
            records = cursor.fetchall()
            for row in records:
                pop_insert_date = row[0]

        if przycisk == "P1" or przycisk == "P10":

            czas_wtrysk_s = 0
            if wtrysk_s != 0:
                if (czas_cyklu_s / wtrysk_s) > czas_wysylania:
                    czas_wtrysk_s = 0
                    print(colored('CZAS CYKLU JEST WIĘKSZY NIŻ CZAS WYSYŁANIA ZOSTANIE ON WYZEROWANY', kolor))
                    konsola_page.print_console('CZAS CYKLU JEST WIĘKSZY NIŻ CZAS WYSYŁANIA ZOSTANIE ON WYZEROWANY',
                                       console_color)
                else:
                    czas_wtrysk_s = (czas_cyklu_s / wtrysk_s)

                if czas_wtrysk_s != 0:
                    # sprawdzenie czy wspolczynnik wysylania miesci sie w dopuszczalnych granicach
                    if czas_wysylania / czas_wtrysk_s > gorna_granica_wsp:
                        wsp_wys_s = wsp_wys_s
                    elif czas_wysylania / czas_wtrysk_s < dolna_granica_wsp:
                        wsp_wys_s = wsp_wys_s
                    else:
                        if czas_wysylania / czas_wtrysk_s > 1:
                            wsp_wys_s = czas_wysylania / czas_wtrysk_s
                        else:
                            wsp_wys_s = wsp_wys_s
                czas_cyklu_s = 0
            rzecz_wtrysk_s = wtrysk_s - wybrak_s
            if rzecz_wtrysk_s < 0:
                rzecz_wtrysk_s = 0
            # conn = MySQLdb.connect(passwd="Pro2017#",db="14443643_projekt",host="89.161.232.241",port=3306,user="14443643_projekt")

            # dodano sprawdzanie czy nie było operatora i wpisywanie 0 w czas cyklu
            if s_postoj_n > 0:
                #postój nieplanowany
                wtryskarka_page.btn_nie_zgloszono_color()
                zapytanie_SQL = "INSERT INTO `" + nazwa_bazy + "`.`" + tabela_bazy + "` (`miejsce`, `maszyna`, `wtrysk`, `wybrak`, `postoj_n`, `awaria_m`, `awaria_f`, `przezbrajanie`, `proby_tech`, `brak_zaop`, `brak_oper`, `susz_m`, `postoj`,  `czas_cyklu`, `pop_insert`) VALUES ('" + miejsce + "', '" + maszyna + "', '" + str(
                    rzecz_wtrysk_s) + "', '" + str(wybrak_s) + "', '" + str(
                    round(s_postoj_n * wsp_wys_s, 3)) + "', '0', '0', '0', '0', '0', '0', '0', '0' , '0', '"+str(pop_insert_date)+"')"
                cursor.execute(zapytanie_SQL)
                print(colored("WYSYLANIE " + zapytanie_SQL + "", kolor))
                konsola_page.print_console(f'CZAS WYSYLANIA {czas_wysylania}, czas: {str(datetime.datetime.now())[:19]}',
                                   console_info_color)
                konsola_page.print_console("WYSYLANIE " + zapytanie_SQL + "", console_color)
                pierwsze_uruchomienie = True
                czas_cyklu_s = 0
                cykl_s = 0
                cykl_e = 0

            else:
                zapytanie_SQL = "INSERT INTO `" + nazwa_bazy + "`.`" + tabela_bazy + "` (`miejsce`, `maszyna`, `wtrysk`, `wybrak`, `postoj_n`, `awaria_m`, `awaria_f`, `przezbrajanie`, `proby_tech`, `brak_zaop`, `brak_oper`, `susz_m`, `postoj`,  `czas_cyklu`, `pop_insert`) VALUES ('" + miejsce + "', '" + maszyna + "', '" + str(
                    rzecz_wtrysk_s) + "', '" + str(wybrak_s) + "', '" + str(
                    round(s_postoj_n * wsp_wys_s, 3)) + "', '0', '0', '0', '0', '0', '0', '0', '0', '" + str(
                    round(czas_wtrysk_s, 3)) + "' , '"+str(pop_insert_date)+"')"
                #print(zapytanie_SQL)
                cursor.execute(zapytanie_SQL)
                print(colored("WYSYLANIE " + zapytanie_SQL + "", kolor))
                konsola_page.print_console(f'CZAS WYSYLANIA {czas_wysylania}, czas: {str(datetime.datetime.now())[:19]}',
                                   console_info_color)
                konsola_page.print_console("WYSYLANIE " + zapytanie_SQL + "", console_color)

            print(colored("Wspolczynnik wysylania s = " + str(wsp_wys_s), 'cyan'))
            konsola_page.print_console("Wspolczynnik wysylania s = " + str(wsp_wys_s), console_info_color)
            wtrysk_s = 0
            pop_wtrysk_s = 0
            wybrak_s = 0
            s_postoj_n = 0

        if przycisk == "P2":
            # s_proby_tech = 1
            zapytanie_SQL = "INSERT INTO `" + nazwa_bazy + "`.`" + tabela_bazy + "` (`miejsce`, `maszyna`, `wtrysk`, `wybrak`, `postoj_n`, `awaria_m`, `awaria_f`, `przezbrajanie`, `proby_tech`, `brak_zaop`, `brak_oper`, `susz_m`, `postoj`,  `czas_cyklu`, `pop_insert`) VALUES ('" + miejsce + "', '" + maszyna + "', '0', '0', '0', '0', '0', '0', '" + str(
                round(s_proby_tech * wsp_wys_s, 3)) + "', '0', '0', '0', '0', '0', '"+str(pop_insert_date)+"')"
            cursor.execute(zapytanie_SQL)
            print(colored("JEST: PROBY\n", 'green'))
            print(colored("WYSYLANIE " + zapytanie_SQL + "", kolor))

            konsola_page.print_console(f'CZAS WYSYLANIA {czas_wysylania}, czas: {str(datetime.datetime.now())[:19]}',
                               console_info_color)
            konsola_page.print_console("JEST: PROBY\n", console_info_color)
            konsola_page.print_console("WYSYLANIE " + zapytanie_SQL + "", console_color)
            pierwsze_uruchomienie = True
            czas_cyklu_s = 0
            cykl_s = 0
            cykl_e = 0
            wtrysk_s = 0
            pop_wtrysk_s = 0

        if przycisk == "P3":
            # s_postoj = 1
            zapytanie_SQL = "INSERT INTO `" + nazwa_bazy + "`.`" + tabela_bazy + "` (`miejsce`, `maszyna`, `wtrysk`, `wybrak`, `postoj_n`, `awaria_m`, `awaria_f`, `przezbrajanie`, `proby_tech`, `brak_zaop`, `brak_oper`, `susz_m`, `postoj`,  `czas_cyklu`, `pop_insert`) VALUES ('" + miejsce + "', '" + maszyna + "', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0','" + str(
                round(s_postoj * wsp_wys_s, 3)) + "', '0', '"+str(pop_insert_date)+"')"
            cursor.execute(zapytanie_SQL)
            print(colored("JEST: POSTOJ\n", 'green'))
            print(colored("WYSYLANIE " + zapytanie_SQL + "", kolor))

            konsola_page.print_console(f'CZAS WYSYLANIA {czas_wysylania}, czas: {str(datetime.datetime.now())[:19]}',
                               console_info_color)
            konsola_page.print_console("JEST: POSTOJ\n", console_info_color)
            konsola_page.print_console("WYSYLANIE " + zapytanie_SQL + "", console_color)
            pierwsze_uruchomienie = True
            czas_cyklu_s = 0
            cykl_s = 0
            cykl_e = 0
            wtrysk_s = 0
            pop_wtrysk_s = 0

        if przycisk == "P4":
            # s_przezbrajanie = 1
            zapytanie_SQL = "INSERT INTO `" + nazwa_bazy + "`.`" + tabela_bazy + "` (`miejsce`, `maszyna`, `wtrysk`, `wybrak`, `postoj_n`, `awaria_m`, `awaria_f`, `przezbrajanie`, `proby_tech`, `brak_zaop`, `brak_oper`, `susz_m`, `postoj`,  `czas_cyklu`, `pop_insert`) VALUES ('" + miejsce + "', '" + maszyna + "', '0', '0', '0', '0', '0', '" + str(
                round(s_przezbrajanie * wsp_wys_s, 3)) + "', '0', '0', '0', '0', '0', '0', '"+str(pop_insert_date)+"')"
            cursor.execute(zapytanie_SQL)
            print(colored("JEST: PRZEZBRAJANIE\n", 'green'))
            print(colored("WYSYLANIE " + zapytanie_SQL + "", kolor))

            konsola_page.print_console(f'CZAS WYSYLANIA {czas_wysylania}, czas: {str(datetime.datetime.now())[:19]}',
                               console_info_color)
            konsola_page.print_console("JEST: PRZEZBRAJANIE\n", console_info_color)
            konsola_page.print_console("WYSYLANIE " + zapytanie_SQL + "", console_color)
            pierwsze_uruchomienie = True
            czas_cyklu_s = 0
            cykl_s = 0
            cykl_e = 0
            wtrysk_s = 0
            pop_wtrysk_s = 0

        if przycisk == "P5":
            # s_susz_m = 1
            zapytanie_SQL = "INSERT INTO `" + nazwa_bazy + "`.`" + tabela_bazy + "` (`miejsce`, `maszyna`, `wtrysk`, `wybrak`, `postoj_n`, `awaria_m`, `awaria_f`, `przezbrajanie`, `proby_tech`, `brak_zaop`, `brak_oper`, `susz_m`, `postoj`,  `czas_cyklu`, `pop_insert`) VALUES ('" + miejsce + "', '" + maszyna + "', '0', '0', '0', '0', '0', '0', '0', '0', '0', '" + str(
                round(s_susz_m * wsp_wys_s, 3)) + "', '0', '0','"+str(pop_insert_date)+"')"
            cursor.execute(zapytanie_SQL)
            print(colored("JEST: SUSZENIE MATERIAŁU\n", 'green'))
            print(colored("WYSYLANIE " + zapytanie_SQL + "", kolor))

            konsola_page.print_console(f'CZAS WYSYLANIA {czas_wysylania}, czas: {str(datetime.datetime.now())[:19]}',
                               console_info_color)
            konsola_page.print_console("JEST: SUSZENIE MATERIAŁU\n", console_info_color)
            konsola_page.print_console("WYSYLANIE " + zapytanie_SQL + "", console_color)
            pierwsze_uruchomienie = True
            czas_cyklu_s = 0
            cykl_s = 0
            cykl_e = 0
            wtrysk_s = 0
            pop_wtrysk_s = 0

        if przycisk == "P6":
            # s_awaria_m = 1
            zapytanie_SQL = "INSERT INTO `" + nazwa_bazy + "`.`" + tabela_bazy + "` (`miejsce`, `maszyna`, `wtrysk`, `wybrak`, `postoj_n`, `awaria_m`, `awaria_f`, `przezbrajanie`, `proby_tech`, `brak_zaop`, `brak_oper`, `susz_m`, `postoj`,  `czas_cyklu`, `pop_insert`) VALUES ('" + miejsce + "', '" + maszyna + "', '0', '0', '0', '" + str(
                round(s_awaria_m * wsp_wys_s, 3)) + "', '0', '0', '0', '0', '0', '0', '0', '0', '"+str(pop_insert_date)+"')"
            cursor.execute(zapytanie_SQL)
            print(colored("JEST: AWARIA MASZYNY\n", 'green'))
            print(colored("WYSYLANIE " + zapytanie_SQL + "", kolor))

            konsola_page.print_console(f'CZAS WYSYLANIA {czas_wysylania}, czas: {str(datetime.datetime.now())[:19]}',
                               console_info_color)
            konsola_page.print_console("JEST: AWARIA MASZYNY\n", console_info_color)
            konsola_page.print_console("WYSYLANIE " + zapytanie_SQL + "", console_color)
            pierwsze_uruchomienie = True
            czas_cyklu_s = 0
            cykl_s = 0
            cykl_e = 0
            wtrysk_s = 0
            pop_wtrysk_s = 0

        if przycisk == "P7":
            # s_awaria_f = 1
            zapytanie_SQL = "INSERT INTO `" + nazwa_bazy + "`.`" + tabela_bazy + "` (`miejsce`, `maszyna`, `wtrysk`, `wybrak`, `postoj_n`, `awaria_m`, `awaria_f`, `przezbrajanie`, `proby_tech`, `brak_zaop`, `brak_oper`, `susz_m`, `postoj`,  `czas_cyklu`, `pop_insert`) VALUES ('" + miejsce + "', '" + maszyna + "', '0', '0', '0', '0', '" + str(
                round(s_awaria_f * wsp_wys_s, 3)) + "', '0', '0', '0', '0', '0', '0', '0', '"+str(pop_insert_date)+"')"
            cursor.execute(zapytanie_SQL)
            print(colored("JEST: AWARIA FORMY\n", 'green'))
            print(colored("WYSYLANIE " + zapytanie_SQL + "", kolor))

            konsola_page.print_console(f'CZAS WYSYLANIA {czas_wysylania}, czas: {str(datetime.datetime.now())[:19]}',
                               console_info_color)
            konsola_page.print_console("JEST: AWARIA FORMY\n", console_info_color)
            konsola_page.print_console("WYSYLANIE " + zapytanie_SQL + "", console_color)
            pierwsze_uruchomienie = True
            czas_cyklu_s = 0
            cykl_s = 0
            cykl_e = 0
            wtrysk_s = 0
            pop_wtrysk_s = 0

        if przycisk == "P8":
            # s_brak_zaop = 1
            zapytanie_SQL = "INSERT INTO `" + nazwa_bazy + "`.`" + tabela_bazy + "` (`miejsce`, `maszyna`, `wtrysk`, `wybrak`, `postoj_n`, `awaria_m`, `awaria_f`, `przezbrajanie`, `proby_tech`, `brak_zaop`, `brak_oper`, `susz_m`, `postoj`,  `czas_cyklu`, `pop_insert`) VALUES ('" + miejsce + "', '" + maszyna + "', '0', '0', '0', '0', '0', '0', '0', '" + str(
                round(s_brak_zaop * wsp_wys_s, 3)) + "', '0', '0', '0', '0', '"+str(pop_insert_date)+"')"
            cursor.execute(zapytanie_SQL)
            print(colored("JEST: BRAK ZAOPATRZENIA\n", 'green'))
            print(colored("WYSYLANIE " + zapytanie_SQL + "", kolor))

            konsola_page.print_console(f'CZAS WYSYLANIA {czas_wysylania}, czas: {str(datetime.datetime.now())[:19]}',
                               console_info_color)
            konsola_page.print_console("JEST: BRAK ZAOPATRZENIA\n", console_info_color)
            konsola_page.print_console("WYSYLANIE " + zapytanie_SQL + "", console_color)
            pierwsze_uruchomienie = True
            czas_cyklu_s = 0
            cykl_s = 0
            cykl_e = 0
            wtrysk_s = 0
            pop_wtrysk_s = 0
        if przycisk == "P9":
            # s_brak_zaop = 1
            zapytanie_SQL = "INSERT INTO `" + nazwa_bazy + "`.`" + tabela_bazy + "` (`miejsce`, `maszyna`, `wtrysk`, `wybrak`, `postoj_n`, `awaria_m`, `awaria_f`, `przezbrajanie`, `proby_tech`, `brak_zaop`, `brak_oper`, `susz_m`, `postoj`,  `czas_cyklu`, `pop_insert`) VALUES ('" + miejsce + "', '" + maszyna + "', '0', '0', '0', '0', '0', '0', '0', '0','" + str(
                round(s_brak_oper * wsp_wys_s, 3)) + "', '0', '0', '0', '"+str(pop_insert_date)+"')"
            cursor.execute(zapytanie_SQL)
            print(colored("JEST: BRAK OPERATORA\n", 'green'))
            print(colored("WYSYLANIE " + zapytanie_SQL + "", kolor))

            konsola_page.print_console(f'CZAS WYSYLANIA {czas_wysylania}, czas: {str(datetime.datetime.now())[:19]}',
                               console_info_color)
            konsola_page.print_console("JEST: BRAK OPERATORA\n", console_info_color)
            konsola_page.print_console("WYSYLANIE " + zapytanie_SQL + "", console_color)
            pierwsze_uruchomienie = True
            czas_cyklu_s = 0
            cykl_s = 0
            cykl_e = 0
            wtrysk_s = 0
            pop_wtrysk_s = 0



        self.czysc_przyciski()  # wyzerowanie obliczonych wartosci
        conn.commit()

        cursor.close()
        conn.close()

    def on_start(self):
        from kivy.base import EventLoop, runTouchApp
        EventLoop.window.bind(on_keyboard=self.console_click)

    def console_click(self, windows, key, *args):

        if key == ord('z'):

            if not self.run_console:
                self.run_console = True
                self.pop_okno = self.screen_manager.current
                self.screen_manager.current = 'Konsola'
            else:
                self.run_console = False
                self.screen_manager.current = self.pop_okno

        if key == ord('r'):
            restart_program()

        if key == 32:
            if self.screen_manager.current == 'Wywolania':
                self.screen_manager.current = 'Wtryskarka'
            elif self.screen_manager.current == 'Wtryskarka':
                self.screen_manager.current = 'Wywolania'


    def build(self):
        global czas_wysylania
        global stop_app
        global start_text
        global wersja
        global przycisk
        global wtrysk_s
        global wybrak_s
        global wsp_wys_s
        global data_z_pliku
        global konsola_page

        self.run_console = False
        konsola_page.print_console(start_text, '#ffffff')

        if data_z_pliku:
            konsola_page.print_console(f'''[color=#FFFFFF]Wczytano dane z poprzedniego uruchomienia:[/color]\n
[color=#FFFFFF]PRZYCISK:[/color]    [color=#FFFFFF]{przycisk}[/color]\n
[color=#FFFFFF]WTRYSK:[/color]  [color=#FFFFFF]{wtrysk_s}[/color]\n
[color=#FFFFFF]WYBRAK:[/color]  [color=#FFFFFF]{wybrak_s}[/color]\n
[color=#FFFFFF]WSPÓŁCZYNNIK WYSYŁANIA:[/color]  [color=#FFFFFF]{wsp_wys_s}[/color]''', '#ffffff')
        # Watek wysylania do bazy danuch

        # Initial, connection screen (we use passed in name to activate screen)
        # First create a page, then a new screen, add page to screen and screen to screen manager

        self.screen_manager = ScreenManager()


        self.screen_wtryskarka = Screen(name='Wtryskarka')
        self.screen_wtryskarka.add_widget(wtryskarka_page)
        self.screen_manager.add_widget(self.screen_wtryskarka)

        # Info page

        self.screen_wywolania = Screen(name='Wywolania')
        self.screen_wywolania.add_widget(wywolania_page)
        self.screen_manager.add_widget(self.screen_wywolania)

        self.screen_konsola = Screen(name='Konsola')
        self.screen_konsola.add_widget(konsola_page)
        self.screen_manager.add_widget(self.screen_konsola)



        self.thread_TCP = threading.Thread(target=self.TCP_IP)
        self.thread_TCP.start()

        #self.wyslij_dane_SQL()

        t = threading.Timer(czas_wysylania, self.wyslij_dane_SQL)
        t.start()

        if(zmieniaj_okna):
            Clock.schedule_interval(self.zmien_okno, czas_zmiana_okna)


        return self.screen_manager

    def zmien_okno(self, dt):
        global wywolania_page
        if self.screen_manager.current == 'Wywolania':
            self.screen_manager.current = 'Wtryskarka'
        elif self.screen_manager.current == 'Wtryskarka':
            wywolania_page.reconnectMQTT()
            wywolania_page.wyslij_MQTT()
            self.screen_manager.current = 'Wywolania'



    def on_stop(self, *args):
        global stop_application
        stop_application = True
        super().on_stop()
        print('on_stop')


def restart_program():
    global przycisk
    global wtrysk_s
    global wybrak_s
    global wsp_wys_s
    global konsola_page

    mqttClient.disconnect()
    dane = {'przycisk': przycisk,
            'wtrysk_s': str(wtrysk_s),
            'wybrak_s': str(wybrak_s),
            'wsp_wys_s': str(wsp_wys_s),
            'wc_magazyn': wywolania_page.wcisnieto_magazyn,
            'wc_nastawiacz': wywolania_page.wcisnieto_nastawiacz,
            'wc_jakosc': wywolania_page.wcisnieto_jakosc,
            'wc_brygadzista': wywolania_page.wcisnieto_brygadzista,
            'wc_narzedziowiec': wywolania_page.wcisnieto_narzedziowiec,
            'wc_utrzymanie': wywolania_page.wcisnieto_utrzymanie,
            'data_magazyn': wywolania_page.data_magazyn,
            'data_nastawiacz': wywolania_page.data_nastawiacz,
            'data_jakosc': wywolania_page.data_jakosc,
            'data_brygadzista': wywolania_page.data_brygadzista,
            'data_narzedziowiec': wywolania_page.data_narzedziowiec,
            'data_utrzymanie': wywolania_page.data_utrzymanie}

    output = open(os.path.join('data', 'data.pkl'), 'wb')

    # Pickle dictionary using protocol 0.
    pickle.dump(dane, output, -1)
    output.close()

    os.execv(sys.executable, ['python'] + sys.argv)



if __name__ == "__main__":
    res = threading.Timer(czas_reset, restart_program)
    res.start()
    Window.fullscreen = 0
    Window.size = (win_width, win_height)
    Window.clearcolor = utils.get_color_from_hex("#8c8c8c")

    Window.left = (screen_width - win_width)
    Window.top = 30

    app = App()
    app.run()

######################################################################################################################
'''
UTWORZENIE PLIKU EXE:
pip install kivy_deps.gstreamer
pyinstaller app.spec

PLIK app.spec:


# -*- mode: python ; coding: utf-8 -*-
from kivy_deps import sdl2, glew, gstreamer
block_cipher = None


a = Analysis(['app.py'],
             pathex=['C:\\Users\\marek\\PycharmProjects\\CykleAppLANtick'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
          name='app',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False , icon='data\\img\\icon.ico')


'''

#######################################################################################################################