import re
import extraction as ex



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


    def is_same(self, s, category):
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
            
            if last == -1:
                return first

            if first == -1:
                return  last

            if (first == 0 and self.first_name != None) or (last == 0 and self.last_name != None):
                return 0
            else:
                return (first + last) / 2

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

        self.complete()

        return str(self.first_name) + ' ' + str(self.last_name)
            

def mask_type(mask):
    if "FULL" in mask: return 'full'
    if "DOB" in mask: return 'dob'
    if "FIRST" in mask: return 'first'
    if "LAST" in mask: return 'last'

def change_index(mask, ind):
    pattern = r'\d|X'
    res = re.sub(pattern, str(ind), mask, count=1)
    return res

def rectify(mask_pairs):
    max_ind = 1
    names = []

    # repeat this procedure to connect up first and last names
    for _ in range(2):
        
        for i in range(len(mask_pairs)):
            
            mask, content = mask_pairs[i]
            cur_type = mask_type(mask)
    
            if cur_type == 'dob': continue
    
            should_add = 1
    
            for name in names:
                if name.is_same(content, cur_type) > 0:
                    new_mask = change_index(mask, name.index)
                    mask_pairs[i] = (new_mask, content)
                    name.fill(content, cur_type)
                    should_add = 0
                    break
                
            if should_add == 1:
                new_name = Name()
                new_name.fill(content, cur_type)
                new_name.index = max_ind
                max_ind += 1
                names.append(new_name)
                
    return mask_pairs

def fix_masks(input, masked):
    p = ex.extract_masked_info(input, masked)
    p = indexing.rectify(p)
    replacements = [pair[0] for pair in p]
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

    