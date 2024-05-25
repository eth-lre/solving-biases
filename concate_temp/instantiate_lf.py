import re
import random
import json
import copy
from tqdm import tqdm
import pickle

random.seed(1)


def get_special_relations_dict(wm):
    lfs = [item.strip() for item in wm.split(";")][:-1]
    part_whole_dict = {}
    rate_dict = {}
    ent_unit_dict = {}
    for lf in lfs:
        parts = [item.strip() for item in re.split("\(|\)|,", lf)]
        if parts[0] == "part":
            whole_entity = parts[3]
            part_entity = parts[6]
            w_unit = parts[4]
            p_unit = parts[8]

            if whole_entity not in part_whole_dict:
                part_whole_dict[whole_entity] = []
            part_whole_dict[whole_entity].append(part_entity)
            if w_unit != 'None' and whole_entity not in ent_unit_dict:
                ent_unit_dict[whole_entity] = w_unit
        # elif parts[0] == "rate":
        #     source_entity = parts[3]
        #     target_entity = parts[6]
        #     rate_dict[target_entity] = source_entity
        elif parts[0] == "container":
            entity = parts[3]
            unit = parts[5]
            if unit != 'None' and entity not in ent_unit_dict:
                    ent_unit_dict[entity] = unit
        elif parts[0] == "transfer":
            entity = parts[4]
            unit = parts[6]
            if unit != 'None' and entity not in ent_unit_dict:
                    ent_unit_dict[entity] = unit
        elif parts[0] == "add":
            r_entity = parts[4]
            r_unit = parts[6]
            a_entity = parts[7]
            a_unit = parts[9]
            if r_unit != 'None' and r_entity not in ent_unit_dict:
                    ent_unit_dict[r_entity] = r_unit
            if a_unit != 'None' and a_entity not in ent_unit_dict:
                    ent_unit_dict[a_entity] = a_unit
        elif parts[0] == "times":
            r_entity = parts[4]
            r_unit = parts[6]
            a_entity = parts[7]
            a_unit = parts[9]
            if r_unit != 'None' and r_entity not in ent_unit_dict:
                    ent_unit_dict[r_entity] = r_unit
            if a_unit != 'None' and a_entity not in ent_unit_dict:
                    ent_unit_dict[a_entity] = a_unit
        elif parts[0] == "rate":
            s_entity = parts[3]
            s_unit = parts[5]
            t_entity = parts[6]
            t_unit = parts[8]
            rate_dict[t_entity] = s_entity
            if s_unit != 'None' and s_entity not in ent_unit_dict:
                    ent_unit_dict[s_entity] = s_unit
            if t_unit != 'None' and t_entity not in ent_unit_dict:
                    ent_unit_dict[t_entity] = t_unit
        

    return part_whole_dict, rate_dict, ent_unit_dict


def get_answer_for_lf(lf, entities_for_agent):
    parts = [item.strip() for item in re.split("\(|\)|,", lf)]
    if parts[0] == "container":
        agent = parts[1]
        entity = parts[3]
        attribute = parts[4] + '_' if parts[4] != "None" else ""
        answer = entities_for_agent[(agent, attribute + entity)]
    elif parts[0] == "add":
        object = parts[1]
        subject = parts[2]
        obj_entity = parts[4]
        obj_attribute = parts[5] + '_' if parts[5] != "None" else ""
        subj_entity = parts[7]
        subj_attribute = parts[8] + '_' if parts[8] != "None" else ""
        complete_obj = obj_attribute + obj_entity
        complete_subj = subj_attribute + subj_entity
        answer = entities_for_agent[(object, complete_obj)] - entities_for_agent[(subject, complete_subj)]
    elif parts[0] == "rate":
        agent = parts[1]
        source_entity = parts[3]
        source_attribute = parts[4] + '_' if parts[4] != "None" else ""
        target_entity = parts[6]
        target_attribute = parts[7] + '_' if parts[7] != "None" else ""
        answer = entities_for_agent[(agent, target_attribute + target_entity)] / entities_for_agent[
            (agent, source_attribute + source_entity)]
    else:
        raise ValueError(f"LF {lf} not yet supported")

    return answer


def get_entity_n_for_agent(entities_for_agent, agent, entity, attribute):
    if attribute == "":
        if (agent, entity) in entities_for_agent:
            return entities_for_agent[(agent, entity)]
        else:
            counter = 0
            for k, v in entities_for_agent.items():
                if len(k[1].split("_")) == 2:
                    attr, ent = k[1].split("_")
                    if k[0] == agent and ent == entity:
                        counter += v
            if counter == 0:
                raise ValueError(f"Agent {agent} does not have any {entity}")
            return counter
    else:
        return entities_for_agent[(agent, attribute + entity)]

def is_carry(a, b, mode):
    carry = False
    a = int(a)
    b = int(b)
    carry_count = 0
    if a < 0 or b < 0:
        return False, 0
    if mode == 'add':
        a = str(a)
        b = str(b)
        dig_len = min(len(a), len(b))
        right_digit_carried = False
        for i in range(1, dig_len+1):
            if int(a[-i]) + int(b[-i]) > 9 or (right_digit_carried and int(a[-i]) + int(b[-i]) == 9):
                carry_count += 1
                right_digit_carried = True
                carry = True
            else:
                right_digit_carried = False
    if mode == 'sub':
        if a < b:
            carry = False
        a = str(a)
        b = str(b)
        dig_len = min(len(a), len(b))
        right_digit_borrowed = False
        for i in range(1, dig_len+1):
            if int(a[-i]) < int(b[-i]) or (right_digit_borrowed and int(a[-i]) == int(b[-i])):
                carry_count += 1
                right_digit_borrowed = True
                carry = True
            else:
                right_digit_borrowed = False
    return carry, carry_count
        
def process_lf(lf, entities_for_agent_list, predicate_stack, check_carry=False, index=None):
    carry_happened = False
    add_carry = False
    sub_carry = False
    ghost_tranfer = False
    carry_count = 0
    if len(entities_for_agent_list) > 0:
        entities_for_agent = entities_for_agent_list[-1].copy()
    else:
        entities_for_agent = {}
    parts = [item.strip() for item in re.split("\(|\)|,", lf)]
    if parts[0] == "container":
        agent = parts[1]
        n = int(parts[2])
        entity = parts[3]
        attribute = parts[4] + '_' if parts[4] != "None" else ""
        if attribute:
            entities_for_agent[(agent, attribute + entity)] = n
        if (agent, entity) not in entities_for_agent:
            entities_for_agent[(agent, entity)] = 0
        entities_for_agent[(agent, entity)] += n
    elif parts[0] == "transfer":
        receiver = parts[1]
        sender = parts[2]
        n = int(parts[3])
        entity = parts[4]
        attribute = parts[5] + '_' if parts[5] != "None" else ""
        # assumes that the transfer comes after a container introduces the agent
        if not receiver == "None":
            if attribute:
                if (receiver, attribute + entity) not in entities_for_agent:
                    entities_for_agent[(receiver, attribute + entity)] = 0
                if check_carry:
                    carry_happened = carry_happened or is_carry(entities_for_agent[(receiver, attribute + entity)], n, 'add')[0]
                    carry_count = carry_count + is_carry(entities_for_agent[(receiver, attribute + entity)], n, 'add')[1]
                entities_for_agent[(receiver, attribute + entity)] += n
            if (receiver, entity) not in entities_for_agent:
                entities_for_agent[(receiver, entity)] = 0
            # update also the total number of entities
            if check_carry:
                    carry_happened = carry_happened or is_carry(entities_for_agent[(receiver, entity)], n, 'add')[0]
                    carry_count = carry_count + is_carry(entities_for_agent[(receiver, entity)], n, 'add')[1]
            entities_for_agent[(receiver, entity)] += n
        if not sender == "None":
            if attribute:
                if (sender, attribute + entity) not in entities_for_agent:
                    entities_for_agent[(sender, attribute + entity)] = n
                if check_carry:
                    carry_happened = carry_happened or is_carry(entities_for_agent[(sender, attribute + entity)], n, 'sub')[0]
                    carry_count = carry_count + is_carry(entities_for_agent[(sender, attribute + entity)], n, 'sub')[1]
                entities_for_agent[(sender, attribute + entity)] -= n
            # when undefined agent sends something, we just pretend he has enough to send
            if (sender, entity) not in entities_for_agent:
                entities_for_agent[(sender, entity)] = n
            # update also the total number of entities
            if check_carry:
                    carry_happened = carry_happened or is_carry(entities_for_agent[(sender, entity)], n, 'sub')[0]
                    carry_count = carry_count + is_carry(entities_for_agent[(sender, entity)], n, 'sub')[1]
            entities_for_agent[(sender, entity)] -= n
    elif parts[0] == "add" or parts[0] == "times":
        object = parts[1]
        subject = parts[2]
        n = int(parts[3])
        obj_entity = parts[4]
        obj_attribute = parts[5] + '_' if parts[5] != "None" else ""
        subj_entity = parts[7]
        subj_attribute = parts[8] + '_' if parts[8] != "None" else ""
        complete_obj = obj_attribute + obj_entity
        complete_subj = subj_attribute + subj_entity
        if parts[0] == "times":
            if (object, complete_obj) in entities_for_agent:
                if subj_attribute:
                    entities_for_agent[(subject, complete_subj)] = entities_for_agent[(object, complete_obj)] / n
                if (subject, subj_entity) not in entities_for_agent:
                    entities_for_agent[(subject, subj_entity)] = 0
                # update also the total number of entities
                entities_for_agent[(subject, subj_entity)] += entities_for_agent[(object, complete_obj)] / n
            elif (subject, complete_subj) in entities_for_agent:
                if obj_attribute:
                    entities_for_agent[(object, complete_obj)] = n * entities_for_agent[(subject, complete_subj)]
                if (object, obj_entity) not in entities_for_agent:
                    entities_for_agent[(object, obj_entity)] = 0
                # update also the total number of entities
                entities_for_agent[(object, obj_entity)] += n * entities_for_agent[(subject, complete_subj)]
            else:
                predicate_stack.append(lf)
        elif parts[0] == "add":
            if (object, complete_obj) in entities_for_agent:
                # we already know the number of entities for the object, and
                # we are updating the number of entities for the subject
                if subj_attribute:
                    entities_for_agent[(subject, complete_subj)] = entities_for_agent[(object, complete_obj)] - n
                    if check_carry:
                        carry_happened = carry_happened or is_carry(entities_for_agent[(object, complete_obj)], n, 'sub')[0]
                        if is_carry(entities_for_agent[(object, complete_obj)], n, 'sub')[0]: 
                            sub_carry = True
                if (subject, subj_entity) not in entities_for_agent:
                    entities_for_agent[(subject, subj_entity)] = 0
                # update also the total number of entities
                entities_for_agent[(subject, subj_entity)] += entities_for_agent[(object, complete_obj)] - n
                if check_carry:
                        carry_happened = carry_happened or is_carry(entities_for_agent[(object, complete_obj)], n, 'sub')[0]
                        carry_count = carry_count + is_carry(entities_for_agent[(object, complete_obj)], n, 'sub')[1]
                        if is_carry(entities_for_agent[(object, complete_obj)], n, 'sub')[0]:
                            sub_carry = True
            elif (subject, complete_subj) in entities_for_agent:
                # we already know the number of entities for the subject, and
                # we are updating the number of entities for the object
                if obj_attribute:
                    entities_for_agent[(object, complete_obj)] = entities_for_agent[(subject, complete_subj)] + n
                    if check_carry:
                        carry_happened = carry_happened or is_carry(entities_for_agent[(subject, complete_subj)], n, 'add')[0]
                        if is_carry(entities_for_agent[(subject, complete_subj)], n, 'add')[0]:
                            add_carry = True
                if (object, obj_entity) not in entities_for_agent:
                    entities_for_agent[(object, obj_entity)] = 0
                # update also the total number of entities
                entities_for_agent[(object, obj_entity)] += entities_for_agent[(subject, complete_subj)] + n
                if check_carry:
                        carry_happened = carry_happened or is_carry(entities_for_agent[(subject, complete_subj)], n, 'add')[0]
                        carry_count = carry_count + is_carry(entities_for_agent[(subject, complete_subj)], n, 'add')[1]
                        if is_carry(entities_for_agent[(subject, complete_subj)], n, 'add')[0]:
                            add_carry = True

            else:
                predicate_stack.append(lf)
    elif parts[0] == "rate":
        agent = parts[1]
        n = int(parts[2])
        source_entity = parts[3]
        source_attribute = parts[4] + '_' if parts[4] != "None" else ""
        target_entity = parts[6]
        target_attribute = parts[7] + '_' if parts[7] != "None" else ""
        if (agent, source_entity) in entities_for_agent:
            if target_attribute:
                entities_for_agent[(agent, target_attribute + target_entity)] = entities_for_agent[(agent, source_attribute + source_entity)] / n
            if (agent, target_entity) not in entities_for_agent:
                entities_for_agent[(agent, target_entity)] = 0
            entities_for_agent[(agent, target_entity)] += entities_for_agent[(agent, source_attribute + source_entity)] / n # update also the total number of entities
        elif (agent, target_entity) in entities_for_agent:
            if source_attribute:
                entities_for_agent[(agent, source_attribute + source_entity)] = entities_for_agent[(agent, target_attribute + target_entity)] * n
            if (agent, source_entity) not in entities_for_agent:
                entities_for_agent[(agent, source_entity)] = 0
            entities_for_agent[(agent, source_entity)] += entities_for_agent[(agent, target_attribute + target_entity)] * n # update also the total number of entities
        else:
            predicate_stack.append(lf)
    elif parts[0] == "part":
        # todo covers only a specific case
        whole_agent = parts[1]
        agent = parts[2]
        whole_entity = parts[3]
        part_entity = parts[6]
        if (whole_agent, whole_entity) not in entities_for_agent:
            entities_for_agent[(whole_agent, whole_entity)] = 0
        entities_for_agent[(parts[1], whole_entity)] += entities_for_agent[(agent, part_entity)]
    else:
        print("Out of the six concepts: " + lf)

    entities_for_agent_list.append(entities_for_agent)
    # if index == 5:
    #     print(f"\n carry_happened at index 5: {carry_happened}")
    if check_carry:
        return entities_for_agent_list, predicate_stack, carry_happened, add_carry, sub_carry, carry_count
    return entities_for_agent_list, predicate_stack


def check_number_consistency(wm, check_carry=False, index=None):
    lfs = [item.strip() for item in wm.split(";")][:-1]
    entities_for_agent_list = []
    predicate_stack = []
    carry_list = []
    add_carry_list = []
    sub_carry_list = []
    carry_count_list = []
    for lf in lfs:
        if check_carry: 
            entities_for_agent_list, predicate_stack, carry_happened, add_carry, sub_carry, carry_count = process_lf(lf, entities_for_agent_list, predicate_stack, check_carry=check_carry, index=index)
            carry_list.append(carry_happened)
            add_carry_list.append(add_carry)
            sub_carry_list.append(sub_carry)
            carry_count_list.append(carry_count)
        else: 
            entities_for_agent_list, predicate_stack = process_lf(lf, entities_for_agent_list, predicate_stack)

    # now instantiate the remaining predicates
    counter = 0
    while len(predicate_stack) > 0:
        lf = predicate_stack.pop(0)
        if check_carry: 
            entities_for_agent_list, predicate_stack, carry_happened, add_carry, sub_carry, carry_count = process_lf(lf, entities_for_agent_list, predicate_stack, check_carry=check_carry)
            carry_list.append(carry_happened)
            add_carry_list.append(add_carry)
            sub_carry_list.append(sub_carry)
            carry_count_list.append(carry_count)
        else: 
            entities_for_agent_list, predicate_stack = process_lf(lf, entities_for_agent_list, predicate_stack)
        counter += 1
        if counter > 100:
            print(f'WM: {wm}')
            print(f'entities_for_agent: {entities_for_agent_list}')
            print("Predicate stack: " + str(predicate_stack))
            raise Exception("Predicate stack is not empty after 100 iterations")
    if check_carry:
        return entities_for_agent_list, carry_list, add_carry_list, sub_carry_list, carry_count_list
    return entities_for_agent_list


def compute_answers(wm_questions, entities_for_agent):
    lfs = [item.strip() for item in wm_questions.split(";")][:-1]
    answers = []
    for lf in lfs:
        answer = get_answer_for_lf(lf, entities_for_agent)
        answers.append(answer)
    return lfs, answers


def instantiate_numbers(s1, s2=None):
    def replace(match):
        r_int = str(random.randint(2, 20))
        return r_int
    
    def replace_second(match, replace_list):
        replacement = replace_list.pop(0)
        return replacement

    pattern = r'\[n\]'  # Regex pattern to match substrings of the form "[n]"
    if s2 is None: 
        replaced_string = re.sub(pattern, replace, s1)
        return replaced_string
    else: 
        r1 = re.sub(pattern, replace, s1)
        #extract numbers from randomized initialization so that second wm gets the same numbers
        replace_list = re.findall(r'\W\d+', r1)
        r2 = re.sub(pattern, lambda x : replace_second(x, replace_list), s2)
        return r1, r2

def instantiate_numbers_big(s1, s2=None):
    def replace(match):
        r_int = str(random.randint(100, 999))
        return r_int
    
    def replace_second(match, replace_list):
        replacement = replace_list.pop(0)
        return replacement

    pattern = r'\[n\]'  # Regex pattern to match substrings of the form "[n]"
    if s2 is None: 
        replaced_string = re.sub(pattern, replace, s1)
        return replaced_string


def instantiate_names(s, name_list_og, replacements, type="agent", dual=None, carry_dual=None):
    replacement_list = []
    replacement_list_dual = []
    def replace(match, replacement_list):
        substring = match.group(0)

        if substring not in replacements:
            choice = random.choice(range(len(name_list)))
            replacements[substring] = name_list.pop(choice)
        replacement_list.append(replacements[substring])

        return replacements[substring]

    def replace_dual(match, replacement_list):
        replacement = replacement_list.pop(0)
        return replacement

    name_list = copy.deepcopy(name_list_og)

    if type == "agent":
        pattern = r'\[agent\d+\]'
    elif type == "entity":
        pattern = r'\[entity\d+\]'
    elif type == "attribute":
        pattern = r'\[attr\d+\]'
    elif type == "unit":
        pattern = r'\[unit\d+\]'
    else:
        raise Exception("Type not recognized")
    if carry_dual:
        r1 = re.sub(pattern, lambda x : replace(x, replacement_list), s)
        r2 = re.sub(pattern, lambda x : replace(x, replacement_list_dual), carry_dual)
        return r1, r2
    elif dual is None: 
        replaced_string = re.sub(pattern, lambda x : replace(x, replacement_list), s)
        return replaced_string
    elif type != 'agent': 
        r1 = re.sub(pattern, lambda x : replace(x, replacement_list), s)
        r2 = re.sub(pattern, lambda x: replace_dual(x, replacement_list), dual)
        return r1, r2
    else:
        r1 = re.sub(pattern, lambda x : replace(x, replacement_list), s)
        r2 = re.sub(pattern, lambda x : replace(x, replacement_list_dual), dual)
        return r1, r2


def initialize_replacements(part_whole_names_og, ent_unit_names_og, part_whole_dict, rate_dict, ent_unit_dict):
    part_whole_names = copy.deepcopy(part_whole_names_og)
    ent_unit_names = copy.deepcopy(ent_unit_names_og)
    replacements = {}
    container_names = part_whole_names.pop("containers")

    for whole_entity, list_of_parts in part_whole_dict.items():
        replacements[whole_entity] = random.choice(list(part_whole_names.keys()))
        for part_entity in list_of_parts:
            possible_part_names = part_whole_names[replacements[whole_entity]]
            choice = random.choice(range(len(possible_part_names)))
            replacements[part_entity] = possible_part_names.pop(choice)
        part_whole_names.pop(replacements[whole_entity])

    for container_entity in rate_dict:
        if container_entity in replacements:
            if container_entity in part_whole_dict.keys():  # handling the case where a container is also a whole
                replacements[container_entity] = "containers"
                for part_entity in part_whole_dict[container_entity]:
                    choice = random.choice(range(len(container_names)))
                    replacements[part_entity] = container_names.pop(choice)
        else:
            choice = random.choice(range(len(container_names)))
            replacements[container_entity] = container_names.pop(choice)
    
    for entity, unit in ent_unit_dict.items():
        if entity in replacements:
            if replacements[entity] in ent_unit_names.keys():   
                replacements[unit] = ent_unit_names[replacements[entity]]
            else:
                replacements[unit] = 'None'
        else:
            replacements[entity] = random.choice(list(ent_unit_names.keys()))
            replacements[unit] = ent_unit_names[replacements[entity]]


    return replacements


def check_if_valid(list_of_numbers, big=None):
    if big:
        for v in list_of_numbers:
            if v not in range(100, 1000):
                return False
            if float(int(v)) != float(v):
                return False
    else:
        for v in list_of_numbers:
            if v not in range(0, 1000):
                return False
            if float(int(v)) != float(v):
                return False
    return True


def instantiate_logical_form(empy_lf_path, destination_path, n_instances, check_carry=False):
    with open(empy_lf_path) as f:
        lines = [line.replace('\n', '') for line in f.readlines()]
    with open('data/entities.csv') as f:
        entities = [e.replace('\n', '') for e in f.readlines()]
    with open('data/agent_names.csv') as f:
        agents = [a.replace('\n', '') for a in f.readlines()]
    with open('data/part_whole_entities.json') as f:
        part_whole_names = json.load(f)
    with open('data/ent_unit_names.json') as f:
        ent_unit_names = json.load(f)
    with open('data/attributes.csv') as f:
        attributes = [a.replace('\n', '') for a in f.readlines()]
    with open('data/units.csv') as f:
        units  = [a.replace('\n', '') for a in f.readlines()]

    instantiated_world_models = []

    pbar = tqdm(total=int(n_instances * (len(lines) / 3)) + 1)

    for i in range(len(lines)):
        if lines[i].startswith('BODY: '):
            line = lines[i].replace('BODY: ', '')
            body_wm = line
            questions_wm = lines[i + 1].replace('QUESTIONS: ', '')

            for _ in range(n_instances):
                counter = 0
                while 1:
                    instantiated_numbers = instantiate_numbers(body_wm)
                    if check_carry: 
                        entities_for_agent_list, carry_happened = check_number_consistency(instantiated_numbers, check_carry=check_carry)
                    else:
                        entities_for_agent_list = check_number_consistency(instantiated_numbers)
                    question_lfs, answers = compute_answers(questions_wm, entities_for_agent_list[-1])
                    flattened_values = [value for entities_for_agent in entities_for_agent_list for value in entities_for_agent.values() ]
                    if check_carry and not carry_happened and check_if_valid(flattened_values) and check_if_valid(answers):
                        break
                    elif not check_carry and check_if_valid(flattened_values) and check_if_valid(answers):
                        break
                    counter += 1
                    if counter > 1000000000:
                        raise Exception("Could not find a valid instantiation after 1000000000 iterations")
                part_whole_dict, rate_dict, ent_unit_dict = get_special_relations_dict(instantiated_numbers)
                wm = instantiated_numbers + '\n' + questions_wm
                replacements = initialize_replacements(part_whole_names, ent_unit_names, part_whole_dict, rate_dict, ent_unit_dict)
                wm = instantiate_names(wm, entities, replacements=replacements, type="entity")
                wm = instantiate_names(wm, attributes, replacements=replacements, type="attribute")
                wm = instantiate_names(wm, agents, replacements=replacements, type="agent")
                wm = instantiate_names(wm, units, replacements=replacements, type="unit")
                instantiated_body, instantiated_questions = wm.split('\n')

                instantiated_world_models.append((instantiated_body, instantiated_questions, answers))
                pbar.update(1)

    with open(destination_path, 'wb') as f:
        pickle.dump(instantiated_world_models, f)
    

    return instantiated_world_models

def instantiate_dual_form(empty_comp_lf_path, empty_trans_lf_path, destination_path_comp, destination_path_trans, n_instances):
    with open(empty_comp_lf_path) as f:
        lines_comp = [line.replace('\n', '') for line in f.readlines()]
    with open(empty_trans_lf_path) as f:
        lines_trans = [line.replace('\n', '') for line in f.readlines()]
    with open('data/entities.csv') as f:
        entities = [e.replace('\n', '') for e in f.readlines()]
    with open('data/agent_names.csv') as f:
        agents = [a.replace('\n', '') for a in f.readlines()]
    with open('data/part_whole_entities.json') as f:
        part_whole_names = json.load(f)
    with open('data/ent_unit_names.json') as f:
        ent_unit_names = json.load(f)
    with open('data/attributes.csv') as f:
        attributes = [a.replace('\n', '') for a in f.readlines()]
    with open('data/units.csv') as f:
        units  = [a.replace('\n', '') for a in f.readlines()]

    instantiated_world_models_comp = []
    instantiated_world_models_trans = []

    pbar = tqdm(total=int(n_instances * (len(lines_comp) / 3)) + 1)

    for i in range(len(lines_comp)):
        if lines_comp[i].startswith('BODY: '):
            #instantiate comparison
            line_comp = lines_comp[i].replace('BODY: ', '')
            body_wm_comp = line_comp
            questions_wm_comp = lines_comp[i + 1].replace('QUESTIONS: ', '')
            #instantiate transfer
            line_trans = lines_trans[i].replace('BODY: ', '')
            body_wm_trans = line_trans
            questions_wm_trans = lines_trans[i + 1].replace('QUESTIONS: ', '')

            for _ in range(n_instances):
                counter = 0
                while 1:
                    instantiated_numbers_comp, instantiated_numbers_trans = instantiate_numbers(body_wm_comp, body_wm_trans)
                    entities_for_agent_list = check_number_consistency(instantiated_numbers_comp)
                    question_lfs_comp, answers = compute_answers(questions_wm_comp, entities_for_agent_list[-1])
                    flattened_values = [value for entities_for_agent in entities_for_agent_list for value in entities_for_agent.values() ]
                    if check_if_valid(flattened_values) and check_if_valid(answers):
                        break
                    counter += 1
                    if counter > 1000000000:
                        raise Exception("Could not find a valid instantiation after 1000000000 iterations")
                part_whole_dict, rate_dict, ent_unit_dict = get_special_relations_dict(instantiated_numbers_comp)
                wm_comp = instantiated_numbers_comp+ '\n' + questions_wm_comp
                wm_trans = instantiated_numbers_trans+ '\n' + questions_wm_trans
                replacements = initialize_replacements(part_whole_names, ent_unit_names, part_whole_dict, rate_dict, ent_unit_dict)
                wm_comp, wm_trans = instantiate_names(wm_comp, entities, replacements=replacements, type="entity", dual=wm_trans)
                wm_comp, wm_trans = instantiate_names(wm_comp, attributes, replacements=replacements, type="attribute", dual=wm_trans)
                wm_comp, wm_trans = instantiate_names(wm_comp, agents, replacements=replacements, type="agent", dual=wm_trans)
                wm_comp, wm_trans = instantiate_names(wm_comp, units, replacements=replacements, type="unit", dual=wm_trans)
                instantiated_body_comp, instantiated_questions_comp = wm_comp.split('\n')
                instantiated_body_trans, instantiated_questions_trans = wm_trans.split('\n')

                instantiated_world_models_comp.append((instantiated_body_comp, instantiated_questions_comp, answers))
                instantiated_world_models_trans.append((instantiated_body_trans, instantiated_questions_trans, answers))
                pbar.update(1)

    with open(destination_path_comp, 'wb') as f:
        pickle.dump(instantiated_world_models_comp, f)
    with open(destination_path_trans, 'wb') as f:
        pickle.dump(instantiated_world_models_trans, f)
    

    return instantiated_world_models_comp, instantiated_world_models_trans

def instantiate_nocarry_carry(empy_lf_path, destination_path_nc, destination_path_c, n_instances, debug=False):
    with open(empy_lf_path) as f:
        lines = [line.replace('\n', '') for line in f.readlines()]
    with open('data/entities.csv') as f:
        entities = [e.replace('\n', '') for e in f.readlines()]
    with open('data/agent_names.csv') as f:
        agents = [a.replace('\n', '') for a in f.readlines()]
    with open('data/part_whole_entities.json') as f:
        part_whole_names = json.load(f)
    with open('data/ent_unit_names.json') as f:
        ent_unit_names = json.load(f)
    with open('data/attributes.csv') as f:
        attributes = [a.replace('\n', '') for a in f.readlines()]
    with open('data/units.csv') as f:
        units  = [a.replace('\n', '') for a in f.readlines()]

    instantiated_world_models_nc = []
    instantiated_world_models_c = []
    add_sub_both = []
    num_carries = []

    pbar = tqdm(total=int(n_instances * (len(lines) / 3)) + 1)

    n_problems = int(n_instances * (len(lines) / 3)) + 1
    index = 0
    for i in range(len(lines)):
        if lines[i].startswith('BODY: '):
            abort_problem = False
            sum_carry = random.randint(1,2)
            line = lines[i].replace('BODY: ', '')
            body_wm = line
            questions_wm = lines[i + 1].replace('QUESTIONS: ', '')

            for _ in range(n_instances):
                counter = 0
                while 1:
                    check_carry = True
                    instantiated_numbers_nc = instantiate_numbers_big(body_wm)
                    if check_carry: 
                        entities_for_agent_list, carry_list, _, _, _ = check_number_consistency(instantiated_numbers_nc, check_carry=check_carry, index=index)
                    question_lfs_nc, answers_nc = compute_answers(questions_wm, entities_for_agent_list[-1])
                    control_answer = answers_nc[0]
                    flattened_values = [value for entities_for_agent in entities_for_agent_list for value in entities_for_agent.values() ]
                    if debug and not any(carry_list) and check_if_valid(flattened_values, big=True) and check_if_valid(answers_nc, big=True): 
                        pass
                    if check_carry and not any(carry_list) and check_if_valid(flattened_values, big=True) and check_if_valid(answers_nc, big=True):
                        break
                    counter += 1
                    if counter > 100000:
                        abort_problem = True
                        break
                if abort_problem:
                    continue
                counter = 0
                while 1:
                    check_carry = True
                    instantiated_numbers_c = instantiate_numbers_big(body_wm)
                    if check_carry: 
                        entities_for_agent_list, carry_list, add_carry_list, sub_carry_list, carry_count_list = check_number_consistency(instantiated_numbers_c, check_carry=check_carry)
                    question_lfs_c, answers_c = compute_answers(questions_wm, entities_for_agent_list[-1])
                    carry_answer = answers_c[0]
                    flattened_values = [value for entities_for_agent in entities_for_agent_list for value in entities_for_agent.values() ]
                    if debug and any(carry_list) and check_if_valid(flattened_values, big=True) and check_if_valid(answers_c, big=True) and carry_answer == control_answer and index==8:
                        print(f'{entities_for_agent_list}')
                        print(f'{carry_list}\n')
                        print(f'{carry_count_list}')
                    if check_carry and any(carry_list) and check_if_valid(flattened_values, big=True) and check_if_valid(answers_c, big=True) and carry_answer == control_answer:
                        if sum(carry_count_list) == sum_carry:
                            break
                    counter += 1
                    if counter > 100000:
                        print(f'aborted index {index}')
                        abort_problem = True
                        break
                if abort_problem:
                    continue
                part_whole_dict, rate_dict, ent_unit_dict = get_special_relations_dict(instantiated_numbers_nc)
                wm_nc = instantiated_numbers_nc+ '\n' + questions_wm
                wm_c = instantiated_numbers_c+ '\n' + questions_wm
                replacements = initialize_replacements(part_whole_names, ent_unit_names, part_whole_dict, rate_dict, ent_unit_dict)
                wm_nc, wm_c = instantiate_names(wm_nc, entities, replacements=replacements, type="entity", carry_dual=wm_c)
                wm_nc, wm_c = instantiate_names(wm_nc, attributes, replacements=replacements, type="attribute", carry_dual=wm_c)
                wm_nc, wm_c = instantiate_names(wm_nc, agents, replacements=replacements, type="agent", carry_dual=wm_c)
                wm_nc, wm_c = instantiate_names(wm_nc, units, replacements=replacements, type="unit", carry_dual=wm_c)
                instantiated_body_nc, instantiated_questions_nc = wm_nc.split('\n')
                instantiated_body_c, instantiated_questions_c = wm_c.split('\n')

                instantiated_world_models_nc.append((instantiated_body_nc, instantiated_questions_nc, answers_nc))
                instantiated_world_models_c.append((instantiated_body_c, instantiated_questions_c, answers_c))
                if any(add_carry_list) and any(sub_carry_list):
                    add_sub_both.append('Both')
                elif any(add_carry_list) and not any(sub_carry_list):
                    add_sub_both.append('Addition')
                elif not any(add_carry_list) and any(sub_carry_list):
                    add_sub_both.append('Subtraction')

                num_carries.append(sum(carry_count_list))
                pbar.update(1)
            index+=1

    with open(destination_path_nc, 'wb') as f:
        pickle.dump(instantiated_world_models_nc, f)
    with open(destination_path_c, 'wb') as f:
        pickle.dump(instantiated_world_models_c, f)
    
    if debug:
        print(instantiated_world_models_nc[8])
        print('')
        print(instantiated_world_models_c[8])
    

    return instantiated_world_models_nc, instantiated_world_models_c, add_sub_both, num_carries


if __name__ == "__main__":
    instantiate_logical_form('data/empy_world_models.txt')