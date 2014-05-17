import random
import string

alphanumerals = string.letters + string.digits

def string(length=8, chars=alphanumerals):
    return ''.join(random.choice(chars) for i in range(length))
