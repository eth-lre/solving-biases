import csv
import re

entity_list = []

def extract_entity(lf):
    #print(lf)
    parts = [item.strip() for item in re.split("\(|\)|,", lf)]
    entity = []
    if parts[0] == "container":
        entity = [parts[3]]
    elif parts[0] == "transfer":
        entity = [parts[4]]
    elif parts[0] == "add" or parts[0] == "times":
        entity = [parts[4], parts[7]]
    elif parts[0] == "rate":
        print(parts[3], parts[6])
        entity = [parts[3], parts[6]]
    elif parts[0] == "part":
        entity = [parts[3], parts[6]]
    else:
        print("Out of the six concepts: "+ lf)
    for e in entity:
        if e not in entity_list and not e == "":
            entity_list.append(e)




for dir in ["asdiv-train.csv", "asdiv-test.csv", "mawps-train.csv", "mawps-test.csv", "svamp-train.csv", "svamp-test.csv"]:
    inf = open(dir, "r")
    csvreader = csv.reader(inf)
    for row in csvreader:
        for lf in [item.strip() for item in row[2].split(")")]:
            if not lf == "":
                extract_entity(lf)
print(len(entity_list))

of = open("data/entities_from_datasets.csv", "w")
writer = csv.writer(of)
for e in entity_list:
    writer.writerow([e])

