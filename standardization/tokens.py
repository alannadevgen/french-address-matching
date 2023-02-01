import pandas as pd
import unidecode
import codecs
import string
import re

def make_tokens(adresses, remp_file):
    '''
    make_tokens: split addresses in tokens, 
    transform them in upper case,
    try to manage punctuation
    
    tokens will then be used to create tags for HMM
    '''
    nrows = adresses.shape[0]
    splited_adresses = []

    for row in range(nrows):
        if type(adresses.iloc[row]) == str:

            # replace special characters
            adresses.iloc[row] = adresses.iloc[row].replace('/', ' ')
            adresses.iloc[row] = adresses.iloc[row].replace('-', ' ')
            adresses.iloc[row] = adresses.iloc[row].replace('(', ' ')
            adresses.iloc[row] = adresses.iloc[row].replace(')', ' ')

            adresses.iloc[row] = adresses.iloc[row].upper()
            

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

                    # replace abreviation
                    for raw in range(remp_file.shape[0]):
                        if word_new == remp_file.iloc[raw, 0]:
                            word_new = remp_file.iloc[raw, 1]
                            break
                    
                    if word_new != '':
                        splited_adress_new.append(word_new)

            splited_adresses.append(splited_adress_new)
    return splited_adresses

def numvoie(adresse, tag, libvoie, sufixes, index):
    if adresse[0].isdigit() and len(adresse[index]) < 5 and adresse[index] != '000':
            tag[index] = "NUMVOIE"
    else:
        last_pos = 0
        for elem in adresse[index]:
            if elem.isdigit():
                last_pos +=1
            else:
                break
        if last_pos > 0:
            letter_after_digit = adresse[index][last_pos : len(adresse[index])]
            if letter_after_digit in sufixes:
                tag[index] = "NUMVOIE"
    return tag


def make_tags(tokens, libvoie):
    tags = []
    sufixes = ['BIS', 'TER', 'QUATER', 'QUINQUIES', 'SEXIES', 'SEPTIES', 
    'OCTIES', 'NONIES', 'DECIES', 'B', 'T', 'Q', 'A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    for adresse in tokens:
        tag = ["INCONNU" for _ in range(len(adresse))]

        # identify numvoie at the beginning of an address
        # tag = numvoie(adresse, tag, libvoie, sufixes, index=0)
       
        # identify libvoie
        for token in adresse:
            if token in list(libvoie.type_voie_maj):
                tag[adresse.index(token)] = "LIBVOIE"

        # identify numvoie before a libvoie
        for index in range(1, len(tag)):
            if tag[index] == 'LIBVOIE' or index == 1:
                if index > 1:
                    # print(index, adresse[index])
                tag = numvoie(adresse, tag, libvoie, sufixes, index=index-1)

        # identify suffix
        for index in range(1, len(adresse)-1):
            if adresse[index] in sufixes and (tag[index-1] == 'NUMVOIE' or tag[index+1] == 'LIBVOIE'):
                tag[index] = 'SUFFIXE'
        
        tags.append(tag)
    return list(zip(tokens, tags))

def most_frequent_tokens(splited_adresses, max_top):
    frequent_tokens = {}
    for adresse in splited_adresses:
        for token in adresse:
            try:
                int(token)
            except:
                if token not in list(frequent_tokens.keys()):
                    frequent_tokens[token] = 1
                else:
                    frequent_tokens[token] += 1
    sort = dict(sorted(frequent_tokens.items(), key=lambda item: item[1], reverse=True))
    top = {}
    for token in list(sort.keys())[0:max_top]:
        top[token] = sort[token]
    return top