def match(text, pattern):
    # If pattern is empty, we have a match if the text is also empty
    if not pattern:
        return not text
    
    # Checks if the first character of text matches the first character of the pattern
    first_match = bool(text) and pattern[0] in {text[0], '.'}
    
    # Handles '*' by looking at the next character in the pattern
    if len(pattern) >= 2 and pattern[1] == '*':
        # Two cases: 
        # 1. We skip 'x*' pattern in pattern 
        # 2. We use 'x*' if the first characters match and try matching the rest of text
        return (match(text, pattern[2:]) or
                (first_match and match(text[1:], pattern)))
    else:
        # If no '*', move to the next character in both text and pattern
        return first_match and match(text[1:], pattern[1:])

#returns True beccause 'abb'
#has 0 or more occurences of 'a' and exactly two occurences of 'b'
print(match("abb","a*bb"))

#returns False because the pattern needs exactly three occurences of 'b'
#and the input text does not
print(match("abb","a*bbb"))