import pandas as pd
import random
import re
import pickle

def create_csv_cons(path='consistency.jsonl'):
    json_examples = pd.read_json(path_or_buf=path, lines=True)
    for i in range(len(json_examples)):
        json_examples.iloc[i]['questions'] = json_examples.iloc[i]['questions'][0]
        json_examples.iloc[i]['answers'] = json_examples.iloc[i]['answers'][0]
    body_examples = json_examples.body.apply(pd.Series)
    paraphrased_examples = json_examples.paraphrased_list.apply(pd.Series)
    questions = json_examples['questions'].apply(pd.Series)
    answers = json_examples['answers'].apply(pd.Series)
    result = pd.concat([questions, body_examples, paraphrased_examples, answers], axis=1)
    result.columns = ['question', 'consistent body', 'inconsistent body', 'consistent paraphrased', 'inconsistent paraphrased', 'answer']
    result = result.iloc[:500]
    result.to_csv('cons.csv', index=False)

def create_csv_dual(path1='comp_v2.jsonl', path2='trans_v2.jsonl'):
    json_examples_comp = pd.read_json(path_or_buf=path1, lines=True)
    body = json_examples_comp['body'].apply(pd.Series)
    para = json_examples_comp['paraphrased_list'].apply(pd.Series)
    q = json_examples_comp['questions'].apply(pd.Series)
    a = json_examples_comp['answers'].apply(pd.Series)
    json_examples_trans = pd.read_json(path_or_buf=path2, lines=True)
    body_trans = json_examples_trans['body'].apply(pd.Series)
    para_trans = json_examples_trans['paraphrased_list'].apply(pd.Series)
    q_trans = json_examples_trans['questions'].apply(pd.Series)
    a_trans = json_examples_trans['answers'].apply(pd.Series)
    result = pd.concat([q, q_trans, body, body_trans, para, para_trans, a], axis=1)
    result.columns = ['question comparison', 'question transition', 'body comparison', 'body transition', 'paraphrase comparison', 'paraphrase transition', 'answer']
    result = result.dropna(axis=0)
    result = filter_output(result)
    result = result.iloc[:500]
    result.to_csv('comp_trans.csv', index=False)

def take_last(paraphrased):
    p_list = paraphrased.split('. ')
    return p_list[-1]

def replace_last(replacee, para_last):
    print(replacee.index)
    return None

def replace(match, carry_prob_quantities):
    replacement = carry_prob_quantities.pop(0)
    return replacement

def create_csv_carry(path1='nocarry.jsonl', path2='carry.jsonl'):
    json_examples_comp = pd.read_json(path_or_buf=path1, lines=True)
    body = json_examples_comp['body'].apply(pd.Series)
    para = json_examples_comp['paraphrased_list'].apply(pd.Series)
    q = json_examples_comp['questions'].apply(pd.Series)
    a = json_examples_comp['answers'].apply(pd.Series)
    json_examples_trans = pd.read_json(path_or_buf=path2, lines=True)
    body_trans = json_examples_trans['body'].apply(pd.Series)
    para_trans = json_examples_trans['paraphrased_list'].apply(pd.Series)
    q_trans = json_examples_trans['questions'].apply(pd.Series)
    a_trans = json_examples_trans['answers'].apply(pd.Series)
    add_sub_both = None
    with open('../add_sub_both.pkl', 'rb') as f:
        add_sub_both = pickle.load(f)
    with open('../num_carries.pkl', 'rb') as f:
        num_carries = pickle.load(f)
    add_sub_both = pd.DataFrame(add_sub_both)
    num_carries = pd.DataFrame(num_carries)
    result = pd.concat([q, body, body_trans, para, para_trans, a, a_trans, add_sub_both, num_carries], axis=1)
    result.columns = ['question', 'body no carry', 'body carry', 'paraphrase no carry', 'paraphrase carry', 'answer no carry', 'answer carry', 'Carry Operation', 'Num. Carries']
    result = result.dropna(axis=0)
    result = filter_output_carry(result)
    # replacing question to be the same for both versions
    ##########################################################
    # para_last = result.iloc[:, 3].apply(take_last)
    # replaced_p_carry = result.iloc[:, 4]
    # for i in range(len(result.iloc[:, 4])):
    #     replaced = '. '.join(result.iloc[i, 4].split('. ')[:-1]) + '. '
    #     replaced = replaced + para_last.iloc[i]
    #     replaced_p_carry.iloc[i] = replaced
    # result['paraphrase carry'] = replaced_p_carry
    ##########################################################
    carry_problems = []
    len_df = len(result.iloc[:, 3])
    i = 0
    while i < len_df:
        carry_prob_quantities = re.findall(r'\d+', result.iloc[i, 4])
        no_carry_quantities = re.findall(r'\d+', result.iloc[i, 3])
        if len(carry_prob_quantities) != len(no_carry_quantities):
            result = result.drop(result.iloc[i,:].name, axis=0)
            len_df-=1
            continue
        original_problem = result.iloc[i, 3]
        substituted_problem = re.sub(r'\d+', lambda x : replace(x, carry_prob_quantities), original_problem)
        carry_problems.append(substituted_problem)
        i+=1
    result['paraphrase carry'] = carry_problems
    result = result.iloc[:500]
    result.to_csv('nocarry_carry.csv', index=False)

def filter_output(df):
    df = df[(~df['paraphrase comparison'].str.contains('\\n') & ~df['paraphrase transition'].str.contains('\\n'))]
    return df

def filter_output_carry(df):
    df = df[(~df['paraphrase no carry'].str.contains('\\n') & ~df['paraphrase carry'].str.contains('\\n'))]
    return df
    
if __name__ == '__main__':
    create_csv_carry()