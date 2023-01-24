import pandas as pd
import unidecode
import codecs
import string
import re

def make_tokens(adresses):
    '''
    make_tokens: split addresses in tokens, 
    transform them in upper case,
    try to manage punctuation
    
    tokens will then be used to create tags for HMM
    '''
    nrows = adresses.shape[0]
    splited_adresses = []

    for row in range(nrows):
        splited_adress = re.split(',| |;', adresses.iloc[row])
        splited_adress_new = []
        for word in splited_adress:
            if word not in string.punctuation:
                try:
                    word_new = codecs.encode(word, encoding="iso-8859-1")
                    word_new = str(word_new, 'utf-8')
                except:
                    word_new = word
                
                # remove accents
                word_new = unidecode.unidecode(word_new)
                word_new = word_new.upper()
                
                # processing 'n°'
                word_new = word_new.replace('NDEG', '')
                word_new = word_new.replace('N?', '')
                word_new = word_new.replace('N!', '')
                if word_new == "N":
                    word_new = word_new.replace('N', '')
                
                if word_new != '':
                    splited_adress_new.append(word_new)

        splited_adresses.append(splited_adress_new)
    return splited_adresses