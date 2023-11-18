import re

def rm_space_b4_punc(text):
    # Define a regex pattern to match whitespace before punctuation
    pattern = r'\s+(?=[,.!?;:])'

    # Replace matched patterns with an empty string
    return re.sub(pattern, '', text)

def correct_corrupted(original, corrupted):
    # Create bigrams from the original string
    words = original.split()
    bigrams = {words[i] + words[i + 1]: words[i] + ' ' + words[i + 1] for i in range(len(words) - 1)}

    # Split the corrupted string into tokens
    corrupted_tokens = corrupted.split()

    # Check each token in the corrupted string
    corrected_tokens = []
    for token in corrupted_tokens:
        # Replace with bigram if match found, otherwise keep the token as is
        corrected_tokens.append(bigrams.get(token, token))

    # Join the tokens back into a string
    return ' '.join(corrected_tokens)

def preprocess(text):
    text = text.replace('[', '(')
    text = text.replace(']', ')')
    return text