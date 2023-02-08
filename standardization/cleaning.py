import unidecode
import codecs
import re

def clean(field):
    '''
    clean addresses
    field: address, city or postal code
    '''

    # upper case
    field_new = field.upper()
    
    # try to replace other special encoding
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
    field_new = re.sub("N\\*|N\\?|N\\?\\(|NÂ°|NA°", "N°", field_new)
    field_new = re.sub("Æ", "AE", field_new)
    field_new = re.sub("Œ", "OE", field_new)

    # remove special characters (punctuation)
    field_new = re.sub('[\\?!/_\\.,;:\\-\'\\(\\)"]', " ", field_new)

    # replace common abbreviations
    field_new = re.sub("SAINT", "ST", field_new)
    field_new = re.sub("S\\/", "SUR", field_new)

    # convert numbers (written with letters) to numbers (digits)
    field_new = re.sub("DEUX", "2", field_new)
    field_new = re.sub("TROIS", "3", field_new)
    field_new = re.sub("QUATRE", "4", field_new)
    field_new = re.sub("CINQ", "5", field_new)
    field_new = re.sub("SIX", "6", field_new)
    field_new = re.sub("SEPT", "7", field_new)
    field_new = re.sub("HUIT", "8", field_new)
    field_new = re.sub("NEUF", "9", field_new)
    field_new = re.sub("DIX", "10", field_new)

    # remove N°
    field_new = re.sub("N°|NADEG|NDEG|", "", field_new)

    # remove any non alpha-numeric character
    field_new = re.sub(r'[^A-Za-z0-9 ]+', '', field_new)
    
    return field_new
