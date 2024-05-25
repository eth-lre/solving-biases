from random import choice, seed, randint
import random

def generate_linear_world_model(n):
	left_agent_id = 1
	left_entity_id = 1
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
	world_model = left
	for i in range(n):
		# TODO: add 'rate' relation (perhaps keep a current entity type variable, indicating whether 'left_entity_id' is a container type or element type)
		operation = choice(['transfer', 'add', 'times'])
		if operation in ('add', 'times'):
			negate = choice([True, False]) if operation == 'add' else False
			first_agent, second_agent = (left_agent_id, next_agent_id) if negate else (next_agent_id, left_agent_id)
			if not use_unit and not use_attr: 
				world_model += ' {} ( [agent{}] , [agent{}] , [n] , [entity{}] , None , None , [entity{}] , None , None );'.format(operation, first_agent, second_agent, left_entity_id, left_entity_id)
			elif use_unit: 
				world_model += ' {} ( [agent{}] , [agent{}] , [n] , [entity{}] , None , [unit{}] , [entity{}] , None , [unit{}] );'.format(operation, first_agent, second_agent, left_entity_id, left_entity_id, left_entity_id, left_entity_id)
			elif use_attr: 
				world_model += ' {} ( [agent{}] , [agent{}] , [n] , [entity{}] , [attr{}] , None , [entity{}] , [attr{}] , None );'.format(operation, first_agent, second_agent, left_entity_id, left_entity_id, left_entity_id, left_entity_id)
			left_agent_id = next_agent_id
			next_agent_id += 1
		elif operation == 'transfer':
			if not use_unit and not use_attr:
				world_model += ' transfer ( [agent{}] , None , [n] , [entity{}] , None , None );'.format(left_agent_id, left_entity_id)
			elif use_unit and not use_attr:
				world_model += ' transfer ( [agent{}] , None , [n] , [entity{}] , None , [unit{}] );'.format(left_agent_id, left_entity_id, left_entity_id)
			elif use_attr:
				world_model += ' transfer ( [agent{}] , None , [n] , [entity{}] , [attr{}] , None );'.format(left_agent_id, left_entity_id, left_entity_id)

	if not use_unit and not use_attr:
		question = 'container ( [agent{}] , None , [entity{}] , None , None );'.format(left_agent_id, left_entity_id)
	elif use_unit and not use_attr:
		question = 'container ( [agent{}] , None , [entity{}] , None , [unit{}] );'.format(left_agent_id, left_entity_id, left_entity_id)
	elif use_attr:
		question = 'container ( [agent{}] , None , [entity{}] , [attr{}] , None );'.format(left_agent_id, left_entity_id, left_entity_id)
	return world_model, question

# seed(624768914)
# for n in range(12):
# 	world_model, question = generate_linear_world_model(n)
# 	print('BODY: {}\nQUESTIONS: {}\n'.format(world_model, question))

def save_linear_world(n):
	seed(624768914)
	out = ''
	for _ in range(n):
		world_model, question = generate_linear_world_model(5)
		out = out + f'BODY: {world_model}\nQUESTIONS: {question}\n\n'
	with open('linear_world_models.txt', 'w') as f:
		f.write(out)

if __name__ == '__main__':
	save_linear_world(15)
