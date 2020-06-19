import csv
path = "/home/heliosys/Documents/csvtest.csv"

def getData(path, *keys):
    path = open(path, 'r', newline='')
    read = csv.DictReader(path, restval='')
    result = []
    if keys:
        keys = list(set(keys))
        read.fieldnames = [x.strip() for x in read.fieldnames]
        popData(keys, read.fieldnames)
        for row in read:
            dic = {}
            for key in keys:
                dic[key] = row[key]
            result.append(dic)
    else:
        for row in read:
            result.append(row)
    return result, read.fieldnames

def popData(keys, read):
    i = 0
    while i < len(keys) :
            key = keys[i]
            if key in read:
                i += 1
            else:
                print("Attention la clé {} n'existe pas".format(key))
                keys.pop(i)
    return keys

def insensitiveCompare(dic, metafields):
    """Compare sans tenir compte de la case, 2 listes de string.
    retourne un dictionnaire forme des couples (dic[i]:metafields[i]) et True pour indiquer que les listes sont
    les memes sans parler de la case"""

    match = {}
    unmatch = []
    for i in dic:
        find = False
        for j in metafields:
            if i.upper() == j.upper():
                find = True
                match[i] = j
        if not find:
            unmatch.append(i)
    return match, len(unmatch)==0

def changeDicCase(dic, modelKey):
    """ Remplace les clés de dic par celles correspondantes dans modelKey
    exemple: dic = {'nom':'LeBon', 'prenom':'JeanEudes'} et modelKey = ['Nom', 'PreNom'] alors
    le resultat sera dic = {'Nom':'LeBon', 'PreNom':'JeanEudes'}"""

    match, find = insensitiveCompare(list(dic.keys()), modelKey)
    for key in list(dic.keys()):
        if key in match.keys() :
            if key in match.values():
                continue
            else:
                dic[match[key]] = dic[key]
                del dic[key]
        else:
            del dic[key]
    return dic

def extractDicCaseInsensitive(dic, modelKey):
    pass

def findPrimaryKey(liste, number=1 ):
    """Trouve dans une liste de dic un ensemble de clé ayant une valeur unique pour chaque dic"""
    result = []
    listKey = liste[0].keys()
    dico = {}
    for key in listKey:
        dico[key] = len(set([dic[key] for dic in liste]))
    primaryKey = [key for key in dico.keys() if dico[key] == len(liste)]
    return primaryKey

def listTdDic(liste, primaryKey):
    """Converti une liste de dic en un dictionnaire ayant pour clées la valeur de primaryKey
    qui est censé etre unique pour chaque dic"""
    result = {}
    for dic in liste:
        result[dic[primaryKey]] = dic
        del result[dic[primaryKey]][primaryKey]
    return result

def affichebien(liste):
    for dic in liste:
        txt = "{nom:50} ==> {prenom}"
        txt = txt.format(nom = dic["nom"], prenom = dic["prenom"])
        print(txt)

keys = ["Nom","Prenom", "Age","NokKey"]

dic, read = getData(path)
print(dic)