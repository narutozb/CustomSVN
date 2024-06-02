from django.core.exceptions import ValidationError
import re

def validate_url(value):
    # Regex pattern to validate URL (allowing URLs without TLD)
    pattern = re.compile(
        r'^(https?|ftp|svn\+ssh)://'  # Add 'svn+ssh' to the protocols
        r'((([a-zA-Z0-9][-a-zA-Z0-9]*)\.)*[a-zA-Z][-a-zA-Z0-9]*|'  # domain
        r'((\d{1,3}\.){3}\d{1,3})|'  # or ip
        r'([a-zA-Z0-9][-a-zA-Z0-9]*@)?'  # optional username
        r'((\d{1,3}\.){3}\d{1,3}))'  # ip
        r'(:\d+)?(/[-a-zA-Z0-9%_.~+]*)*'  # port and path
        r'(\?[-a-zA-Z0-9%_.~+=]*)?'  # query
        r'(#[-a-zA-Z0-9_]*)?$'  # fragment
    )
    if not pattern.match(value):
        raise ValidationError(f'{value} is not a valid URL')