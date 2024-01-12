import re


def validate_and_process_input(input_string):
    cleaned_input = re.sub(r'[^a-zA-Z, ]', '', input_string).lower()
    return ','.join(cleaned_input.split(','))
