import json

def gen_ent_unit_json():
    out = {}
    with open('entities.csv') as f:
            entities = [e.replace('\n', '') for e in f.readlines()]
    for ent in entities:
          out[ent] = 'None'
    out_j = json.dumps(out)
    with open("ent_unit_names.json", "w") as outfile:
        outfile.write(out_j)

if __name__ == "__main__":
      gen_ent_unit_json()
    

