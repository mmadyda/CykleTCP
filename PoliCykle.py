import configparser
import os
import sys
import time

cwd = os.getcwd()
if getattr(sys, 'frozen', False):
    cwd = os.path.dirname(sys.executable)
elif __file__:
    cwd = os.path.dirname(__file__)

config = configparser.ConfigParser()
if os.path.exists(os.path.join(cwd, 'data', 'poli.ini')):
    config.read(os.path.join(cwd, 'data', 'poli.ini'))


    liczba_maszyn = int(config['DEFAULT']['liczba_maszyn'])  # liczba obslugiwanych maszyn
    folder_programu = str(config['DEFAULT']['folder_programu'])
    nazwa_programu = str(config['DEFAULT']['nazwa_programu'])
else:
    liczba_maszyn = 1
    folder_programu = 'cykle'
    nazwa_programu = 'app'




for i in range(1,liczba_maszyn+1):
    path = os.path.join('cykle'+str(i), 'app'+str(i)+'.exe')
    print(path)
    os.startfile(path)

