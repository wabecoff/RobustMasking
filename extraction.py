import re

'''
Functions for extracting the content that was masked out by the t5 model.
'''

def get_substrings_between_patterns(text, pattern):
    # Find all matches for the pattern in the lowercase text
    matches = list(re.finditer(pattern, text))

    # List to hold the substrings
    substrings = []

    # Get the substring before the first match
    start = 0
    end = matches[0].start() if matches else len(text)
    substrings.append(text[start:end])

    # Extract substrings between matches
    for i in range(len(matches) - 1):
        start = matches[i].end()
        end = matches[i + 1].start()
        substrings.append(text[start:end])

    # Get the substring after the last match
    if matches and matches[-1].end() <= len(text):
        start = matches[-1].end()
        end = len(text)
        substrings.append(text[start:end])

    return substrings

def find_first_capture(input_string, pattern):
    # Use re.finditer to find all matches of the pattern in the input_string
    matches = re.finditer(pattern, input_string)

    # Initialize a list to store the captured groups from each match
    captured_groups = []

    # Iterate through the matches and extract first
    for match in matches:
        captured_groups.append(match[0])

    return captured_groups

def find_middle_substring(text, substr1, substr2):
    # Check if both substrings are empty
    if substr1 == "" and substr2 == "":
        return text, ''

    # Find the end of the first substring, or start from the beginning if the first substring is empty
    start_index = text.find(substr1) + len(substr1) if substr1 else 0

    # Find the start of the second substring, or go to the end if the second substring is empty
    end_index = text.find(substr2, start_index) if substr2 else len(text)

    # If substr2 has a length of 2 or more and it was not found, try searching for substr2[1:]
    if len(substr2) >= 2 and end_index == -1:
        end_index = text.find(substr2[1:], start_index)

    # Extract the substring between substr1 and substr2
    middle_substring = text[start_index:end_index] if start_index != -1 and end_index != -1 else ""

    # Extract the rest of the string starting from substr2
    post_substr2_text = text[end_index:] if end_index != -1 else ""

    return middle_substring, post_substr2_text

def extract_masked_info(input_text, masked_text):
    pairs = []

    # Regex for our masked tokens
    pattern = r"(\[\[(FULL_NAME|FIRST_NAME|LAST_NAME|DOB)_?[0-9|X]{0,3}\]\])"

    # Find the content between masks as anchor for masked content
    substrs = get_substrings_between_patterns(masked_text, pattern)
    masks = find_first_capture(masked_text, pattern)

    #deep copy the string
    input_left = input_text[:]

    # Use substrings from above to get original masked content
    for i in range(len(substrs)-1):
        substr1, substr2 = substrs[i], substrs[i+1]

        #extract out content and shorten front of string accordingly
        content, input_left = find_middle_substring(input_left, substr1, substr2)

        pairs.append((masks[i], content))

    return pairs

def replace_masks(text,  replacements):
    pattern = r"(\[\[(FULL_NAME|FIRST_NAME|LAST_NAME|DOB)_?[0-9|X]{0,3}\]\])"
    # Create an iterator from the list of replacement strings
    replacement_iter = iter(replacements)

    # Function to get the next replacement string
    def get_replacement(match):
        return next(replacement_iter)

    # Use re.sub with a function that fetches the next replacement
    return re.sub(pattern, get_replacement, text)

# Function allows us to recover original text given masked text + mask-content pairs
def recover(masked_text, content_pairs):
    new_text = masked_text

    #replace masks with content iteratively
    for pair in content_pairs:
        mask, content = pair[0], pair[1]
        new_text = new_text.replace(mask, content, 1)

    return new_text
