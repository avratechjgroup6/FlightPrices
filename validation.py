import re


def check_name(name):
    if type(name) is str:
        good_name = re.compile("([ a-zA-Z]+)+")
        if good_name.fullmatch(name):
            return True
    return False


def check_email(email):
    if type(email) is str:
        valid_chars = "a-zA-Z0-9\_\-\."
        good_email = re.compile("[{0}]+@[{0}]+\.[{0}]+".format(valid_chars))
        if good_email.fullmatch(email):
            return True
    return False
