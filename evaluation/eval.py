# %%
import os
import hydra
import pandas as pd
import json
import wandb
import tqdm
import torch
import random
import re
from scipy.stats import ttest_rel
from omegaconf import DictConfig, OmegaConf
from transformers import LlamaForCausalLM, LlamaTokenizer, AutoTokenizer, AutoModelForCausalLM
from wrapt_timeout_decorator import *
from openai import OpenAI
import time


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    
# Function to make an API call
@timeout(25)
def prompt_api_model(input_text, model='gpt-3.5-turbo', max_tokens=256, temperature=0, top_p=1, output_only_number=False):
    messages = [{"role": "user", "content": input_text}]
    if output_only_number:
        messages = [{"role": "system", "content": "Answer the following questions with a single numerical value, do not output any additional text."}] + messages
    while 1:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            break
        except Exception as e:
            print(f'(probably) OpenAI error : {e}\n retrying...')
            time.sleep(5)
            continue
    return response.choices[0].message.content


def direct_inference(model, tokenizer, problem, device, use_qa_pattern=True):
    """
    standard direct inference, 0-shot
    """
    if use_qa_pattern:
        eval_prompt = 'Q: ' + problem + "\nA: The answer (arabic numerals) is "
    else:
        eval_prompt = problem + "\nThe answer (arabic numerals) is "

    if type(model) == str:
        # we are using a an openai model through the APIs
        ask_to_output_only_number = False
        if 'gpt-4' in model:
            ask_to_output_only_number = True
        decoded_output = prompt_api_model(eval_prompt, model=model, max_tokens=16, temperature=0, top_p=1, output_only_number=ask_to_output_only_number)
    else:
        model_input = tokenizer(eval_prompt, return_tensors="pt").to(device)
        with torch.no_grad():
            len_prompt = model_input['input_ids'].shape[1]
            output = model.generate(**model_input, max_new_tokens=16, pad_token_id=tokenizer.eos_token_id, do_sample=False)[0,len_prompt:]
            decoded_output = tokenizer.decode(output, skip_special_tokens=True)
    
    decoded_output = decoded_output.replace(',', '') # models sometimes output 1,000 instead of 1000
    decoded_output = decoded_output.replace('.', '') # remove for experiments on data from hegarty, 1995, which use results like $3.45
    return decoded_output

def cot_inference(model, tokenizer, problem, device, use_qa_pattern=True):
    """
    zero-shot chain-of-thought inference using the two-stage prompt method proposed by Kojima et al. (2022)
    """
    if use_qa_pattern:
        eval_prompt = "Q: " + problem + "\nA: Let's think step by step. " 
    else:
        eval_prompt = problem + "\nLet's think step by step. " 

    if type(model) == str:
        # we are using a an openai model through the APIs
        decoded_output = prompt_api_model(eval_prompt, model=model, max_tokens=256, temperature=0, top_p=1)
    else:
        model_input = tokenizer(eval_prompt, return_tensors="pt").to(device)
        with torch.no_grad():
            len_prompt_pre_cot = model_input['input_ids'].shape[1]
            output = model.generate(**model_input, max_new_tokens=256, do_sample=False)[0,:]
            decoded_output = tokenizer.decode(output, skip_special_tokens=True)

    eval_prompt2 = decoded_output + "\nTherefore, the answer (arabic numerals) is "

    if type(model) == str:
        decoded_output_without_cot = prompt_api_model(eval_prompt2, model=model, max_tokens=16, temperature=0, top_p=1)
        decoded_output_with_cot = eval_prompt2 + decoded_output_without_cot
    else:
        model_input = tokenizer(eval_prompt2, return_tensors="pt").to(device)
        with torch.no_grad():
            len_prompt = model_input['input_ids'].shape[1]
            output = model.generate(**model_input, max_new_tokens=16, do_sample=False)
            decoded_output_with_cot = tokenizer.decode(output[0,len_prompt_pre_cot:], skip_special_tokens=True)
            decoded_output_with_cot = decoded_output_with_cot.replace(',', '')
            decoded_output_without_cot = tokenizer.decode(output[0,len_prompt:], skip_special_tokens=True)
            decoded_output_without_cot = decoded_output_without_cot.replace(',', '')
            decoded_output_without_cot = decoded_output_without_cot.replace('.', '') # remove for experiments on data from hegarty, 1995, which use results like $3.45
    
    return decoded_output_with_cot, decoded_output_without_cot


def child_persona_inference(model, tokenizer, problem, device, use_qa_pattern=True):
    """
    zero-shot chain-of-thought inference using the two-stage prompt method proposed by Kojima et al. (2022)
    """
    if use_qa_pattern:
        eval_prompt = "Q: " + problem + "\nA: Let's think step by step as a grade-school child would. " 
    else:
        eval_prompt = problem + "\nLet's think step by step as a grade-school child would. " 

    model_input = tokenizer(eval_prompt, return_tensors="pt").to(device)
    with torch.no_grad():
        len_prompt_pre_cot = model_input['input_ids'].shape[1]
        output = model.generate(**model_input, max_new_tokens=256, do_sample=False)[0,:]
        decoded_output = tokenizer.decode(output, skip_special_tokens=True)
    eval_prompt2 = decoded_output + "\nTherefore, the answer (arabic numerals) is "

    model_input = tokenizer(eval_prompt2, return_tensors="pt").to(device)
    with torch.no_grad():
        len_prompt = model_input['input_ids'].shape[1]
        output = model.generate(**model_input, max_new_tokens=16, do_sample=False)
        decoded_output_with_cot = tokenizer.decode(output[0,len_prompt_pre_cot:], skip_special_tokens=True)
        decoded_output_with_cot = decoded_output_with_cot.replace(',', '')
        decoded_output_without_cot = tokenizer.decode(output[0,len_prompt:], skip_special_tokens=True)
        decoded_output_without_cot = decoded_output_without_cot.replace(',', '')
    
    return decoded_output_with_cot, decoded_output_without_cot


@hydra.main(config_path='../conf', config_name='config_eval')
def run_experiment(args: DictConfig):
    print(OmegaConf.to_yaml(args))
    os.chdir(args.project_dir)
    # initialize logging
    log_directory = args.output_dir
    log_directory += f'/test_type_{args.test_type}'
    log_directory += f'/solution_mode_{args.solution_mode}'
    if 'llama' in args.model.lower():
        model_str = args.model.split("/")[-1]
    else:
        model_str = args.model
    log_directory += f'/{model_str}'
    print(f'log_directory: {log_directory}')
    os.makedirs(log_directory, exist_ok=True)
    wandb_name = f'{model_str}'
    wandb_name += f' -t {args.test_type}'
    wandb_name += f' -m {args.solution_mode}'
    wandb.init(project='llm-mwp-bias', name=wandb_name, notes='', dir=log_directory,
               settings=wandb.Settings(start_method='thread'), mode=args.wandb_mode)
    args_to_log = dict(args)
    args_to_log['out_dir'] = log_directory
    random.seed(args.seed)
    torch.manual_seed(args.seed)
    wandb.config.update(args_to_log)
    del args_to_log

    # Initialize Model and Tokenizer
    model_id = args.model
    if 'gpt-3.5' not in model_id and 'gpt-4' not in model_id:
        with open(args.hf_token_path, 'r') as f:
            hf_token = f.read()
        tokenizer = AutoTokenizer.from_pretrained(model_id, cache_dir=args.transformers_cache_dir, token=hf_token)
        model = AutoModelForCausalLM.from_pretrained(model_id, device_map='auto', cache_dir=args.transformers_cache_dir, token=hf_token)
        #model = AutoModelForCausalLM.from_pretrained(model_id, cache_dir=args.transformers_cache_dir).to(args.device)
        model.eval()
    else:
        # we are using a an openai model through the APIs
        # Set up your OpenAI API credentials
        api_key_file = 'data/openai_keys.txt'
        with open(api_key_file) as fp:
            organization_key, api_key = fp.readlines()
        global client
        client = OpenAI(
            organization = organization_key.replace('\n', ''),
            api_key = api_key
        )


        model = model_id
        tokenizer = None

    #use qa pattern in prompt if not using instruction-tuned models
    use_qa_pattern = ('instruct' not in model_id) and ('chat' not in model_id)

    # load Data
    data = pd.read_csv(args.data_path, sep=",")

    # get the predictions
    results_df = get_predictions(data, model, tokenizer, args, use_qa_pattern)
    wandb.run.summary.update({'accuracy_A': results_df['accuracy_A'].mean()})
    wandb.run.summary.update({'accuracy_B': results_df['accuracy_B'].mean()})
    wandb.run.summary.update({'pred_change': results_df['pred_change'].mean()})

    # store number of predictions actually extracted
    A_n_pred_extracted = len(results_df[results_df['pred_A'] != "-1"]) / len(results_df)
    B_n_pred_extracted = len(results_df[results_df['pred_B'] != "-1"]) / len(results_df)
    wandb.summary.update({'A_pred_extracted': A_n_pred_extracted})
    wandb.summary.update({'B_pred_extracted': B_n_pred_extracted})

    pvalue = ttest_rel(results_df['accuracy_A'].values, results_df['accuracy_B'].values).pvalue
    wandb.run.summary.update({'pvalue_ttest': pvalue})

    # store results
    fname = f'results'
    out_path = os.path.join(log_directory, fname + ".feather")
    print('out_path: ', out_path)
    results_df.to_feather(out_path)
    return results_df

# %%
def get_predictions(data, model, tokenizer, args, use_qa_pattern):
    results = []
    if args.dry_run:
        data = data.head(5)
    progress_bar = tqdm.tqdm(total=len(data))
    for idx, r in data.iterrows():
        if args.test_type.startswith('consistency'):
            A_paraphrased = r['consistent paraphrased']
            B_paraphrased = r['inconsistent paraphrased']
        elif args.test_type == 'comparison_vs_transfer':
            A_paraphrased = r['paraphrase comparison']
            B_paraphrased = r['paraphrase transition']
        elif args.test_type == 'carry':
            A_paraphrased = r['paraphrase carry']
            B_paraphrased = r['paraphrase no carry']
        else:
            raise ValueError(f'Unknown test type: {args.test_type}')
        answer = int(r['answer'])

        if args.solution_mode == 'cot':
            out1, out1_without_cot = cot_inference(model, tokenizer, A_paraphrased, args.device, use_qa_pattern)
            out2, out2_without_cot = cot_inference(model, tokenizer, B_paraphrased, args.device, use_qa_pattern)
            # regex match the first number in the output
            match  = re.search(r'\d+', out1_without_cot)
            pred1  = match.group() if match else "-1"
            match  = re.search(r'\d+', out2_without_cot)
            pred2  = match.group() if match else "-1"
        elif args.solution_mode == 'child_persona':
            out1, out1_without_cot = child_persona_inference(model, tokenizer, A_paraphrased, args.device, use_qa_pattern)
            out2, out2_without_cot = child_persona_inference(model, tokenizer, B_paraphrased, args.device, use_qa_pattern)
            # regex match the first number in the output
            match  = re.search(r'\d+', out1_without_cot)
            pred1  = match.group() if match else "-1"
            match  = re.search(r'\d+', out2_without_cot)
            pred2  = match.group() if match else "-1"
        elif args.solution_mode == 'direct':
            out1 = direct_inference(model, tokenizer, A_paraphrased, args.device, use_qa_pattern)
            out2 = direct_inference(model, tokenizer, B_paraphrased, args.device, use_qa_pattern)
            # regex match the first number in the output
            match  = re.search(r'\d+', out1)
            pred1  = match.group() if match else "-1"
            match  = re.search(r'\d+', out2)
            pred2  = match.group() if match else "-1"
        else:
            raise ValueError(f'Unknown solution mode: {args.solution_mode}')
        
        accuracy1 = int(int(pred1) == answer) if is_int(pred1) else 0 
        accuracy2 = int(int(pred2) == answer) if is_int(pred2) else 0

        # store results
        result = {}
        result.update(r)
        result['pred_A'] = pred1
        result['pred_B'] = pred2
        result['accuracy_A'] = accuracy1
        result['accuracy_B'] = accuracy2
        result['output_A'] = out1
        result['output_B'] = out2
        result['pred_change'] = result['pred_A'] != result['pred_B']
        results.append(result)
        progress_bar.update(1)

    results_df = pd.DataFrame(results)
    return results_df

# %%

if __name__ == '__main__':
    run_experiment()

# %%
