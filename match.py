import re
from functools import lru_cache

def validate_pattern(pattern):
    """
    Validate the regex pattern for basic correctness.
    - Ensures proper use of *, +, ? quantifiers.
    - Checks for balanced brackets in character classes.
    """
    if '*' in pattern and (pattern.startswith('*') or '**' in pattern):
        raise ValueError("Invalid pattern: '*' must follow a character or group.")
    if '+' in pattern and (pattern.startswith('+') or '++' in pattern):
        raise ValueError("Invalid pattern: '+' must follow a character or group.")
    if '?' in pattern and (pattern.startswith('?') or '??' in pattern):
        raise ValueError("Invalid pattern: '?' must follow a character or group.")
    if pattern.count('[') != pattern.count(']'):
        raise ValueError("Unbalanced brackets in pattern.")
    return True

@lru_cache(None)
def match_helper(text, pattern, case_sensitive=True):
    """
    Recursive helper function for matching text against a pattern.
    - Supports '.', '*', '+', '?', '[abc]', '[^abc]', '[a-z]', '^', and '$'.
    - Handles quantifiers and character classes.
    """
    if not pattern:
        return not text  # If pattern is empty, return True only if text is also empty.

    # Adjust for case-insensitivity
    if not case_sensitive:
        text = text.lower()
        pattern = pattern.lower()

    # Function to check if the first character matches
    def char_matches(c, p):
        if p.startswith('[') and ']' in p:  # Handle character classes like [abc], [^abc]
            end = p.index(']')
            negate = p[1] == '^'  # Negated character class check
            chars = set()
            i = 2 if negate else 1
            while i < end:
                if i + 2 < end and p[i + 1] == '-':  # Handle ranges like [a-z]
                    chars.update(chr(x) for x in range(ord(p[i]), ord(p[i + 2]) + 1))
                    i += 3
                else:
                    chars.add(p[i])
                    i += 1
            return (c not in chars if negate else c in chars), p[end + 1:]
        return c == p or p == '.', p[1:]  # Match direct character or '.'

    # Handle the first character
    first_match = bool(text) and char_matches(text[0], pattern[0])

    # Handle quantifiers
    if len(pattern) >= 2:
        if pattern[1] == '*':  # '*' matches 0 or more of the preceding element
            # Match 0 occurrences of the character (skip '*')
            return (match_helper(text, pattern[2:], case_sensitive) or
                    # Match 1 or more occurrences of the character
                    (first_match and match_helper(text[1:], pattern, case_sensitive)))

        elif pattern[1] == '+':  # '+' matches 1 or more of the preceding element
            return first_match and match_helper(text[1:], pattern, case_sensitive)

        elif pattern[1] == '?':  # '?' matches 0 or 1 of the preceding element
            return (match_helper(text, pattern[2:], case_sensitive) or
                    (first_match and match_helper(text[1:], pattern[2:], case_sensitive)))

    # Match anchors
    if pattern.startswith('^'):
        return match_helper(text, pattern[1:], case_sensitive) if text else False
    if pattern.endswith('$') and len(pattern) > 1:
        return match_helper(text, pattern[:-1], case_sensitive) if not text else False

    # Continue matching without quantifiers
    return first_match and match_helper(text[1:], pattern[1:], case_sensitive)

def match(text, pattern, case_sensitive=True):
    """
    Wrapper function to validate the pattern and invoke the matching logic.
    - Supports partial matching.
    """
    validate_pattern(pattern)  # Validate the pattern
    return match_helper(text, pattern, case_sensitive)

def count_matches(text, pattern, case_sensitive=True):
    """
    Count the number of times the pattern matches within the text.
    """
    validate_pattern(pattern)  # Validate the pattern
    matches = 0
    for i in range(len(text)):  # Check from every position
        if match(text[i:], pattern, case_sensitive):
            matches += 1
    return matches

def interactive_regex_matcher():
    """
    Interactive command-line interface for testing the regex matcher.
    Features:
    - Allows users to input text and patterns.
    - Supports case-sensitive matching toggle.
    - Displays match results and count of matches.
    """
    print("Welcome to the Regex Matcher!")
    print("Supports: '.', '*', '+', '?', '[abc]', '[a-z]', '[^abc]', case sensitivity, and anchors ('^', '$').")
    print("Type 'exit' to quit.")

    while True:
        text = input("\nEnter the text: ")
        if text.lower() == 'exit':  # Exit condition
            print("Goodbye!")
            break
        pattern = input("Enter the pattern: ")
        if pattern.lower() == 'exit':  # Exit condition
            print("Goodbye!")
            break
        case_sensitive = input("Case-sensitive matching? (yes/no): ").strip().lower() == 'yes'

        try:
            validate_pattern(pattern)  # Validate the pattern
            count = count_matches(text, pattern, case_sensitive)
            print(f"\nPattern matches found: {count}")

            if count > 0:
                print("The text matches the pattern.")
            else:
                print("The text does not match the pattern.")

        except ValueError as ve:
            print(f"Error: {ve}")
        except Exception as e:
            print(f"Unexpected error: {e}")

if __name__ == "__main__":
    interactive_regex_matcher()
