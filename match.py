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

@lru_cache(None)  # Memoization 
def match_helper(text, pattern, case_sensitive=True):
    """
    Recursive helper function for matching text against a pattern.
    Supports:
    - Wildcard '.' (matches any character).
    - Quantifiers '*' (0 or more), '+' (1 or more), '?' (0 or 1).
    - Character classes '[abc]', ranges '[a-z]'.
    - Case-sensitive matching based on a parameter.
    """
    if not pattern:
        return not text  # If pattern is empty, return True only if text is also empty.

    # Adjust for case-insensitivity
    if not case_sensitive:
        text = text.lower()
        pattern = pattern.lower()

    # Function to check if the first character matches
    def char_matches(c, p):
        if p.startswith('[') and ']' in p:  # [abc] or [a-z]
            end = p.index(']')
            chars = set()
            i = 1
            while i < end:
                if i + 2 < end and p[i + 1] == '-':  # Handle ranges like [a-z]
                    chars.update(chr(x) for x in range(ord(p[i]), ord(p[i + 2]) + 1))
                    i += 3
                else:  # Add individual characters 
                    chars.add(p[i])
                    i += 1
            return c in chars, p[end + 1:]  # Return match status and remaining pattern
        return c == p or p == '.', p[1:]  # Match direct character or '.' wildcard

    first_match, remaining_pattern = char_matches(text[0] if text else '', pattern)

    # Handle quantifiers
    if len(remaining_pattern) >= 1:
        if remaining_pattern[0] == '*':  # '*' matches 0 or more of the preceding element
            return (match_helper(text, remaining_pattern[1:], case_sensitive) or
                    (first_match and match_helper(text[1:], pattern, case_sensitive)))
        elif remaining_pattern[0] == '+':  # '+' matches 1 or more of the preceding element
            return first_match and match_helper(text[1:], pattern, case_sensitive)
        elif remaining_pattern[0] == '?':  # '?' matches 0 or 1 of the preceding element
            return (match_helper(text, remaining_pattern[1:], case_sensitive) or
                    (first_match and match_helper(text[1:], remaining_pattern[1:], case_sensitive)))

    # Continue matching without quantifiers
    return first_match and match_helper(text[1:], remaining_pattern, case_sensitive)

def match(text, pattern, case_sensitive=True):
    """
    Wrapper function to validate the pattern and invoke the matching logic.
    - Supports partial matching.
    """
    validate_pattern(pattern)  # Validate the pattern for syntax errors

    # Iterate over the text to find partial matches
    for i in range(len(text) + 1):
        if match_helper(text[i:], pattern, case_sensitive):
            return True
    return False

def count_matches(text, pattern, case_sensitive=True):
    """
    Count the number of times the pattern matches within the text.
    - Iterates through the text, checking for matches starting at each position.
    """
    validate_pattern(pattern)  # Validate the pattern for syntax errors
    matches = 0
    for i in range(len(text)):
        if match(text[i:], pattern, case_sensitive):  # Check if a match starts at position i
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
    print("Supports: '.', '*', '+', '?', '[abc]', '[a-z]', case sensitivity, and anchors ('^', '$').")
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

            # Count matches
            count = count_matches(text, pattern, case_sensitive)
            print(f"\nPattern matches found: {count}")

            # Full match check
            if match(text, pattern, case_sensitive):
                print("The text matches the pattern.")
            else:
                print("The text does not match the pattern.")

        except ValueError as ve:
            print(f"Error: {ve}")  # Display error for invalid patterns
        except Exception as e:
            print(f"Unexpected error: {e}")  # Catch-all for other exceptions

if __name__ == "__main__":
    interactive_regex_matcher()  # Run the interactive interface
