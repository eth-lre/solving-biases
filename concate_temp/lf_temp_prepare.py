import csv
import re
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
wnl = WordNetLemmatizer()
from word2number import w2n


label_list = []
body_pairs = {}
question_pairs = {}

def to_lf_dict(lf):
    parts = [item.strip() for item in re.split("\(|\)|,", lf)]
    #print(parts)
    dict = {}
    dict["concept"] = parts[0]
    if parts[0] == "container":
        dict["label"] = parts[1]
        dict["quantity"] = parts[2]
        dict["entity"] = parts[3]
        dict["attribute"] = parts[4]
        dict["unit"] = parts[5]
    elif parts[0] == "transfer":
        dict["recipient_label"] = parts[1]
        dict["sender_label"] = parts[2]
        dict["quantity"] = parts[3]
        dict["entity"] = parts[4]
        dict["attribute"] = parts[5]
        dict["unit"] = parts[6]
    elif parts[0] == "add" or parts[0] == "times":
        dict["result_label"] = parts[1]
        dict["argument_label"] = parts[2]
        dict["quantity"] = parts[3]
        dict["result_entity"] = parts[4]
        dict["result_attribute"] = parts[5]
        dict["result_unit"] = parts[6]
        dict["argument_entity"] = parts[7]
        dict["argument_attribute"] = parts[8]
        dict["argument_unit"] = parts[9]
    elif parts[0] == "rate":
        dict["label"] = parts[1]
        dict["quantity"] = parts[2]
        dict["source_entity"] = parts[3]
        dict["source_attribute"] = parts[4]
        dict["source_unit"] = parts[5]
        dict["target_entity"] = parts[6]
        dict["target_attribute"] = parts[7]
        dict["target_unit"] = parts[8]
    elif parts[0] == "part":
        dict["whole_label"] = parts[1]
        dict["part_label"] = parts[2]
        dict["whole_entity"] = parts[3]
        dict["whole_attribute"] = parts[4]
        dict["whole_unit"] = parts[5]
        dict["part_entity"] = parts[6]
        dict["part_attribute"] = parts[7]
        dict["part_unit"] = parts[8]
    else:
        print("Out of the six concepts: "+ lf)
    return dict

def question_temp_analyze(lf, dict, sen):
    tokens_l = word_tokenize(sen.lower())
    tokens = word_tokenize(sen)
    if dict["concept"] == "container" and dict["attribute"] == "None" and dict["unit"] == "None":
        # label place holder
        # name
        label_index = []
        label_index.extend([i for i, x in enumerate(tokens_l) if x == dict["label"]])
        # personal pronoun
        label_index.extend([i for i, x in enumerate(tokens_l) if x == "she" or x == "he"])
        for index in label_index:
            tokens[index] = "[LABEL]"

        # entity place holder
        for i,x in enumerate(tokens_l):
            if wnl.lemmatize(x, "n") == wnl.lemmatize(dict["entity"], "n"):
                tokens[i] = "[ENTITY]s"

        if "[LABEL]" in tokens and "[ENTITY]s" in tokens:
            writer.writerow(["q-container", lf, " ".join(tokens), sen])


def isFloat(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

def quantity_replace(dict, tokens_l, tokens):
    if "/" in dict["quantity"]:
        quantity = float(dict["quantity"].split("/")[0]) / float(dict["quantity"].split("/")[1])
        dict["quantity"] = quantity
    for i, x in enumerate(tokens_l):
        if x.isdigit() or isFloat(x):
            if float(x) == float(dict["quantity"]):
                tokens[i] = "[NUM]"
        try:
            w2n.word_to_num(x)
            tokens[i] = "[NUM]"
        except:
            continue
    return tokens


def body_temp_analyze(lf, dict, sen):
    tokens_l = word_tokenize(sen.lower())
    tokens = word_tokenize(sen)
    if dict["concept"] == "container" and dict["attribute"]=="None" and dict["unit"]=="None":
        # label place holder
        # name
        label_index = []
        label_index.extend([i for i, x in enumerate(tokens_l) if x == dict["label"]])
        # personal pronoun
        label_index.extend([i for i, x in enumerate(tokens_l) if x == "she" or x == "he"])
        for index in label_index:
            tokens[index] = "[LABEL]"

        # quantity place holder
        tokens = quantity_replace(dict, tokens_l, tokens)

        # entity place holder
        for i,x in enumerate(tokens_l):
            if wnl.lemmatize(x, "n") == wnl.lemmatize(dict["entity"], "n"):
                tokens[i] = "[ENTITY]s"

        if "[LABEL]" in tokens and "[NUM]" in tokens and "[ENTITY]" in tokens:
                writer.writerow([dict["concept"], lf, " ".join(tokens), sen])

    if dict["concept"] == "transfer" and dict["attribute"]=="None" and dict["unit"]=="None":
        # label place holder
        r_index = []
        s_index = []
        if not dict["recipient_label"] == "None":
            r_index.extend([i for i, x in enumerate(tokens_l) if x == dict["recipient_label"]])
            if dict["sender_label"] == "None":
                r_index.extend([i for i, x in enumerate(tokens_l) if x == "she" or x == "he"])
        if not dict["sender_label"] == "None":
            s_index.extend([i for i, x in enumerate(tokens_l) if x == dict["sender_label"]])
            if dict["recipient_label"] == "None":
                s_index.extend([i for i, x in enumerate(tokens_l) if x == "she" or x == "he"])
        # if both not None, meaning of personal pronoun need manual check

        for index in r_index:
            tokens[index] = "[R_LABEL]"
        for index in s_index:
            tokens[index] = "[S_LABEL]"

        # entity place holder
        for i,x in enumerate(tokens_l):
            if wnl.lemmatize(x, "n") == wnl.lemmatize(dict["entity"], "n") or x == "them":
                tokens[i] = "[ENTITY]"

        # quantity place holder
        tokens = quantity_replace(dict, tokens_l, tokens)

        if ("[S_LABEL]" in tokens or "[R_LABEL]" in tokens) and "[NUM]" in tokens and "[ENTITY]" in tokens:
            writer.writerow([dict["concept"], lf, " ".join(tokens), sen])

    if (dict["concept"] == "add" or dict["concept"] == "times") and dict["result_attribute"] == "None" and dict["result_unit"] == "None" and dict["argument_attribute"] == "None" and dict["argument_unit"] == "None":
        # label place holder
        r_index = []
        a_index = []
        ra_index = []
        if dict["result_label"] == dict["argument_label"]:
            ra_index.extend([i for i, x in enumerate(tokens_l) if x == dict["result_label"]])
        else:
            r_index.extend([i for i, x in enumerate(tokens_l) if x == dict["result_label"]])
            a_index.extend([i for i, x in enumerate(tokens_l) if x == dict["argument_label"]])

        for index in r_index:
            tokens[index] = "[R_LABEL]"
        for index in a_index:
            tokens[index] = "[A_LABEL]"
        for index in ra_index:
            tokens[index] = "[RA_LABEL]"

        # entity place holder
        if dict["result_entity"] == dict["argument_entity"]:
            for i,x in enumerate(tokens_l):
                if wnl.lemmatize(x, "n") == wnl.lemmatize(dict["result_entity"], "n"):
                    tokens[i] = "[RA_ENTITY]"
        else:
            for i, x in enumerate(tokens_l):
                if wnl.lemmatize(x, "n") == wnl.lemmatize(dict["result_entity"], "n"):
                    tokens[i] = "[R_ENTITY]"
                if wnl.lemmatize(x, "n") == wnl.lemmatize(dict["argument_entity"], "n"):
                    tokens[i] = "[A_ENTITY]"

        # quantity place holder
        tokens = quantity_replace(dict, tokens_l, tokens)

        if ("[A_LABEL]" in tokens or "[R_LABEL]" in tokens or "[RA_LABEL]" in tokens) and "[NUM]" in tokens and ("[R_ENTITY]" in tokens or "[A_ENTITY]" in tokens or "[RA_ENTITY]" in tokens):
            writer.writerow([dict["concept"], lf, " ".join(tokens), sen])

    if dict["concept"] == "rate" and dict["source_attribute"] == "None" and dict["source_unit"] == "None" and dict["target_attribute"] == "None" and dict["target_unit"] == "None":
        print(dict, sen)
        label_index = []
        label_index.extend([i for i, x in enumerate(tokens_l) if x == dict["label"]])
        for index in label_index:
            tokens[index] = "[LABEL]"

        # quantity place holder
        tokens = quantity_replace(dict, tokens_l, tokens)

        # entity place holder
        for i, x in enumerate(tokens_l):
            if wnl.lemmatize(x, "n") == wnl.lemmatize(dict["source_entity"], "n"):
                tokens[i] = "[S_ENTITY]"
            if wnl.lemmatize(x, "n") == wnl.lemmatize(dict["target_entity"], "n"):
                tokens[i] = "[T_ENTITY]"

        if "[NUM]" in tokens and "[S_ENTITY]" in tokens and "[T_ENTITY]" in tokens:
                writer.writerow([dict["concept"], lf, " ".join(tokens), sen])
                #print(sen, tokens)








def template_prepare(lf, sen):
    concept_count = lf.count("(")
    # first deal with single concept per sentence
    if concept_count == 1:
        lf_dict = to_lf_dict(lf)
        if "quantity" in lf_dict.keys():
            if lf_dict["quantity"] == "None":
                question_temp_analyze(lf, lf_dict, sen)
            # else:
            #     body_temp_analyze(lf, lf_dict, sen)



of_dir = "temp_pair.csv"
of = open(of_dir, "a")
writer = csv.writer(of)


for dir in ["asdiv-train.csv", "asdiv-test.csv", "mawps-train.csv", "mawps-test.csv", "svamp-train.csv", "svamp-test.csv"]:
    inf = open(dir, "r")
    csvreader = csv.reader(inf)
    for row in csvreader:
        template_prepare(row[2], row[1])


