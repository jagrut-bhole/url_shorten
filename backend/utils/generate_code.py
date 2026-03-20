import string
import random

def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters.lower() + string.digits, k=length))

