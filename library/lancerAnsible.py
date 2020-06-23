import subprocess as sp
import os

playbook = "helloworld.yml"
inventaire = "inventory.yml"
#result = sp.run(["ansible-playbook", playbook,"-i", inventaire ], capture_output= True, text = True)

result = sp.run(["ansible-playbook", playbook,"-i", inventaire ])
print(result.stdout)
var = os.environ["NEWVAR"]
print(var)
