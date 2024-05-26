from django.core.exceptions import ValidationError
import re

def validate_url(value):
    # Regex pattern to validate URL (allowing URLs without TLD)
    pattern = re.compile(
        r'^(https?|ftp)://'
        r'(((([a-zA-Z0-9][-a-zA-Z0-9]*)\.)*[a-zA-Z][-a-zA-Z0-9]*)|'
        r'((\d{1,3}\.){3}\d{1,3}))'
        r'(:\d+)?(/[-a-zA-Z0-9%_.~+]*)*'
        r'(\?[-a-zA-Z0-9%_.~+=]*)?'
        r'(#[-a-zA-Z0-9_]*)?$'
    )
    if not pattern.match(value):
        raise ValidationError(f'{value} is not a valid URL')
