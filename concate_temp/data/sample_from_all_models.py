
from random import sample 
def sample_models():
    cons_path = "consistency_models_550.txt"
    comp_path = "linear_comp_models.txt"
    trans_path = "linear_trans_models.txt"
    with open(cons_path) as f:
        cons_text = f.read()
        cons_models = cons_text.split('\n\n')[:-1]
    with open(comp_path) as f:
        comp_text = f.read()
        comp_models = comp_text.split('\n\n')[:-1]
    with open(trans_path) as f:
        trans_text = f.read()
        trans_models = trans_text.split('\n\n')[:-1]
    all_models = cons_models + comp_models + trans_models
    all_models_addition = []
    for model in all_models:
        if 'transfer' in model or 'add' in model:
            all_models_addition.append(model)
    sampled_models = sample(all_models_addition, 620)
    out =  ''
    for model in sampled_models:
        out += model + '\n\n'
    with open('sampled_models.txt', 'w') as f:
        f.write(out)
if __name__ == '__main__':
    sample_models()