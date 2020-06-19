import threading as td
import time

path = r"/home/heliosys/examples.desktop"



class RessourceManager(td.Thread):
    def __init__(self, ressource):
        td.Thread.__init__(self)
        self.ressource = ressource

    def run(self):
        for line in self.ressource.readlines():
            time.sleep(1)
            print(line)
        self.ressource.close()


if __name__ == '__main__':
    try:
        file = open(path)
        ob = RessourceManager(file)
        ob.setDaemon(True)
        ob.start()
        while True: time.sleep(10)
    except:
        print("Dans Except")
        for t in td.enumerate() :
            if t != td.main_thread():
