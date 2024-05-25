from random import choice, seed, randint
import random

def generate_consistency_model():
    #pointer to left most agent and entity
    left_agent_id = 1
    left_entity_id = 1
    #pointer to most recently added agent/entity
    next_agent_id = left_agent_id + 1
    #set them as equal intially and on first invocation, increment 
    next_entity_id = left_entity_id
    use_unit = False
    use_attr = False
    r_unit = randint(1, 100)
    r_attr = randint(1, 100)
    n_first = randint(0,2)
    n_subject = randint(0,2)
    if r_unit <= 30:
        use_unit = True
        left = 'container ( [agent1] , [n] , [entity1] , None , [unit1] );'
    elif r_attr <= 50:
        use_attr = True
        left = 'container ( [agent1] , [n] , [entity1] , [attr1] , None );'
    else:
        left = 'container ( [agent1] , [n] , [entity1] , None , None );'
    world_model = left
    #generating preface blocks
    #transfer after rate is too ambiguous so we break after rate sampled
    for i in range(n_first):
        sample_relation = randint(0,1)
        if not use_unit and not use_attr:
            if sample_relation == 0: 
                world_model += ' transfer ( [agent{}] , None , [n] , [entity{}] , None , None );'.format(left_agent_id, left_entity_id)
            elif sample_relation == 1:
                next_entity_id += 1
                world_model += f' rate ( [agent{left_agent_id}] , [n] , [entity{next_entity_id}] , None , None , [entity{left_entity_id}] , None , None );'
                left_entity_id = next_entity_id
        elif use_unit and not use_attr:
            if sample_relation == 0:
                world_model += ' transfer ( [agent{}] , None , [n] , [entity{}] , None , [unit{}] );'.format(left_agent_id, left_entity_id, left_entity_id)
            elif sample_relation == 1:
                next_entity_id += 1
                world_model += f' rate ( [agent{left_agent_id}] , [n] , [entity{next_entity_id}] , None , [unit{next_entity_id}] , [entity{left_entity_id}] , None , [unit{left_entity_id}] );'
                left_entity_id = next_entity_id
        elif use_attr:
            if sample_relation == 0:
                world_model += ' transfer ( [agent{}] , None , [n] , [entity{}] , [attr{}] , None );'.format(left_agent_id, left_entity_id, left_entity_id)
            elif sample_relation == 1:
                next_entity_id += 1
                world_model += f' rate ( [agent{left_agent_id}] , [n] , [entity{next_entity_id}] , [attr{next_entity_id}] , None , [entity{left_entity_id}] , [attr{left_entity_id}] , None );'
                left_entity_id = next_entity_id
    #generating consistency block
    operation = choice(['add', 'times'])
    negate = choice([True, False]) 
    first_agent, second_agent = (left_agent_id, next_agent_id) if negate else (next_agent_id, left_agent_id)
    #choosing random entity that left most agent posesses as the 'entity of interest' (the entity which will be asked about)
    left_entity_id = randint(1, next_entity_id)
    if not use_unit and not use_attr: 
        world_model += ' {} ( [agent{}] , [agent{}] , [n] , [entity{}] , None , None , [entity{}] , None , None );'.format(operation, first_agent, second_agent, left_entity_id, left_entity_id)
    elif use_unit: 
        world_model += ' {} ( [agent{}] , [agent{}] , [n] , [entity{}] , None , [unit{}] , [entity{}] , None , [unit{}] );'.format(operation, first_agent, second_agent, left_entity_id, left_entity_id, left_entity_id, left_entity_id)
    elif use_attr: 
        world_model += ' {} ( [agent{}] , [agent{}] , [n] , [entity{}] , [attr{}] , None , [entity{}] , [attr{}] , None );'.format(operation, first_agent, second_agent, left_entity_id, left_entity_id, left_entity_id, left_entity_id)
    #adding transfers and rates to subject entity
    for i in range(n_subject):
        sample_relation = randint(0,1)
        if not use_unit and not use_attr:
            if sample_relation == 0: 
                world_model += ' transfer ( [agent{}] , None , [n] , [entity{}] , None , None );'.format(next_agent_id, left_entity_id)
            elif sample_relation == 1:
                next_entity_id += 1
                world_model += f' rate ( [agent{next_agent_id}] , [n] , [entity{next_entity_id}] , None , None , [entity{left_entity_id}] , None , None );'
                left_entity_id = next_entity_id
        elif use_unit and not use_attr:
            if sample_relation == 0:
                world_model += ' transfer ( [agent{}] , None , [n] , [entity{}] , None , [unit{}] );'.format(next_agent_id, left_entity_id, left_entity_id)
            elif sample_relation == 1:
                next_entity_id += 1
                world_model += f' rate ( [agent{next_agent_id}] , [n] , [entity{next_entity_id}] , None , [unit{next_entity_id}] , [entity{left_entity_id}] , None , [unit{left_entity_id}] );'
                left_entity_id = next_entity_id
        elif use_attr:
            if sample_relation == 0:
                world_model += ' transfer ( [agent{}] , None , [n] , [entity{}] , [attr{}] , None );'.format(next_agent_id, left_entity_id, left_entity_id)
            elif sample_relation == 1:
                next_entity_id += 1
                world_model += f' rate ( [agent{next_agent_id}] , [n] , [entity{next_entity_id}] , [attr{next_entity_id}] , None , [entity{left_entity_id}] , [attr{left_entity_id}] , None );'
                left_entity_id = next_entity_id
    #generating question block
    if not use_unit and not use_attr:
        question = 'container ( [agent{}] , None , [entity{}] , None , None );'.format(next_agent_id, left_entity_id)
    elif use_unit and not use_attr:
        question = 'container ( [agent{}] , None , [entity{}] , None , [unit{}] );'.format(next_agent_id, left_entity_id, left_entity_id)
    elif use_attr:
        question = 'container ( [agent{}] , None , [entity{}] , [attr{}] , None );'.format(next_agent_id, left_entity_id, left_entity_id)
    return world_model, question

def save_linear_world(n):
    seed(624768914)
    out = ''
    for _ in range(n):
        world_model, question = generate_consistency_model()
        out = out + f'BODY: {world_model}\nQUESTIONS: {question}\n\n'
    with open('consistency_models_550.txt', 'w') as f:
        f.write(out)

if __name__ == '__main__':
    save_linear_world(550)
