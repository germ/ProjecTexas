#A linear script to piece the bits of data together

import json
import copy
import random
import string
import pickle

#Read in the JSON data
f = open("items.json", "r")

line = ""
while 1:
    i = f.readline()
    if not i:
        break
    else:
        line = line + i
f.close()

coder   = json.JSONDecoder()
data    = coder.decode(line)
clean   = {}

#Ugly hack to collect info into one dict
#TODO: Clean this up

#Loop over entire array, making sure that the identifiers are not nulled, the
#objects are not the same and the objects are in the correct order
for o in data:
    for i in data:
        if (o['ident'] == i['ident']) and ('name' in o) and (o['ident'] != "") \
            and (i['ident'] != "") and (i != o):
            
            #Merge into i
            o['finalStatement'] = i['finalStatement']       

            """Ugly hack that strips the URL down to the page name by reversing
            the string, finding the closest '/' and storing from the negative
            index of the slash to the end"""
            #TODO: Clean this ugly mess of a hack
            o['ident'] = o['ident'][-string.find(o['ident'][::-1], "/"):]
            clean[o['ident']] = copy.deepcopy(o)

            #Equivelent of Nulling 
            i['ident'] = ""
            o['ident'] = ""

#dump using pickle
#TODO: Use a decent database
dump = open("clean.pickle", "w")
pickle.dump(clean, dump)
dump.close()
