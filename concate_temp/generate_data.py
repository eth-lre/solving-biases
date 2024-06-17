from instantiate_lf import instantiate_logical_form, instantiate_dual_form
from concate_temp import load_temp_dict, load_world_model, generate_mwp
from paraphrase import paraphrase_problems
import json
import pickle

if __name__ == "__main__":
    # Parameters
    comp_lf_path = 'data/linear_comp_models.txt'
    trans_lf_path = 'data/linear_trans_models.txt'
    empty_lf_path = 'data/consistency_models_550.txt'
    destination_path = 'data/cons_init.txt' 
    dual_destination_path = 'data/trans_init.txt' 
    final_text_path = 'data/consistency.jsonl'
    final_text_path_comp = 'data/comp.jsonl'
    final_text_path_trans = 'data/trans.jsonl'
    template_file = 'data/temp_pair_v3.csv'
    n_instances = 1


    instantiated_world_models = instantiate_logical_form(empty_lf_path, destination_path, n_instances)
    temp_dict = load_temp_dict(template_file)
    templated_mwp_list = generate_mwp(instantiated_world_models, temp_dict, consistency=True)
    final_mwp_list = paraphrase_problems(templated_mwp_list, consistency=True)

    with open(final_text_path, 'w') as f:
        for mwp_dict in final_mwp_list:
            json.dump(mwp_dict, f)
            f.write('\n')


