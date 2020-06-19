import threading as td
import time
import _thread

path = r"/home/heliosys/Documents/csvtest.csv"
path2 = r"/home/heliosys/examples.desktop"

class RessourceManager(td.Thread):
    def __init__(self, ressource):
        td.Thread.__init__(self)
        self.ressource = ressource
        self.setDaemon(True)
        self.event = td.Event()
        #self.event = event

    def run(self):

        while True:
            time.sleep(0.1)
        pass
                #self.event.set()

if __name__ == '__main__':
    try:
        ob2 = RessourceManager(path2)
        ob2.start()
        ob2.start()

        file = open(path2, 'r')
        for line in file:
            time.sleep(1)
            print(line)
        file.close()
        td.excepthook(exc_type = SystemExit)

    except KeyboardInterrupt:
        print("arret du processus...")
        liste = td.enumerate()
        for t in liste:
            if t != td.main_thread() and t.is_alive():
                print(t.getName())
                if t.event:
                    time.sleep(2)
                    t.event.clear()

        #if ob.is_alive():

        #event.wait()
        #mainproc = td.Thread(td.main_thread())
        print("Processus termine")

    except _thread.error:
        print("Thread Error")