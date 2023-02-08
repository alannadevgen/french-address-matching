import pandas as pd
import unidecode
import codecs
import string
import re

def cleaning_encoding(field):
    '''
    perform basic standardisation / cleaning on addresses
    '''

    # upper case
    field = field.upper()

    # manage frequent encoding issues
    try:
        field_new = codecs.encode(field, encoding="iso-8859-1")
        field_new = str(field, 'utf-8')
    except:
        field_new = field
    
    field_new = unidecode.unidecode(field_new)
    field_new = field_new.upper()
    
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
    field_new = re.sub("N°|NADEG|NDEG", "", field_new)
    
    return field_new


def make_tokens(adresses, remp_file):
    '''
    make_tokens: split addresses in tokens, 
    delete tokens composed only of punctuation
    '''
    nrows = adresses.shape[0]
    splited_adresses = []

    for row in range(nrows):
        if type(adresses.iloc[row]) == str:
            
            clean_adress = cleaning_encoding(adresses.iloc[row])

            splited_adress = re.split(',| |;', clean_adress)
            splited_adress_new = []
            for word in splited_adress:
                if word not in string.punctuation:
                    # remove any residual blank space:
                    word = re.sub(' +', '', word)
                    word = re.sub(' ', '', word)

                    # replace common abreviation
                    for raw in range(remp_file.shape[0]):
                        if word == remp_file.iloc[raw, 0]:
                            word = remp_file.iloc[raw, 1]
                            break
                # remove punctation and N° (useless)
                if word not in ['', '/', '-']:    
                    splited_adress_new.append(word)

            splited_adresses.append(splited_adress_new)
    return splited_adresses

def numvoie(adresse, tag, libvoie, sufixes, index):
    '''
    Identify NUMVOIE tags for a given tag in adresse
    '''
    # identify common format for NUMVOIE like 42
    if adresse[index].isdigit() and len(adresse[index]) < 5 and not re.match("^0[0-9]{2,3}$", adresse[index]):
            tag[index] = "NUMVOIE"

    # very rare to have 0B or 0C for a NUMVOIE
    elif adresse[index][0] != '0': 
        # identify NUMVOIE composed with a suffix like 42B or 42TER
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
    '''
    Associate a tag to each token
    '''
    tags = []
    sufixes = ['BIS', 'TER', 'QUATER', 'QUINQUIES', 'SEXIES', 'SEPTIES', 
    'OCTIES', 'NONIES', 'DECIES', 'B', 'T', 'Q', 'A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    for adresse in tokens:
        tag = ["INCONNU" for _ in range(len(adresse))]
        
        for index in range(len(tag)):
            # identify libvoie
            if adresse[index] in list(libvoie.type_voie_maj):
                tag[index] = "LIBVOIE"

            # identify parcelle or cadastre indication
            elif re.match("^CADAST|^PARCEL|^0{3}$|^FEUIL|^SECTION", adresse[index]):
                tag[index] = "PARCELLE"
            
            # identify additional information
            elif re.match("^CAVE|^COULOIR|^CO[NM]PLEM|^ADRES|^VIDE|^SAN?IT?AIR|^PARK|^LOCAUX?$|\
                ^DIVERS?$|^SORTIE?S?|^SOLS?$|^ORDUR|^CIR^CULATION|^TER?RAS?SE?S?$|^LOGEM|^AP?PART|\
                    ^IM?MEUB|^BATIM|^ENTRE{0,2}S?|^PORTE?S$|MA?I?S{1,2}ONS?$|^PAVIL|^ETA?GE?S?|RDC|\
                        REZ|CHAUS?SE?ES?|DAL?LE{0,2}S?|^CHAMBR|SDB|^CUISI|GA[GR]A[GR]E|GRENIER\
                            CHAUFERIES?|CHAUDIERES?", adresse[index]):
                tag[index] = "COMP"
            
            # identify parcelles without blankspace
            elif tag[index] == "INCONNU" and tag[index-1] in ["INCONNU", "PARCELLE"] and re.match(".*[A-Z]+.*", adresse[index]) and re.match("^[0-9]{0,3}[0-9A-Z]{1}[0-9A-Z]{1}[0-9]{1,4}$", adresse[index]):
                tag[index] = "PARCELLE"
            
            # identify LIEU
            elif not index and not re.match(".*[0-9]+.*", adresse[index]):
                # tag[index] != 'INCONNU' and 
                tag[index] = 'LIEU'

        for index in range(0, len(tag)-1):
            # identify complement before LIBVOIE like "GRAND RUE"
            if tag[index+1] == 'LIBVOIE':
                if re.match("^GRAND|^PETIT|^ANCIEN|^HAUT|^NOUVE|LE|LA|LES|AUX?", adresse[index]):
                    tag[index] = 'LIBVOIE'
            
        for index in range(1, len(tag)):
            # identify numvoie before a libvoie or at the first position
            if tag[index] == 'LIBVOIE' or index == 1:
                tag = numvoie(adresse, tag, libvoie, sufixes, index=index-1)
                # tag = numvoie(adresse, tag, libvoie, sufixes, index=index+1)
            
            # identify suffix after NUMVOIE
            if adresse[index] in sufixes and tag[index-1] == 'NUMVOIE':
                tag[index] = 'SUFFIXE'
                
        # identify parcelles with specific rules 
        # when elements of the parcelle are separated with blankspace
        for index in range(2, len(tag)):
            if tag[index] == "INCONNU" and re.match("^[0-9]{1,4}$", adresse[index]):
                if tag[index-1] == "INCONNU" and re.match("^[0-9A-Z]{1}[0-9A-Z]{1}$", adresse[index-1]):
                    if tag[index-2] == "INCONNU" and re.match("^[0-9]{2,3}$", adresse[index-2]):
                        tag[index-2] = "PARCELLE"
                    elif tag[index-2] in ["INCONNU", "PARCELLE"]:
                        tag[index-1] = "PARCELLE"
                        tag[index] = "PARCELLE"

        # if several LIBVOIE prefer to keep one with a NUMVOIE before or the first one in the sequence
        if tag.count("LIBVOIE") > 1:
            cpt = 0
            for index in range(len(tag)):
                if tag[index] == 'LIBVOIE':
                    cpt += 1
                if tag[index] == 'LIBVOIE' and cpt > 1 and tag[index-1] != 'NUMVOIE':
                    # if not the first and not preceded by NUMVOIE
                    tag[index] = 'INCONNU'

        # if several tags NUMVOIE check if the middle tags between them could be NUMVOIE
        list_index = []
        if tag.count("NUMVOIE") > 1:
            for index in range(len(tag)):
                if tag[index] == 'NUMVOIE':
                    list_index.append(index)

            for i in range(len(list_index)-1):
                for index in range(list_index[i], list_index[i+1]):
                    tag = numvoie(adresse, tag, libvoie, sufixes, index=index)
        
        # idem for PARCELLE
        list_index = []
        if tag.count("PARCELLE") > 1:
            for index in range(len(tag)):
                if tag[index] == 'PARCELLE':
                    list_index.append(index)
            if not (sum(list_index) == (len(list_index) * (len(list_index)-1))/2):
                for i in range(len(list_index)-1):
                    for index in range(list_index[i], list_index[i+1]):
                        tag[index] = 'PARCELLE'

        # identify places (LIEU) after NUMVOIE
        if 'LIBVOIE' not in tag:
            for index in range(0, len(tag)-1):
                if tag[index] == 'NUMVOIE' and tag[index+1]=='INCONNU' and not re.match(".*[0-9]+.*", adresse[index+1]):
                    tag[index+1] = 'LIEU'

        # put LIBVOIE, COMP or PARCELLE tag after a first one and before the next tag (or the end)
        for index in range(len(tag)):
            if tag[index] == 'LIBVOIE':
                lib_tag = index
                next_tag = len(tag)
                for index2 in range(lib_tag+1, len(tag)):
                    if tag[index2] != 'INCONNU':
                        next_tag = index2
                        break
                for index3 in range(lib_tag+1, next_tag):
                    tag[index3] = 'LIBVOIE'

            elif tag[index] == 'COMP':
                lib_tag = index
                next_tag = len(tag)
                for index2 in range(lib_tag+1, len(tag)):
                    if tag[index2] != 'INCONNU':
                        next_tag = index2
                        break
                for index3 in range(lib_tag+1, next_tag):
                    tag[index3] = 'COMP'
            
            elif tag[index] == 'PARCELLE':
                lib_tag = index
                next_tag = len(tag)
                for index2 in range(lib_tag+1, len(tag)):
                    if tag[index2] != 'INCONNU':
                        next_tag = index2
                        break
                for index3 in range(lib_tag+1, next_tag):
                    tag[index3] = 'PARCELLE'

            elif tag[index] == 'LIEU':
                lib_tag = index
                next_tag = len(tag)
                for index2 in range(lib_tag+1, len(tag)):
                    if tag[index2] != 'INCONNU':
                        next_tag = index2
                        break
                for index3 in range(lib_tag+1, next_tag):
                    tag[index3] = 'LIEU'

        tags.append(tag)
    return list(zip(tokens, tags))

def df_tags(tags):
    list_tags = ['LIEU', 'NUMVOIE', 'SUFFIXE', 'COMPLIBVOIE', 'LIBVOIE', 'PARCELLE', 'COMP', 'INCONNU']
    res = {}
    for elem in list_tags:
        res[elem] = []
        for index in range(len(tags)):
            tags_adresse = []
            for index2 in range(len(tags[index][0])):
                if elem == tags[index][1][index2]:
                    tags_adresse.append(tags[index][0][index2])
            res[elem].append(tags_adresse)
    
    df = pd.DataFrame()
    for tag in list_tags:
        df[tag] = res[tag]

    return df


def most_frequent_tokens(splited_adresses, max_top):
    '''
    Return the most frequent tokens
    '''
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