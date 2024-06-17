from instantiate_lf import instantiate_logical_form, instantiate_dual_form, instantiate_nocarry_carry
from concate_temp import load_temp_dict, load_world_model, generate_mwp
from paraphrase import paraphrase_problems
import json
import pickle

if __name__ == "__main__":
    # Parameters
    empty_lf_path = 'data/single_comp_models.txt'
    destination_path_nc = 'data/sample_init_nc.txt' 
    destination_path_c = 'data/sample_init_c.txt'
    final_text_path_c = 'data/carry.jsonl'
    template_file = 'data/temp_pair_comp_trans.csv'
    n_instances = 1

    instantiated_nc, instantiated_c, add_sub_both, num_carries = instantiate_nocarry_carry(empty_lf_path, destination_path_nc, destination_path_c, n_instances)
    temp_dict = load_temp_dict(template_file)

    with open('add_sub_both.pkl', 'wb') as f:
        pickle.dump(add_sub_both, f)
    with open('num_carries.pkl', 'wb') as f:
        pickle.dump(num_carries, f)

    templated_mwp = generate_mwp(instantiated_c, temp_dict)
    final_mwp_c = paraphrase_problems(templated_mwp, carry=True)

    with open(final_text_path_c, 'w') as f:
        for mwp_dict in final_mwp_c:
            json.dump(mwp_dict, f)
            f.write('\n')

 
