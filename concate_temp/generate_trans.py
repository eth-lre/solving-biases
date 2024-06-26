from instantiate_lf import instantiate_logical_form, instantiate_dual_form
from concate_temp import load_temp_dict, load_world_model, generate_mwp
from paraphrase import paraphrase_problems
import json
import pickle

if __name__ == "__main__":
    # Parameters
    empty_lf_path = 'data/linear_comp_models.txt'
    dual_lf_path = 'data/linear_trans_models.txt'
    destination_path = 'data/comp_init.txt' 
    dual_destination_path = 'data/trans_init.txt' 
    final_text_path_trans = 'data/trans_v2.jsonl'
    template_file = 'data/temp_pair_comp_trans.csv'
    n_instances = 1

    instantiated_comp, instantiated_trans = instantiate_dual_form(empty_lf_path, dual_lf_path, destination_path, dual_destination_path, n_instances)
    temp_dict = load_temp_dict(template_file)
    templated_mwp_comp = generate_mwp(instantiated_comp, temp_dict, consistency=False, dual=True, pair_cons=False)
    templated_mwp_trans = generate_mwp(instantiated_trans, temp_dict, consistency=False, dual=True, pair_cons=False)
    final_mwp_trans = paraphrase_problems(templated_mwp_trans, consistency=False)

    with open(final_text_path_trans, 'w') as f:
        for mwp_dict in final_mwp_trans:
            json.dump(mwp_dict, f)
            f.write('\n')

