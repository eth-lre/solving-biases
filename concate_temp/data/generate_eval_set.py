import random 
from generate_linear_world_model import generate_linear_world_model

def generate_eval_set(empty_lf_path='empty_world_models.txt'):
    random.seed(12345)
    with open(empty_lf_path) as f:
        mws = [line for line in f.readlines()]
    num_gen = 50
    with open(empty_lf_path) as f:
         temp = f.read()
    temp = temp * 10
    for _ in range(num_gen):
        length = random.randint(3,6)
        world_model, question = generate_linear_world_model(length)
        temp = temp + f'BODY: {world_model}\nQUESTIONS: {question}\n\n'
    lines = temp.split('\n\n')
    lines = lines[:-1]
    random.shuffle(lines)
    out = ''
    for line in lines:
        out = out + line + '\n\n'
    with open('evaluation_set_100.txt', 'w') as f:
        f.write(out)

if __name__ == '__main__':
    generate_eval_set()
