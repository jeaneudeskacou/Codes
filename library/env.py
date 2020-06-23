#!/usr/bin/python3

import sys
import os
register = ""

if (len(sys.argv) > 1):
	print("Ansible a passe des arguments")
else:
	print("Le programme vient d'etre lancé")
	try:
		arg0 = sys.argv[0]
		arg1 = sys.argv[1]
	except:


		#f = open(path, 'w')
		f = open("/home/heliosys/result.txt", 'w')
		f.write("Ceci est arg0: {}, et ceci est arg1: {}".format(arg0, arg1))
