# Cognitive Biases in Language Models
This repository contains the code for the paper ["Do Language Models Exhibit the Same Cognitive Biases in Problem Solving as Human Learners?"](https://arxiv.org/pdf/2401.18070), presented at ICML 2024.

## Setup
To install the required packages, run:

``pip install -r requirements.txt``

## Data Generation

- Generate Uninstantiated World Models </br>
Run `generate_linear_world_model.py` to generate empty linear world models. `generate_consistency_model.py` generates pairs which differ only in consistency. `generate_dual_models.py` generates a comparison problem and a transfer problem both implying the same arithmetic computation. 

- Instantiate and Convert Problems to Natural Language </br>
Run `generate_data.py` to generate natural language word problem data sets from empty world models. `generate_comp.py` and `generate_trans.py` can be used to generate pairs of problems which share the same variable instantiations for comparison vs transfer experiments. `generate_carry.py` and `generate_nocarry.py` can be used to generate pairs of problems which are identical up to differences in variable quantities, where the problems generated by the former always contain carries. 

## Evaluation 

Run `python eval.py` to load a model, evaluate it, and store its preditions. The arguments are handeld using [Hydra](https://hydra.cc/):
- `test_type` indicates for which of the three biases considered in the paper the model should be test for (`consistency`, `comparison_vs_transfer`, or `carry`) 
- `model` the HuggingFace identifier of the model that should be tested
- `solution_mode` indicates how teh model should be prompted (`direct` or `cot`)
- `data_path` is the path to `.csv` file containing the problems generated for the corresponding `test_type`
- `hf_token_path` is the path to a `.txt` file containing a token to access gated HuggingFace models (e.g., LLaMA2)

The default configuration can be found in `conf/config_eval.yaml`. The script stores the predictions in `eval_out/[test_type]/[solution_mode]/[model_id]` and uploads the metrics on `wandb`. You can disable wandb sync by setting `wandb_mode=offline`.

## Citation

Please cite as:

```
@inproceedings{opedal2024language,
  title = {Do Language Models Exhibit the Same Cognitive Biases in Problem Solving as Human Learners?},
  author = {Opedal, Andreas and Stolfo, Alessandro and Shirakami, Haruki and Jiao, Ying and Cotterell, Ryan and Schölkopf, Bernhard and Saparov, Abulhair and Sachan, Mrinmaya},
  booktitle = {Forty-first International Conference on Machine Learning},
  month = july,
  year = {2024},
  url = {https://arxiv.org/abs/2401.18070},
}
```



