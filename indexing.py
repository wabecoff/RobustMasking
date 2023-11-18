import re
import extraction as ex

'''
Functions for numbering the mask tokens for names. 
'''

#Implementation of Levenshtein edit distance, courtesy of Chatgpt
def edit_distance(str1, str2):
    # Convert both strings to lower case to ignore case differences
    str1, str2 = str1.lower(), str2.lower()

    # Create a table to store results of subproblems
    dp = [[0 for x in range(len(str2) + 1)] for x in range(len(str1) + 1)]

    # Fill dp[][] in bottom up manner
    for i in range(len(str1) + 1):
        for j in range(len(str2) + 1):

            # If first string is empty, only option is to insert all characters of second string
            if i == 0:
                dp[i][j] = j

            # If second string is empty, only option is to remove all characters of first string
            elif j == 0:
                dp[i][j] = i

            # If last characters are the same, ignore last character and recur for remaining string
            elif str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]

            # If last character is different, consider all possibilities and find minimum
            else:
                dp[i][j] = 1 + min(dp[i][j - 1],        # Insert
                                   dp[i - 1][j],        # Remove
                                   dp[i - 1][j - 1])    # Replace

    return dp[len(str1)][len(str2)]

'''
Name class is used to decide if mask tokens for names have the same referent.
The main functionality is 'fill' and 'is_same'.  We use 'fill' to save as much
information as possible when storing a name, so if we only have the last name
for a name, but now have the first name and know it is from
'''
class Name:
    def __init__(self):
        self.first_name = None
        self.last_name = None
        self.full_name = None
        self.middle_name = None
        self.variants = []
        self.index = None


    def str_compare(self, s1, s2):
        if s1 == s2:
            return 1
        elif edit_distance(s1, s2) < 2:
            return 0.5
        else:
            return 0

    # Reasonably determine if a string is the same name as our current name object.
    def is_same(self, s, category):
        # want to compare with lower case for more generous string matching.
        s = s.lower()
        target = None

        if category == 'first':
            if self.first_name == None:
                return 0
            target = self.first_name.lower()

            return self.str_compare(s, target)

        if category == 'last':
            if self.last_name == None:
                return 0
            target = self.last_name.lower()

            return self.str_compare(s, target)

        if category == 'full':
            # for full names, we create a new name object from the string
            test_name = Name()
            test_name.fill(s, category)

            if test_name.first_name:
                first = self.is_same(test_name.first_name, 'first')
            else:
                first = -1

            if test_name.last_name:
                last = self.is_same(test_name.last_name, 'last')
            else:
                last = -1

            # if only first or last name found, use the result from the other one
            if last == -1:
                return first
            if first == -1:
                return  last

            if (first == 0 and self.first_name != None) or (last == 0 and self.last_name != None):
                return 0
            else:
                return (first + last) / 2

    # Percolate information from first name last name to full name, and vice versa.
    def complete(self):
        if self.first_name != None and self.last_name != None:
            if self.full_name == None:
                self.full_name = self.first_name + ' ' + self.last_name

            elif len(self.full_name) < len(self.first_name + ' ' + self.last_name):
                self.full_name = self.first_name + ' ' + self.last_name
                return

        elif self.first_name != None:
            self.full_name = self.first_name

        elif self.last_name != None:
            self.full_name = self.last_name

    def fill(self, s, category):
        # Split the input string into tokens
        tokens = s.split()

        if category == 'full':
            # Use the first token as the first name
            if self.first_name == None:
                self.first_name = tokens[0]
            # Use longer form of name when possible
            elif len(tokens[0]) > len(self.first_name):
                self.first_name = tokens[0]


            # Determine the last name
            if len(tokens) > 1:
                last_name_tokens = tokens[1:]

                if len(last_name_tokens) > 1:
                    # Check if the second to last token is short (<= 3 characters)
                    # This is to catch names like 'de Vries' or 'El Ramin'
                    if len(last_name_tokens[-2]) <= 3 and len(last_name_tokens) > 1:
                        last_name_tokens[-2] += " " + last_name_tokens[-1]
                        last_name = " ".join(last_name_tokens[:-1])
                    else:
                        last_name = last_name_tokens[-1]

                else:
                    last_name = last_name_tokens[-1]

                if self.last_name == None and last_name_tokens[0] != "":

                    self.last_name = last_name_tokens[0]

                # Use longer form of name when possible
                elif self.last_name != None and len(last_name) > len(self.last_name):
                    self.last_name = last_name

        elif category == 'first':

            if self.first_name == None:
                self.first_name = s
            # Use longer form of name when possible
            elif len(s) > len(self.first_name):
                self.first_name = s

        elif category == 'last':

            if self.last_name == None:
                self.last_name = s
            # Use longer form of name when possible
            elif len(s) > len(self.last_name):
                self.last_name = s

        else:
            raise ValueError("Invalid category. Use 'full', 'first', or 'last'.")

        # if necessary, move first name, last name to full name and vice versa.
        self.complete()

        return str(self.first_name) + ' ' + str(self.last_name)

# Extract the type from the mask string
def mask_type(mask):
    if "FULL" in mask: return 'full'
    if "DOB" in mask: return 'dob'
    if "FIRST" in mask: return 'first'
    if "LAST" in mask: return 'last'

# Basic function to swap in a new number for our mask string.
def change_index(mask, ind):
    pattern = r'\d|X'
    res = re.sub(pattern, str(ind), mask, count=1)
    return res

'''
Rectify fixes the numbering for our mask tokens.  We check the indexing on our
mask tokens by creating Name objects for unique names.
'''
def rectify(mask_pairs):
    max_ind = 1
    names = []

    # we need to pass over our list twice. Once to initialize all the names,
    # the second time to finish fixing up the numbering.
    for _ in range(2):

        for i in range(len(mask_pairs)):

            mask, content = mask_pairs[i]
            cur_type = mask_type(mask)

            # date of birth not numbered
            if cur_type == 'dob': continue

            should_add = 1

            # use correct existing index if we've seen it before
            for name in names:
                if name.is_same(content, cur_type) > 0:
                    new_mask = change_index(mask, name.index)
                    mask_pairs[i] = (new_mask, content)
                    name.fill(content, cur_type)
                    should_add = 0
                    break

            # if not create a new name object with the next index
            if should_add == 1:
                new_name = Name()
                new_name.fill(content, cur_type)
                new_name.index = max_ind
                max_ind += 1
                names.append(new_name)

    return mask_pairs

'''
Takes in the input to the t5 and the output from the t5.
Fixes the numbering on the t5 and outputs pairs of [(mask_token, content),...]
'''
def fix_masks(input, masked):
    # get pairs of masked mask tokens and masked content.
    p = ex.extract_masked_info(input, masked)
    # fix indexes of on mask tokens using content referents.
    p = indexing.rectify(p)
    replacements = [pair[0] for pair in p]
    # move fixed mask tokens back into masked text span
    masked = ex.replace_masks(masked, replacements)
    return masked, p

def split_string(string, max_length):
    # Define the regular expression pattern for splitting
    # This pattern will look for punctuation, newline, or space
    pattern = r'([,.!?;:\n]|\s)'

    # Split the string based on the defined pattern
    words = re.split(pattern, string)

    # Reconstruct the substrings with the split characters
    substrings = []
    current_substring = ''
    for word in words:
        if len(current_substring + word) < max_length:
            current_substring += word
        else:
            if current_substring:
                substrings.append(current_substring)
            current_substring = word

    # Add the last substring if it's not empty
    if current_substring:
        substrings.append(current_substring)

    return substrings
