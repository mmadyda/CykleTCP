import os
import subprocess

from time import sleep

dirname, filename = os.path.split(os.path.abspath(__file__))

subprocess.call([os.path.join(dirname,'PoliCykle','cykle1', 'app1.exe'), 'arg'],cwd=os.path.join(dirname,'PoliCykle','cykle1'))
subprocess.call([os.path.join(dirname,'PoliCykle','cykle2', 'app2.exe'), 'arg'],cwd=os.path.join(dirname,'PoliCykle','cykle2'))


#os.startfile(os.path.join(dirname,'PoliCykle','cykle3', 'app3.exe'))

