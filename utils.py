import re

'''
Some helper functions to clean up errors in text from t5 output.
'''

def rm_space_b4_punc(text):
    # remove added whitespace b4 punct chars.
    pattern = r'\s+(?=[,.!?;:])'

    return re.sub(pattern, '', text)

def correct_corrupted(original, corrupted):
    # here we realign corrupted text span with original with basic bigram matching

    # get bigrams from the original string
    words = original.split()
    bigrams = {words[i] + words[i + 1]: words[i] + ' ' + words[i + 1] for i in range(len(words) - 1)}

    # Split the corrupted string into tokens
    corrupted_tokens = corrupted.split()

    # Check each token in the corrupted string
    corrected_tokens = []
    for token in corrupted_tokens:
        corrected_tokens.append(bigrams.get(token, token))

    return ' '.join(corrected_tokens)

def preprocess(text):
    text = text.replace('[', '(')
    text = text.replace(']', ')')
    return text
