from random import choice, seed, randint
import random

def generate_dual_models():
    left_agent_id = 1
    left_entity_id = 1
    left_a_fixed = left_agent_id
    left_e_fixed = left_entity_id
    next_agent_id = left_agent_id + 1
    use_unit = False
    use_attr = False
    r_unit = randint(1, 100)
    r_attr = randint(1, 100)
    if r_unit <= 30:
        use_unit = True
        left = 'container ( [agent1] , [n] , [entity1] , None , [unit1] );'
    elif r_attr <= 50:
        use_attr = True
        left = 'container ( [agent1] , [n] , [entity1] , [attr1] , None );'
    else:
        left = 'container ( [agent1] , [n] , [entity1] , None , None );'
    world_model_comp = left
    world_model_trans = left
    n = randint(1,5)
    for i in range(n):
        # TODO: add 'rate' relation (perhaps keep a current entity type variable, indicating whether 'left_entity_id' is a container type or element type)
        #building comparison wm
        negate = choice([True, False])
        first_agent, second_agent = (left_agent_id, next_agent_id) if negate else (next_agent_id, left_agent_id)
        if not use_unit and not use_attr: 
            world_model_comp += ' {} ( [agent{}] , [agent{}] , [n] , [entity{}] , None , None , [entity{}] , None , None );'.format('add', first_agent, second_agent, left_entity_id, left_entity_id)
        elif use_unit: 
            world_model_comp += ' {} ( [agent{}] , [agent{}] , [n] , [entity{}] , None , [unit{}] , [entity{}] , None , [unit{}] );'.format('add', first_agent, second_agent, left_entity_id, left_entity_id, left_entity_id, left_entity_id)
        elif use_attr: 
            world_model_comp += ' {} ( [agent{}] , [agent{}] , [n] , [entity{}] , [attr{}] , None , [entity{}] , [attr{}] , None );'.format('add', first_agent, second_agent, left_entity_id, left_entity_id, left_entity_id, left_entity_id)
        #building transfer wm
        if not use_unit and not use_attr:
            if not negate: world_model_trans += ' transfer ( [agent{}] , [agent{}] , [n] , [entity{}] , None , None );'.format(left_a_fixed, next_agent_id, left_e_fixed)
            else: world_model_trans += ' transfer ( [agent{}] , [agent{}] , [n] , [entity{}] , None , None );'.format(next_agent_id, left_a_fixed, left_e_fixed)
        elif use_unit and not use_attr:
            if not negate: world_model_trans += ' transfer ( [agent{}] , [agent{}] , [n] , [entity{}] , None , [unit{}] );'.format(left_a_fixed, next_agent_id, left_e_fixed, left_e_fixed)
            else: world_model_trans += ' transfer ( [agent{}] , [agent{}] , [n] , [entity{}] , None , [unit{}] );'.format(next_agent_id, left_a_fixed, left_e_fixed, left_e_fixed)
        elif use_attr:
            if not negate: world_model_trans += ' transfer ( [agent{}] , [agent{}] , [n] , [entity{}] , [attr{}] , None );'.format(left_a_fixed, next_agent_id, left_e_fixed, left_e_fixed)
            else: world_model_trans += ' transfer ( [agent{}] , [agent{}] , [n] , [entity{}] , [attr{}] , None );'.format(next_agent_id, left_a_fixed, left_e_fixed, left_e_fixed)
        left_agent_id = next_agent_id
        next_agent_id += 1
    #building comp question
    if not use_unit and not use_attr:
        question_comp = 'container ( [agent{}] , None , [entity{}] , None , None );'.format(left_agent_id, left_entity_id)
    elif use_unit and not use_attr:
        question_comp = 'container ( [agent{}] , None , [entity{}] , None , [unit{}] );'.format(left_agent_id, left_entity_id, left_entity_id)
    elif use_attr:
        question_comp = 'container ( [agent{}] , None , [entity{}] , [attr{}] , None );'.format(left_agent_id, left_entity_id, left_entity_id)
    #building transfer question
    if not use_unit and not use_attr:
        question_trans = 'container ( [agent{}] , None , [entity{}] , None , None );'.format(left_a_fixed, left_e_fixed)
    elif use_unit and not use_attr:
        question_trans = 'container ( [agent{}] , None , [entity{}] , None , [unit{}] );'.format(left_a_fixed, left_e_fixed, left_e_fixed)
    elif use_attr:
        question_trans = 'container ( [agent{}] , None , [entity{}] , [attr{}] , None );'.format(left_a_fixed, left_e_fixed, left_e_fixed)
    return world_model_comp, world_model_trans, question_comp, question_trans

def generate_comp_models():
    left_agent_id = 1
    left_entity_id = 1
    left_a_fixed = left_agent_id
    left_e_fixed = left_entity_id
    next_agent_id = left_agent_id + 1
    use_unit = False
    use_attr = False
    r_unit = randint(1, 100)
    r_attr = randint(1, 100)
    if r_unit <= 30:
        use_unit = True
        left = 'container ( [agent1] , [n] , [entity1] , None , [unit1] );'
    elif r_attr <= 50:
        use_attr = True
        left = 'container ( [agent1] , [n] , [entity1] , [attr1] , None );'
    else:
        left = 'container ( [agent1] , [n] , [entity1] , None , None );'
    world_model_comp = left
    world_model_trans = left
    n = 1
    for i in range(n):
        # TODO: add 'rate' relation (perhaps keep a current entity type variable, indicating whether 'left_entity_id' is a container type or element type)
        #building comparison wm
        negate = choice([True, False])
        first_agent, second_agent = (left_agent_id, next_agent_id) if negate else (next_agent_id, left_agent_id)
        if not use_unit and not use_attr: 
            world_model_comp += ' {} ( [agent{}] , [agent{}] , [n] , [entity{}] , None , None , [entity{}] , None , None );'.format('add', first_agent, second_agent, left_entity_id, left_entity_id)
        elif use_unit: 
            world_model_comp += ' {} ( [agent{}] , [agent{}] , [n] , [entity{}] , None , [unit{}] , [entity{}] , None , [unit{}] );'.format('add', first_agent, second_agent, left_entity_id, left_entity_id, left_entity_id, left_entity_id)
        elif use_attr: 
            world_model_comp += ' {} ( [agent{}] , [agent{}] , [n] , [entity{}] , [attr{}] , None , [entity{}] , [attr{}] , None );'.format('add', first_agent, second_agent, left_entity_id, left_entity_id, left_entity_id, left_entity_id)
        #building transfer wm
        if not use_unit and not use_attr:
            if not negate: world_model_trans += ' transfer ( [agent{}] , [agent{}] , [n] , [entity{}] , None , None );'.format(left_a_fixed, next_agent_id, left_e_fixed)
            else: world_model_trans += ' transfer ( [agent{}] , [agent{}] , [n] , [entity{}] , None , None );'.format(next_agent_id, left_a_fixed, left_e_fixed)
        elif use_unit and not use_attr:
            if not negate: world_model_trans += ' transfer ( [agent{}] , [agent{}] , [n] , [entity{}] , None , [unit{}] );'.format(left_a_fixed, next_agent_id, left_e_fixed, left_e_fixed)
            else: world_model_trans += ' transfer ( [agent{}] , [agent{}] , [n] , [entity{}] , None , [unit{}] );'.format(next_agent_id, left_a_fixed, left_e_fixed, left_e_fixed)
        elif use_attr:
            if not negate: world_model_trans += ' transfer ( [agent{}] , [agent{}] , [n] , [entity{}] , [attr{}] , None );'.format(left_a_fixed, next_agent_id, left_e_fixed, left_e_fixed)
            else: world_model_trans += ' transfer ( [agent{}] , [agent{}] , [n] , [entity{}] , [attr{}] , None );'.format(next_agent_id, left_a_fixed, left_e_fixed, left_e_fixed)
        left_agent_id = next_agent_id
        next_agent_id += 1
    #building comp question
    if not use_unit and not use_attr:
        question_comp = 'container ( [agent{}] , None , [entity{}] , None , None );'.format(left_agent_id, left_entity_id)
    elif use_unit and not use_attr:
        question_comp = 'container ( [agent{}] , None , [entity{}] , None , [unit{}] );'.format(left_agent_id, left_entity_id, left_entity_id)
    elif use_attr:
        question_comp = 'container ( [agent{}] , None , [entity{}] , [attr{}] , None );'.format(left_agent_id, left_entity_id, left_entity_id)
    #building transfer question
    if not use_unit and not use_attr:
        question_trans = 'container ( [agent{}] , None , [entity{}] , None , None );'.format(left_a_fixed, left_e_fixed)
    elif use_unit and not use_attr:
        question_trans = 'container ( [agent{}] , None , [entity{}] , None , [unit{}] );'.format(left_a_fixed, left_e_fixed, left_e_fixed)
    elif use_attr:
        question_trans = 'container ( [agent{}] , None , [entity{}] , [attr{}] , None );'.format(left_a_fixed, left_e_fixed, left_e_fixed)
    return world_model_comp, question_comp

# seed(624768914)
# for n in range(12):
# 	world_model, question = generate_linear_world_model(n)
# 	print('BODY: {}\nQUESTIONS: {}\n'.format(world_model, question))

def save_linear_world(n):
    seed(624768914)
    out_comp = ''
    out_trans = ''
    for _ in range(n):
        world_model_comp, world_model_trans, question_comp, question_trans = generate_dual_models()
        out_comp = out_comp + f'BODY: {world_model_comp}\nQUESTIONS: {question_comp}\n\n'
        out_trans = out_trans + f'BODY: {world_model_trans}\nQUESTIONS: {question_trans}\n\n'
    with open('linear_comp_models.txt', 'w') as f:
        f.write(out_comp)
    with open('linear_trans_models.txt', 'w') as f:
        f.write(out_trans)

def save_comp_world(n):
    seed(624768914)
    out_comp = ''
    for _ in range(n):
        world_model_comp, question_comp = generate_comp_models()
        out_comp = out_comp + f'BODY: {world_model_comp}\nQUESTIONS: {question_comp}\n\n'
    with open('single_comp_models.txt', 'w') as f:
        f.write(out_comp)
    
if __name__ == '__main__':
    save_linear_world(610)
