import re
import numpy as np


def clean_label(field):
    '''
    clean addresses
    field: address, city or postal code
    '''

    # upper case
    field_new = field.upper()

    # if 2 À 10 RUE ... replaced À by COMPRIS JUSQUE
    # 2 COMPRIS JUSQUE 10 RUE
    detect = re.findall(
        '.*[0-9]+[\t| |-]*(AU|À)[\t| |-]*[0-9]+.*',
        field_new)
    if detect:
        for elem in detect:
            first_pos = field_new.find(elem)
            start = first_pos
            end = first_pos + len(elem)
            matched = field_new[start:end]
            if 'AU' in matched[0]:
                index = matched.find('AU') + start
                field_new = field_new[0:index] + ' COMPRIS JUSQUE ' +\
                    field_new[index+2:len(field_new)]

            elif 'À' in matched[0]:
                index = matched.find('À') + start
                field_new = field_new[0:index] + ' COMPRIS JUSQUE ' +\
                    field_new[index+1:len(field_new)]

    # try to replace other special encoding
    field_new = re.sub("Ã|Ã¢|A£|\\?Á|C½|¶|·|À|Á|Â|Ã|Ä|Å", "A", field_new)
    field_new = re.sub("Ã©|A©|Ã¨|A¨|Ãª|Aª|Ã«|A«|\
    \\?¿|AC¦|Â¦|AEA©|EAª|Ó|Ì©|\\?®|[ÈÉÊË]", "E", field_new)
    field_new = re.sub("Ã¯|A¯|A®|×|AØ|[ÌÍÎÏ]", "I", field_new)
    field_new = re.sub("Ã´|A´|[ÒÓÔÕÖ]", "O", field_new)
    field_new = re.sub("Ã¹|Ã¼¹|A¼|A»|[ÙÚÛÜ]", "U", field_new)
    field_new = re.sub("Ÿ|Ý", "Y", field_new)
    field_new = re.sub("Ã§|À§|À§|A§|§¢|Ç", "C", field_new)
    field_new = re.sub("Ã¦|ÂC¦", "AE", field_new)
    field_new = re.sub("Å", "OE", field_new)
    field_new = re.sub("E½", "EME", field_new)
    field_new = re.sub("I¿½|IE½|¡|Õ|Ø", "°", field_new)
    field_new = re.sub("’|´", "'", field_new)
    field_new = re.sub("–", "-", field_new)
    field_new = re.sub("\\[", "\\(", field_new)
    field_new = re.sub("\\]", "\\)", field_new)
    field_new = re.sub("N\\*|N\\?|N\\?\\(|NÂ°|NA°", "NUMERO", field_new)
    field_new = re.sub("Æ", "AE", field_new)
    field_new = re.sub("Œ", "OE", field_new)

    # remove special characters (punctuation)
    field_new = re.sub('[\\?!/_\\.,;:&\\-\'\\(\\)\\/"]', " ", field_new)

    # replace common abbreviations
    field_new = re.sub("L-D", "LIEUDIT", field_new)

    # replace email adresses by email to identify them
    field_new = re.sub("^[a-zA-Z0-9]+(?:\\.[a-zA-Z0-9]+)*@[a-zA-Z0-9]+"
                       "(?:\\.[a-zA-Z0-9]+)*$", "EMAIL", field_new)

    # remove any non alpha-numeric character
    field_new = re.sub(r'[^A-Za-z0-9 ]+', '', field_new)

    return field_new


def clean_code(field, pad_with_zero=True):
    try:
        # transform float type for CP
        new_field = float(field)
        new_field = int(new_field)
        new_field = str(new_field)

    except:
        if field == np.nan:
            new_field = ''
        else:
            new_field = str(field)

    if len(new_field) == 4:
        new_field = '0' + new_field

    return new_field
