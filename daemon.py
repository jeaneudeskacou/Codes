"""ce module lit la table de routage et ecrit les données dans des fichiers
comme ceci.
{1587496787.5253153:
 {'ligne 1': {'DESTINATION': '0.0.0.0', 'PASSERELLE': '192.168.117.2', 'GENMASK': '0.0.0.0', 'INDIC': 'UG', 'METRIC': '100', 'REF': '0', 'USE': '0', 'IFACE': 'ens33'},
  'ligne 2': {'DESTINATION': '169.254.0.0', 'PASSERELLE': '0.0.0.0', 'GENMASK': '255.255.0.0', 'INDIC': 'U', 'METRIC': '1000', 'REF': '0', 'USE': '0', 'IFACE': 'ens33'},
  'ligne 3': {'DESTINATION': '192.168.117.0', 'PASSERELLE': '0.0.0.0', 'GENMASK': '255.255.255.0', 'INDIC': 'U', 'METRIC': '100', 'REF': '0', 'USE': '0', 'IFACE': 'ens33'}
  }
}
dans sa presente version, le module produit 2 fichiers, un fichier binaire contenant la donnée sous forme d'objet (donc facilement exploitable par l'ordinateur mais
illisible pour l'homme)
un fichier .txt destiné à etre lu par l'homme.
"""
#!/usr/bin/python3
import os
import time
import pickle
import struct
import json
import subprocess

OUTPUT_DIR_NAME = "Experiment_outputs"
OUTPUT_DIR_PATH = os.path.join(os.getenv("HOME"), OUTPUT_DIR_NAME)
META_FILE = os.path.join(OUTPUT_DIR_PATH, "meta.txt")
TABLE = os.path.join(OUTPUT_DIR_PATH, "table.tmp")
LAST_TABLE = os.path.join(OUTPUT_DIR_PATH, "lastTable.binary")

def initialization():
    """Fonction pour creer le dossier où seront stockées les sorties
    ainsi qu'un fichier servant a retrouver le nombre d'experiences réalisée
    Leur donner les droits necessaire etc. Si le dossier existe deja, on lit juste le
    fichier meta.txt et on renvoi la valeur lu"""
    if os.path.exists(OUTPUT_DIR_PATH) :
        if os.path.exists(META_FILE):
            with open(META_FILE, "rb") as meta_file:
                number = struct.unpack("i", meta_file.read(4))
                for i in number:
                    result = i+1
                    break
            with open(META_FILE, "wb") as meta_file:
                meta_file.write(struct.pack("i", result))
            return result
        else:
            open(META_FILE,'x')
            with open(META_FILE, "wb") as meta_file:
                meta_file.write(struct.pack("i", 0))
            return 1
    else:
        os.mkdir(OUTPUT_DIR_PATH)
        with open(META_FILE, "wb") as meta_file:
           meta_file.write(struct.pack("i", 0))
        return 1


def new_Experiment():
    """Fonction pour creer les fichiers necessaires pour une nouvelle experience
    notamment le fichier de sorties. Elle reinitialise aussi le fichier intermediaire
    comme le TABLE"""

    xp_number = initialization()
    OUTPUT = os.path.join(OUTPUT_DIR_PATH, "experiment_" + str(xp_number)+".txt" )
    BINARY = os.path.join(OUTPUT_DIR_PATH, "experiment_" + str(xp_number)+".binary")
    NS_FILE = os.path.join(OUTPUT_DIR_PATH, "nsFile_" + str(xp_number)+".txt")
    open(LAST_TABLE, 'w')
    return OUTPUT, BINARY, NS_FILE


def getTable():
    result = subprocess.run(["route", "-n"],capture_output = True, text= True)
    result = result.stdout
    #print(result)
    return result


def parseTableData(table):
    result = {}
    result["DESTINATION"] = table[0]
    result["PASSERELLE"] = table[1]
    result["GENMASK"] = table[2]
    result["INDIC"] = table[3]
    result["METRIC"] = table[4]
    result["REF"] = table[5]
    result["USE"] = table[6]
    result["IFACE"] = table[7]
    return result


def getTabledata(src=getTable()):
    data = {}
    text = src.split("\n")
    for line in range(len(text) - 3):
        lg = text[line + 2].split(' ')
        cle = "ligne " + str(line+1)
        data[cle] = parseTableData(tablerefactor(lg))
    return data


def isTableExist(newTable):
    #dstSize = os.path.getsize(dst)
    with open(LAST_TABLE, "rb") as file:
        reader = pickle.Unpickler(file)
        data = reader.load()
        data = data.values()
        return data==newTale


def getPositions(gps_socket, data_stream):
    info  = {}
    for new_data in gps_socket:
        if new_data:
            data_stream.unpack(new_data)
            try:
                long = float(data_stream.TPV['lon'])
                lat = float(data_stream.TPV['lat'])
                speed = float(data_stream.TPV['speed'])
                info = {'long':long,'lat':lat,'speed':speed}
                return info, getSecondes(data_stream.TPV['time'][11:19])
            except:
                return None


def getLastInput(dst=LAST_TABLE):
    dstSize = os.path.getsize(dst)
    with open(dst, "rb") as file:
        if dstSize == 0:
            return None
        else:
            reader = pickle.Unpickler(file)
            return reader.load()


def getUpdate():
    newRoutingTable = getTabledata()
    lastInput = getLastInput()
    with open(LAST_TABLE, "wb") as file:
        writer = pickle.Pickler(file)
        writer.dump(newRoutingTable)
    if newRoutingTable == lastInput:
        return {time.time(): [{}, "position"]}
    return {time.time(): [newRoutingTable, "position"]}


def setSimulationData(file, data, node_number=0):
    with open(file, 'w') as scr:
        strInit = "$node_({id}) set {name}_ {position}\n"
        strMove = "$ns_ at {time} \"$node_({id}) setdest {position_X} {position_Y} {speed}\"\n"
        keys = list(data.keys())
        keys.sort()
        X = data[keys[0]][1]['long']
        Y = data[keys[0]][1]['lat']
        FINAL_STR = strInit.format(id=node_number, name='X', position=X)
        FINAL_STR += strInit.format(id=node_number, name='Y', position=Y)
        for i in range(1, len(keys)):
            X = data[keys[i]][1]['long']
            Y = data[keys[i]][1]['lat']
            avrageSpeed = (((X-data[keys[i-1]][1]['long'])**2 +(Y-data[keys[i-1]][1]['lat'])**2)**(0.5))/(keys[i]-keys[i-1])
            FINAL_STR += strMove.format(time=(keys[i]-keys[0]), id=node_number, position_X = X, position_Y = Y, speed = avrageSpeed)
        scr.write(FINAL_STR)
        print(keys)

def writeDataOnFile(binary, output, dico):
    with open(binary, "wb") as bin:
        writer = pickle.Pickler(bin)
        writer.dump(dico)
    with open(output, 'w') as txt:
        txt.write(str(dico))

def getSecondes(time):
    timeTbale = time.split(':')
    seconde = int(timeTbale[0])*3600
    seconde += int(timeTbale[1])*60
    seconde += int(timeTbale[2])
    return seconde

def tablerefactor(table):
    elmt = 0
    while elmt < len(table) - 1:
        if table[elmt] in " ":
            table.pop(elmt)
        else:
            table[elmt].strip()
            elmt += 1
    return table

def main(nombreExc):
    xp = new_Experiment()
    OUTPUT = xp[0]
    BINARY = xp[1]
    NS_FILE = xp[2]

    dico = {}
    i = 0
    while (True):
        if i==nombreExc :
            break
        i+=1
        print("============================= Nouvelle Interation =================================")
        dico.update(getUpdate())
        print(dico)
        time.sleep(3)
    writeDataOnFile(BINARY, OUTPUT, dico)
    setSimulationData(NS_FILE, dico)
    #setSimulationData()

#main(10)
print(getTable())
print(getTabledata())