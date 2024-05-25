import csv
import re
import random
from nltk.stem import WordNetLemmatizer
wnl = WordNetLemmatizer()

random.seed(17)

TEMP_DIR = "data/temp_pair_v2.csv"
WM_DIR = "data/instantiated_world_models.txt"

def load_temp_dict(dir):
    temp_dict = {}
    inf = open(dir, "r")
    csvreader = csv.reader(inf)
    for row in csvreader:
        concept = row[0]
        lf = row[1]
        temp = row[2]
        if concept not in temp_dict.keys():
            temp_dict[concept] = {}
        if lf not in temp_dict[concept].keys():
            temp_dict[concept][lf] = [temp]
        else:
            temp_dict[concept][lf].append(temp)
    return temp_dict

def load_world_model(dir):
    inf = open(dir, "r")
    return inf.readlines()

def get_subject_from_q(lf):
    parts = [item.strip() for item in re.split("\(|\)|,", lf)]
    return parts[1]

def get_subject_from_lf(lf):
    parts = [item.strip() for item in re.split("\(|\)|,", lf)]
    return parts[1]

def process_lf(lf, type, track_q = False):
    parts = [item.strip() for item in re.split("\(|\)|,", lf)]
    #print(parts)
    concept = parts[0]
    fill_dict = {}
    transed_ents_lf = []
    if type == "body":
        #todo: add attribute templating for part
        if parts[0] == "container":
            fill_dict["label"] = parts[1]
            fill_dict["quantity"] = parts[2]
            fill_dict["entity"] = parts[3]
            fill_dict["attribute"] = parts[4]
            fill_dict["unit"] = parts[5]
            parts[1] = "[LABEL]"
            parts[2] = "[NUM]" if parts[2] != "None" else parts[2]
            parts[3] = "[ENTITY]"
            parts[4] = "[ATTRIBUTE]" if parts[4] != "None" else parts[4]
            parts[5] = "[UNIT]" if parts[5] != "None" else parts[5]
            # current attribute and unit are "None", no replacement to them
        elif parts[0] == "transfer":
            fill_dict["recipient_label"] = parts[1]
            fill_dict["sender_label"] = parts[2]
            fill_dict["quantity"] = parts[3]
            fill_dict["entity"] = parts[4]
            fill_dict["attribute"] = parts[5]
            fill_dict["unit"] = parts[6]
            if parts[1] != 'None' and parts[5] != 'None' and not track_q: transed_ents_lf.append((parts[1], parts[5], parts[4]))
            elif parts[1] != 'None' and not track_q: transed_ents_lf.append((parts[1], parts[4]))
            if parts[2] != 'None' and parts[5] != 'None' and not track_q: transed_ents_lf.append((parts[2], parts[5], parts[4]))
            elif parts[2] != 'None' and not track_q: transed_ents_lf.append((parts[2], parts[4]))
            if not parts[1] == "None":
                parts[1] = "[R_LABEL]"
            if not parts[2] == "None":
                parts[2] = "[S_LABEL]"
            parts[3] = "[NUM]"
            parts[4] = "[ENTITY]"
            parts[5] = "[ATTRIBUTE]" if parts[5] != "None" else parts[5]
            parts[6] = "[UNIT]" if parts[6] != "None" else parts[6]
        elif parts[0] == "add" or parts[0] == "times":
            fill_dict["result_label"] = parts[1]
            fill_dict["argument_label"] = parts[2]
            fill_dict["quantity"] = parts[3]
            fill_dict["result_entity"] = parts[4]
            fill_dict["result_attribute"] = parts[5]
            fill_dict["result_unit"] = parts[6]
            fill_dict["argument_entity"] = parts[7]
            fill_dict["argument_attribute"] = parts[8]
            fill_dict["argument_unit"] = parts[9]
            parts[1] = "[R_LABEL]"
            parts[2] = "[A_LABEL]"
            parts[3] = "[NUM]"
            parts[4] = "[R_ENTITY]"
            parts[5] = "[R_ATTRIBUTE]" if parts[5] != "None" else parts[5]
            parts[6] = "[R_UNIT]" if parts[6] != "None" else parts[6]
            parts[7] = "[A_ENTITY]"
            parts[8] = "[A_ATTRIBUTE]" if parts[8] != "None" else parts[8]
            parts[9] = "[A_UNIT]" if parts[9] != "None" else parts[9]
        elif parts[0] == "rate":
            fill_dict["label"] = parts[1]
            fill_dict["quantity"] = parts[2]
            fill_dict["source_entity"] = parts[3]
            fill_dict["source_attribute"] = parts[4]
            fill_dict["source_unit"] = parts[5]
            fill_dict["target_entity"] = parts[6]
            fill_dict["target_attribute"] = parts[7]
            fill_dict["target_unit"] = parts[8]
            parts[1] = "[LABEL]"
            parts[2] = "[NUM]"
            parts[3] = "[S_ENTITY]"
            parts[4] = "[S_ATTRIBUTE]" if parts[4] != "None" else parts[4]
            parts[7] = "[T_ATTRIBUTE]" if parts[7] != "None" else parts[7]
            parts[6] = "[T_ENTITY]"
            parts[5] = "[S_UNIT]" if parts[5] != "None" else parts[5]
            parts[8] = "[T_UNIT]" if parts[8] != "None" else parts[8]
        elif parts[0] == "part":
            fill_dict["whole_label"] = parts[1]
            fill_dict["part_label"] = parts[2]
            fill_dict["whole_entity"] = parts[3]
            fill_dict["whole_attribute"] = parts[4]
            fill_dict["whole_unit"] = parts[5]
            fill_dict["part_entity"] = parts[6]
            fill_dict["part_attribute"] = parts[7]
            fill_dict["part_unit"] = parts[8]
            parts[1] = "[W_LABEL]"
            parts[2] = "[P_LABEL]"
            parts[3] = "[W_ENTITY]"
            parts[5] = "[W_UNIT]" if parts[5] != "None" else parts[5]
            parts[8] = "[P_UNIT]" if parts[8] != "None" else parts[8]
            parts[6] = "[P_ENTITY]"
        else:
            print("Out of the six concepts: "+ lf)
    else:
        if parts[0] == "container":
            if parts[1] != 'None' and parts[4] != 'None' and track_q: transed_ents_lf.append((parts[1], parts[4], parts[3]))
            elif parts[1] != 'None' and track_q: transed_ents_lf.append((parts[1], parts[3]))
            fill_dict["label"] = parts[1]
            fill_dict["entity"] = parts[3]
            fill_dict["attribute"] = parts[4]
            fill_dict["unit"] = parts[5]
            parts[1] = "[LABEL]"
            parts[3] = "[ENTITY]"
            parts[4] = "[ATTRIBUTE]" if parts[4] != "None" else parts[4]
            parts[5] = "[UNIT]" if parts[5] != "None" else parts[5]
        elif parts[0] == "add" or parts[0] == "times":
            fill_dict["result_label"] = parts[1]
            fill_dict["argument_label"] = parts[2]
            fill_dict["result_entity"] = parts[4]
            fill_dict["result_attribute"] = parts[5]
            fill_dict["result_unit"] = parts[6]
            fill_dict["argument_entity"] = parts[7]
            fill_dict["argument_attribute"] = parts[8]
            fill_dict["argument_unit"] = parts[9]
            parts[1] = "[R_LABEL]"
            parts[2] = "[A_LABEL]"
            parts[4] = "[R_ENTITY]"
            parts[5] = "[R_ATTRIBUTE]" if parts[5] != "None" else parts[5]
            parts[6] = "[R_UNIT]" if parts[6] != "None" else parts[6]
            parts[7] = "[A_ENTITY]"
            parts[8] = "[A_ATTRIBUTE]" if parts[8] != "None" else parts[8]
            parts[9] = "[A_UNIT]" if parts[9] != "None" else parts[9]
        elif parts[0] == "rate":
            fill_dict["label"] = parts[1]
            fill_dict["source_entity"] = parts[3]
            fill_dict["source_attribute"] = parts[4]
            fill_dict["source_unit"] = parts[5]
            fill_dict["target_entity"] = parts[6]
            fill_dict["target_attribute"] = parts[7]
            fill_dict["target_unit"] = parts[8]
            parts[1] = "[LABEL]"
            parts[3] = "[S_ENTITY]"
            parts[4] = "[S_ATTRIBUTE]" if parts[4] != "None" else parts[4]
            parts[6] = "[T_ENTITY]"
            parts[7] = "[T_ATTRIBUTE]" if parts[7] != "None" else parts[7]
            parts[5] = "[S_UNIT]" if parts[5] != "None" else parts[5]
            parts[8] = "[T_UNIT]" if parts[8] != "None" else parts[8]

    lf_temp = parts[0] + " ( " + parts[1]
    for i in range(2, len(parts)-1):
        lf_temp = lf_temp + " , " + parts[i]
    lf_temp = lf_temp + parts[-1] + " )"
    return concept, fill_dict, lf_temp, transed_ents_lf


def fill_template(concept, fill_dict, temp):
    #todo: add attribute filling for part and q-rate
    temp_filled = ""
    if concept == "container":
        temp_filled = temp.replace("[LABEL]", fill_dict["label"])
        temp_filled = temp_filled.replace("[NUM]", fill_dict["quantity"])
        temp_filled = temp_filled.replace("[ENTITY]", wnl.lemmatize(fill_dict["entity"], "n"))
        if not fill_dict["attribute"] == "None":
            temp_filled = temp_filled.replace("[ATTRIBUTE]", fill_dict["attribute"])
        if not fill_dict["unit"] == "None":
            temp_filled = temp_filled.replace("[UNIT]", fill_dict["unit"])
    elif concept == "transfer":
        if not fill_dict["recipient_label"] == "None":
            temp_filled = temp.replace("[R_LABEL]", fill_dict["recipient_label"])
        else:
            temp_filled = temp
        if not fill_dict["sender_label"] == "None":
            temp_filled = temp_filled.replace("[S_LABEL]", fill_dict["sender_label"])
        temp_filled = temp_filled.replace("[NUM]", fill_dict["quantity"])
        temp_filled = temp_filled.replace("[ENTITY]", wnl.lemmatize(fill_dict["entity"], "n"))
        if not fill_dict["attribute"] == "None":
            temp_filled = temp_filled.replace("[ATTRIBUTE]", fill_dict["attribute"])
        if not fill_dict["unit"] == "None":
            temp_filled = temp_filled.replace("[UNIT]", fill_dict["unit"])
    elif concept == "add" or concept == "times":
        temp_filled = temp.replace("[R_LABEL]", fill_dict["result_label"])
        temp_filled = temp_filled.replace("[A_LABEL]", fill_dict["argument_label"])
        temp_filled = temp_filled.replace("[NUM]", fill_dict["quantity"])
        if not fill_dict["result_attribute"] == "None":
            temp_filled = temp_filled.replace("[R_ATTRIBUTE]", fill_dict["result_attribute"])
        if not fill_dict["argument_attribute"] == "None":
            temp_filled = temp_filled.replace("[A_ATTRIBUTE]", fill_dict["argument_attribute"])
        if not fill_dict["result_unit"] == "None":
            temp_filled = temp_filled.replace("[R_UNIT]", fill_dict["result_unit"])
        if not fill_dict["argument_unit"] == "None":
            temp_filled = temp_filled.replace("[A_UNIT]", fill_dict["argument_unit"])
        temp_filled = temp_filled.replace("[R_ENTITY]", wnl.lemmatize(fill_dict["result_entity"], "n"))
        temp_filled = temp_filled.replace("[A_ENTITY]", wnl.lemmatize(fill_dict["argument_entity"], "n"))
    elif concept == "rate":
        if not fill_dict["label"] == "None":
            temp_filled = temp.replace("[LABEL]", fill_dict["label"])
        else:
            temp_filled = temp
        temp_filled = temp_filled.replace("[NUM]", fill_dict["quantity"])
        temp_filled = temp_filled.replace("[S_ENTITY]", wnl.lemmatize(fill_dict["source_entity"], "n"))
        temp_filled = temp_filled.replace("[T_ENTITY]", wnl.lemmatize(fill_dict["target_entity"], "n"))
        if not fill_dict["source_attribute"] == "None":
                temp_filled = temp_filled.replace("[S_ATTRIBUTE]", fill_dict["source_attribute"])
        if not fill_dict["target_attribute"] == "None":
                temp_filled = temp_filled.replace("[T_ATTRIBUTE]", fill_dict["target_attribute"])
        if not fill_dict["source_unit"] == "None":
                temp_filled = temp_filled.replace("[S_UNIT]", fill_dict["source_unit"])
        if not fill_dict["target_unit"] == "None":
                temp_filled = temp_filled.replace("[T_UNIT]", fill_dict["target_unit"])
    elif concept == "part":
        temp_filled = temp.replace("[W_LABEL]", fill_dict["whole_label"])
        temp_filled = temp_filled.replace("[W_ENTITY]", fill_dict["whole_entity"])
        if not fill_dict["whole_unit"] == "None":
                temp_filled = temp_filled.replace("[W_UNIT]", fill_dict["whole_unit"])
    elif concept == "q-container":
        temp_filled = temp.replace("[LABEL]", fill_dict["label"])
        temp_filled = temp_filled.replace("[ENTITY]", wnl.lemmatize(fill_dict["entity"], "n"))
        if not fill_dict["attribute"] == "None":
            temp_filled = temp_filled.replace("[ATTRIBUTE]", fill_dict["attribute"])
        if not fill_dict["unit"] == "None":
            temp_filled = temp_filled.replace("[UNIT]", fill_dict["unit"])
    elif concept == "q-add":
        temp_filled = temp.replace("[R_LABEL]", fill_dict["result_label"])
        temp_filled = temp_filled.replace("[A_LABEL]", fill_dict["argument_label"])
        if not fill_dict["result_attribute"] == "None":
            temp_filled = temp_filled.replace("[R_ATTRIBUTE]", fill_dict["result_attribute"])
        if not fill_dict["argument_attribute"] == "None":
            temp_filled = temp_filled.replace("[A_ATTRIBUTE]", fill_dict["argument_attribute"])
        if not fill_dict["result_unit"] == "None":
            temp_filled = temp_filled.replace("[R_UNIT]", fill_dict["result_unit"])
        if not fill_dict["argument_unit"] == "None":
            temp_filled = temp_filled.replace("[A_UNIT]", fill_dict["argument_unit"])
        temp_filled = temp_filled.replace("[R_ENTITY]", wnl.lemmatize(fill_dict["result_entity"], "n"))
        temp_filled = temp_filled.replace("[A_ENTITY]", wnl.lemmatize(fill_dict["argument_entity"], "n"))
    elif concept == "q-rate":
        temp_filled = temp.replace("[LABEL]", fill_dict["label"])
        temp_filled = temp_filled.replace("[S_ENTITY]", wnl.lemmatize(fill_dict["source_entity"], "n"))
        temp_filled = temp_filled.replace("[T_ENTITY]", wnl.lemmatize(fill_dict["target_entity"], "n"))
        if not fill_dict["source_unit"] == "None":
                temp_filled = temp_filled.replace("[S_UNIT]", fill_dict["source_unit"])
        if not fill_dict["target_unit"] == "None":
                temp_filled = temp_filled.replace("[T_UNIT]", fill_dict["target_unit"])

    return temp_filled


def generate_nl_description(wm, temp_dict, type, transed_ents_body=None, consistency_question=None, dual=False, pair_cons=False):
    consistency_q_lf = None
    if consistency_question is not None:
       consistency_q_lf = consistency_question
    lfs = [item.strip() for item in wm.split(";")][:-1]
    parts = []
    nl = []
    transed_ents = []
    consistent_nl = []
    inconsistent_nl = []
    cons_idx = 0
    final_cons_idx = 0
    start_lf = lfs[0]
    prev_subject = None
    for lf in lfs:
        # append nl description only for the first part-lf
        if type == "body":
            concept, fill_dict, lf_temp, transed_ents_lf = process_lf(lf, type, track_q=False)
            if not concept == "part" or (
                    concept == "part" and not fill_dict["whole_label"] + fill_dict["whole_entity"] in parts):
                if consistency_q_lf is None and not dual: 
                    temp = random.sample(temp_dict[concept][lf_temp], 1)[0]
                    temp_filled = fill_template(concept, fill_dict, temp)
                    nl.append(temp_filled)
                #dealing with consistency with question type generation
                #if we are generating consistency against question, sample from specific templates cons-add/cons-sub etc.
                elif consistency_q_lf is not None and not dual and concept!="add" and concept!="times":
                    temp = random.sample(temp_dict[concept][lf_temp], 1)[0]
                    temp_filled = fill_template(concept, fill_dict, temp)
                    consistent_nl.append(temp_filled)
                    inconsistent_nl.append(temp_filled)
                elif consistency_q_lf is not None and not dual and concept=="add" or concept=="times":
                    final_cons_idx = cons_idx
                    subject = get_subject_from_q(consistency_q_lf)
                    if fill_dict["result_label"] == subject:
                        if concept=="add": 
                            consistent_temp = random.sample(temp_dict["cons-add"][lf_temp], 1)[0]
                            inconsistent_temp = random.sample(temp_dict["cons-sub"][lf_temp], 1)[0] 
                        elif concept=="times": 
                            consistent_temp = random.sample(temp_dict["cons-times"][lf_temp], 1)[0]
                            inconsistent_temp = random.sample(temp_dict["cons-div"][lf_temp], 1)[0]
                        consistent_temp_filled = fill_template(concept, fill_dict, consistent_temp)
                        consistent_nl.append(consistent_temp_filled)
                        inconsistent_temp_filled = fill_template(concept, fill_dict, inconsistent_temp)
                        inconsistent_nl.append(inconsistent_temp_filled)
                    elif fill_dict["result_label"] != subject:
                        if concept=="add": 
                            consistent_temp = random.sample(temp_dict["cons-sub"][lf_temp], 1)[0]
                            inconsistent_temp = random.sample(temp_dict["cons-add"][lf_temp], 1)[0] 
                        elif concept=="times": 
                            consistent_temp = random.sample(temp_dict["cons-div"][lf_temp], 1)[0]
                            inconsistent_temp = random.sample(temp_dict["cons-times"][lf_temp], 1)[0]
                        consistent_temp_filled = fill_template(concept, fill_dict, consistent_temp)
                        consistent_nl.append(consistent_temp_filled)
                        inconsistent_temp_filled = fill_template(concept, fill_dict, inconsistent_temp)
                        inconsistent_nl.append(inconsistent_temp_filled)
                #dealing with dual generation 
                #if we want to enforce pairwise consistency
                elif dual and pair_cons and concept == "add":
                    if prev_subject is None: prev_subject = get_subject_from_lf(start_lf)
                    if fill_dict['result_label'] == prev_subject:
                        #situation where the newly introduced agent has less of something
                        consistent_temp = random.sample(temp_dict["cons-sub"][lf_temp], 1)[0]
                        consistent_temp_filled = fill_template(concept, fill_dict, consistent_temp)
                        consistent_nl.append(consistent_temp_filled)
                        #for the dual situation, we don't need the inconsistent question so just fill it with None (so we don't need separate functions)
                        inconsistent_temp_filled = None
                        inconsistent_nl.append(inconsistent_temp_filled)
                        prev_subject = fill_dict['argument_label']
                    elif fill_dict['result_label'] != prev_subject:
                        #situation where newly introduced agent has more of something
                        consistent_temp = random.sample(temp_dict["cons-add"][lf_temp], 1)[0]
                        consistent_temp_filled = fill_template(concept, fill_dict, consistent_temp)
                        consistent_nl.append(consistent_temp_filled)
                        inconsistent_temp_filled = None
                        inconsistent_nl.append(inconsistent_temp_filled)
                        prev_subject = fill_dict['result_label']
                #if we don't want pairwise consistency
                elif dual and not pair_cons and concept == "add":
                    consistent_temp = random.sample(temp_dict["add"][lf_temp], 1)[0]
                    consistent_temp_filled = fill_template(concept, fill_dict, consistent_temp)
                    consistent_nl.append(consistent_temp_filled)
                    inconsistent_temp_filled = None
                    inconsistent_nl.append(inconsistent_temp_filled)
                #for LFs that are not comparisons
                elif dual and concept != 'add':
                    temp = random.sample(temp_dict[concept][lf_temp], 1)[0]
                    temp_filled = fill_template(concept, fill_dict, temp)
                    consistent_nl.append(temp_filled)
                    inconsistent_nl.append(temp_filled)

                if concept == "part":
                    parts.append(fill_dict["whole_label"] + fill_dict["whole_entity"])
            transed_ents = transed_ents + transed_ents_lf
        else:
            concept, fill_dict, lf_temp, transed_ents_q = process_lf(lf, type, track_q=True)
            concept = "q-"+concept
            temp = random.sample(temp_dict[concept][lf_temp], 1)[0]
            temp_filled = fill_template(concept, fill_dict, temp)
            if len(transed_ents_q) > 0 and transed_ents_q[0] in transed_ents_body: temp_filled = temp_filled[:-1] + ' now?'
            nl.append(temp_filled)
        cons_idx += 1
        prev_lf = lf
    if consistency_question is None and not dual: return nl, transed_ents
    else: return consistent_nl, inconsistent_nl, final_cons_idx


def generate_mwp(wm_list, temp_dict, consistency=False, dual=False, pair_cons=False):
    mwp_list = []
    for wm_body, wm_questions, answers in wm_list:
        transed_ents_body = generate_nl_description(wm_body, temp_dict, "body")[1]
        questions = " ".join(generate_nl_description(wm_questions, temp_dict, "question", transed_ents_body)[0])
        question_list = [q.strip() + '?' for q in questions.split('?') if len(q) > 3]
        if not consistency and not dual:
            body = " ".join(generate_nl_description(wm_body, temp_dict, "body")[0])
            mwp_list.append({'body': body, 'questions': question_list, 'answers': answers})
        elif dual:
            consistent_body, inconsistent_body, cons_idx= generate_nl_description(wm_body, temp_dict, "body", dual=True, pair_cons=pair_cons)
            consistent_body = " ".join(consistent_body)
            mwp_list.append({'body': consistent_body, 'questions': question_list, 'answers': answers})
        else:
            consistent_body, inconsistent_body, cons_idx= generate_nl_description(wm_body, temp_dict, "body", consistency_question=wm_questions)
            consistent_body = " ".join(consistent_body)
            inconsistent_body = " ".join(inconsistent_body)
            mwp_list.append({'body': [consistent_body, inconsistent_body], 'questions': question_list, 'answers': answers, 'consistency index': cons_idx})
    return mwp_list


