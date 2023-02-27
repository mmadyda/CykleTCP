import os

cw = os.getcwd()

os.chdir(os.path.join(cw,'PoliCykle','cykle1'))
os.startfile('app1.exe')

os.chdir(os.path.join(cw,'PoliCykle','cykle2'))
os.startfile('app2.exe')

os.chdir(os.path.join(cw,'PoliCykle','cykle3'))
os.startfile('app3.exe')
