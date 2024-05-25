import re


def is_int(x):
    try:
        int(x)
        return True
    except:
        return False


def load_txt(path):
    with open(path, 'r') as f:
        lines = f.read().splitlines()

    data = []
    for i, line in enumerate(lines):
        # TODO use json and store result
        if i % 3 == 1:
            data.append(line.strip())
    return data


def get_lf_exemplars(problem_type):
    if problem_type == 'add':
        path = './from_dataset_add.txt'

    with open(path, 'r') as f:
        lines = f.read().splitlines()

    lfs = []
    probs = []
    for line in lines:
        if line.startswith('Logical form:'):
            lfs.append(line.strip())
        elif line.startswith('Math problem:'):
            probs.append(line.strip())

    exemplars = ''

    for lf, prob in zip(lfs, probs):
        exemplars += prob + '\n' + lf + '\n\n'

    return exemplars
