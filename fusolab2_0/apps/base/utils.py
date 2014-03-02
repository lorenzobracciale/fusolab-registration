import re

def is_polite(txt):
    """
    Search for profanities
    """
    text_to_check = txt 
    # parole da controllare senza gli spazi
    r1 = re.compile(r'porc\s?d\w+|madonna|coop|cazzo|culo|stronz|puttana|troia|coglion|piscio|cacca|merda|frocio|puppa|succhi|mortacci',  re.IGNORECASE) #profanities
    # parole da controllare con gli spazi
    r2 = re.compile(r'fica|sorca|pene|vagin|anal|pussy|cock|cumshot|cum',  re.IGNORECASE) #profanities
    # 3l33t speech
    text_to_check = text_to_check.replace("1", "i") #
    text_to_check = text_to_check.replace("0", "o") #
    text_to_check = text_to_check.replace("3", "e") #
    text_to_check = text_to_check.replace("2", "l") #
    text_to_check = text_to_check.replace("5", "s") #
    text_to_check = text_to_check.replace("8", "otto") #

    return (not r1.search(text_to_check) ) and (not r2.search(text_to_check.replace(" ", "")))


