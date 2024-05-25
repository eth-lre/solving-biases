import json
import openai
import time
from wrapt_timeout_decorator import *
from tqdm import tqdm
import random
import re

# Set up your OpenAI API credentials
api_key_file = 'data/openai_api_key.txt'
with open(api_key_file) as fp:
    organization_key, api_key = fp.readlines()
openai.organization = organization_key.replace('\n', '')
openai.api_key = api_key


def prompt_funct(problem, mode='regular'):
    conservative_prompt = f'Correct all grammatical mistakes that appear in the following math word problem: {problem}\n Fix any awkward or redundant phrasing. \
        Pay close attention to incorrect plural forms. Do NOT solve the problem. Do NOT compute any intermediate solutions. Do NOT make any changes to the numerical values or implied mathematical operations. \
        Only output the corrected math word problem and nothing else. Do NOT restate the original problem. Do NOT include "Corrected Version:" or any description of the task.\n'
    regular_prompt = f'Paraphrase the following math word problem: {problem}\n Fix any awkward or redundant phrasing. \
        Pay close attention to incorrect plural forms. Do NOT solve the problem. Do NOT make any changes to the numerical values or implied mathematical operations.\n'
    if mode == 'regular':
        prompt = regular_prompt
    else:
        prompt = conservative_prompt
    return prompt


# Function to make an API call to paraphrase a sentence
@timeout(25)
def paraphrase_problem(mwp):
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[{"role": "user", "content": prompt_funct(mwp, mode='conservative')}],
        max_tokens=256,
        temperature=0,
        top_p=1,
    )
    return response.choices[0]['message']['content']

def paraphrase_problems(templated_mwp_list, consistency=False, comp_trans=False, max_iter=None, carry=False):
    bad_mwps = []
    count = 0
    for mwp in tqdm(templated_mwp_list, desc='Paraphrasing problems'):
        paraphrased = []
        question = random.choice(mwp['questions'])
        idx = mwp['questions'].index(question)
        mwp['questions'] = [question]
        mwp['answers'] = [mwp['answers'][idx]]
        if not consistency:
            text = mwp['body'].strip() + ' ' + question
            paraphrased_problem = None
            while paraphrased_problem is None:
                paraphrased_problem = try_paraphrase(text)
            #check if comp_trans sentences match in 'more' 'fewer' word between template and paraphrase
            para_sentences = paraphrased_problem.split('. ')
            temp_sentences = text.split('. ')
            if comp_trans or carry:
                if len(para_sentences) == len(temp_sentences):
                    match = True
                    for i in range(len(para_sentences)):
                        if 'more' in para_sentences[i] and 'more' not in temp_sentences[i]:
                            match = False
                        elif ('fewer' in para_sentences[i] or 'less' in para_sentences[i]) and not ('fewer' in temp_sentences[i] or 'less' in temp_sentences[i]):
                            match = False
                    if match: paraphrased.append(paraphrased_problem)
                    else:
                        print('more/fewer mismatch')
                        paraphrased.append(None)
                else:
                    print('length mismatch')
                    paraphrased.append(None)
            else:
                if len(para_sentences) == len(temp_sentences):
                    paraphrased.append(paraphrased_problem)
                else:
                    print('length mismatch')
                    paraphrased.append(None)
        if consistency:
            consistent_text = mwp['body'][0].strip() + ' ' + question
            inconsistent_text = mwp['body'][1].strip() + ' ' + question
            consistent_paraphrased_problem = None
            inconsistent_paraphrased_problem = None
            template_len = len(consistent_text.split('. '))
            while consistent_paraphrased_problem is None:
                consistent_paraphrased_problem = try_paraphrase(consistent_text)
            while inconsistent_paraphrased_problem is None:
                inconsistent_paraphrased_problem = try_paraphrase(inconsistent_text)
            cons_idx = mwp['consistency index']
            res = consistent_paraphrased_problem.split('. ')
            inc_whole = inconsistent_paraphrased_problem.split('. ')
            #checking that consistent and inconsistent problems have same length, and that they both have same length as template
            if len(res) != len(inc_whole) or len(res) != template_len:
                bad_mwps.append(mwp)
                print('encountered index mismatch')
                continue
            inc_sentence = inc_whole[cons_idx]
            cons_sentence = res[cons_idx]
            res[cons_idx] = inc_sentence
            #checking that if 'fewer' in one then 'more' in the other and vice versa
            if ('fewer' in cons_sentence or 'less' in cons_sentence) and 'more' not in inc_sentence:
                bad_mwps.append(mwp)
                print('paraphrase more/fewer issue (fewer fewer)')
                continue
            elif 'more' in cons_sentence and not ('fewer' in inc_sentence or 'less' in inc_sentence):
                bad_mwps.append(mwp)
                print('paraphrase more/fewer issue (more more)')
                continue
            inconsistent_paraphrased_problem = '. '.join(res)
            paraphrased.append(consistent_paraphrased_problem)
            paraphrased.append(inconsistent_paraphrased_problem)
        mwp['paraphrased_list'] = paraphrased
        count += 1
        if max_iter is not None and count > max_iter:
            break
    for bad_mwp in bad_mwps:
        templated_mwp_list.remove(bad_mwp)
    return templated_mwp_list

def try_paraphrase(text):
    try:
        return paraphrase_problem(text)
    except:
        try_paraphrase(text)

