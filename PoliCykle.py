import os
import time

cw = os.getcwd()

folder = 'PoliCykle'

#os.chdir(os.path.join(cw,'PoliCykle','cykle1'))
#os.startfile('app1.exe')

#os.chdir(os.path.join(cw,'PoliCykle','cykle2'))
#os.startfile('app2.exe')

#os.chdir(os.path.join(cw,'PoliCykle','cykle3'))
#os.startfile('app3.exe')
os.startfile(os.path.join(folder,'cykle1','app1.exe'))
time.sleep(5)
os.startfile(os.path.join(folder,'cykle2','app2.exe'))
time.sleep(5)
os.startfile(os.path.join(folder,'cykle3','app3.exe'))
