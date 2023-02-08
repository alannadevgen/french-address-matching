import re
import pandas as pd

sufixes = ['BIS', 'TER', 'QUATER', 'QUINQUIES', 'SEXIES', 'SEPTIES',
'OCTIES', 'NONIES', 'DECIES', 'B', 'T', 'Q', 'A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

def tag_numvoie(row_tokens, row_tags, index, libvoie_file):
    '''
    tag_numvoie: give a NUMVOIE tag to a token if it is relevant
    row_tokens: tokens of one row
    row_tags: tags of one row
    index: index of the token to tag
    libvoie_file: file containing all tokens that must be tagged as LIBVOIE
    '''
    # identify common format for NUMVOIE like 42
    if row_tokens[index].isdigit() and len(row_tokens[index]) < 5 and not re.match("^0[0-9]{2,3}$", row_tokens[index]):
        row_tags[index] = "NUMVOIE"

    # very rare to have 0B or 0C for a NUMVOIE
    elif row_tokens[index][0] != '0': 
        # identify NUMVOIE composed with a suffix like 42B or 42TER
        last_pos = 0 # position of the last digit
        
        for elem in row_tokens[index]:
            if elem.isdigit():
                last_pos += 1
            else:
                break
        
        if last_pos > 0:
            letter_after_digit = row_tokens[index][last_pos : len(row_tokens[index])]
            if letter_after_digit in sufixes:
                row_tags[index] = "NUMVOIE"
    
    return row_tags


def complete_tags(row_tags, tag_to_complete, index_first_tag):
    '''
    complete_tags: if we have PARCELLE INCONNU INCONNU PARCELLE, replace INCONNU by PARCELLE
    similarly, if we have LIBVOIE INCONNU INCONNU, replace the 2 last tags by INCONNU
    row_tags: tags of one row
    tag_to_complete: name of the tag to complete
    index_first_tag: index of the first token associate with tag_to_complete
    '''

    index_next_tag = len(row_tags)

    # identify the index of the next tag if there is one
    for index in range(index_first_tag + 1, len(row_tags)):
        if row_tags[index] != 'INCONNU':
            index_next_tag = index
            break
    
    # complete all tags in the middle 
    # if only one tag, it will complete until the end
    for index in range(index_first_tag + 1, index_next_tag):
        row_tags[index] = tag_to_complete
    
    return row_tags


def tag(tokenized_field, libvoie_file):
    '''
    tag: asociate a tag for each row and for each token
    tokenized_field: list of tokens for each row (tokens is a list of token)
    libvoie_file: file containing all tokens that must be tagged as LIBVOIE
    '''
    list_tags = []
    
    for row_tokens in tokenized_field:
        # initialize all tokens to INCONNU
        row_tags = ["INCONNU" for _ in range(len(row_tokens))]
        
        for index in range(len(row_tags)):
            # identify LIBVOIE
            if row_tokens[index] in list(libvoie_file.type_voie_maj):
                row_tags[index] = "LIBVOIE"

            # identify PARCELLE
            elif re.match("^PC$|^CADAST|^PARCC?EL|^0{3}$|^FEUIL|^SEC?T?ION|^REF\.?|REFERENCE?S?$", row_tokens[index]):
                row_tags[index] = "PARCELLE"
            
            # identify complement COMP
            elif re.match("^CAVE|^COULOIR|^CO[NM]PLEM|^ADRES|^VIDE|^SAN?IT?AIR|^PARK|^LOCAUX?$|\
                ^DIVERS?$|^SORTIE?S?|^SOLS?$|^ORDUR|^CIR^CULATION|^LOGEM|^AP?PART|\
                    ^IM?MEUB|^BATIM|^ENTRE{0,2}S?|^PORTE?S$|MA?I?S{1,2}ONS?$|^PAVIL|^ETA?GE?S?|RDC|\
                        REZ|CHAUS?SE?ES?|DAL?LE{0,2}S?|^CHAMBR|SDB|^CUISI|GA[GR]A[GR]E|GRENIER\
                            CHAUFERIES?|CHAUDIERES?|^[0-9]{1,2}I?E[MR]E?$", row_tokens[index]):
                row_tags[index] = "COMP"

            # identify postal code CP
            elif row_tags[index] == "INCONNU" and re.match("^(?:0[1-9]|[1-8]\d|9[0-8])\d{3}$", row_tokens[index]):
                row_tags[index] = "CP"
            
            # identify PARCELLE (when elements are not splited by blankspace)
            elif row_tags[index] == "INCONNU" and row_tags[index-1] in ["INCONNU", "PARCELLE"] and re.match("^[0-9]{0,3}[0-9A-Z]{1}[0-9A-Z]{1}[0-9]{1,4}$", row_tokens[index]):
                # and re.match(".*[A-Z]+.*", adresse[index])
                row_tags[index] = "PARCELLE"
            
            # identify LIEU
            elif not index and not re.match(".*[0-9]+.*", row_tokens[index]):
                # tag[index] != 'INCONNU' and 
                row_tags[index] = 'LIEU'

            # identify COMMUNE
            elif re.match("^COMMUNES?$", row_tokens[index]):
                row_tags[index] = 'COMMUNE'

        for index in range(0, len(row_tags)-1):
            # identify complement before LIBVOIE like "GRAND RUE" as LIBVOIE
            if row_tags[index+1] == 'LIBVOIE':
                if re.match("^GRAND|^PETIT|^ANCIEN|^HAUT|^NOUVE|^VIEL|^VIEUX?|LE|LA|LES|AUX?", row_tokens[index]):
                    row_tags[index] = 'LIBVOIE'
            
        for index in range(1, len(row_tags)):
            # identify NUMVOIE before a LIBVOIE or at the first position
            if row_tags[index] == 'LIBVOIE' or index == 1:
                row_tags = tag_numvoie(row_tokens, row_tags, index-1, libvoie_file)

            # identify suffix after NUMVOIE
            if row_tokens[index] in sufixes and row_tags[index-1] == 'NUMVOIE':
                row_tags[index] = 'SUFFIXE'
                
        # identify PARCELLE with specific rules 
        # when elements of the parcelle are separated with blankspace
        for index in range(2, len(row_tags)):
            if row_tags[index] == "INCONNU" and re.match("^[0-9]{1,4}$", row_tokens[index]):
                if row_tags[index-1] == "INCONNU" and re.match("^[0-9A-Z]{1}[0-9A-Z]{1}$", row_tokens[index-1]):
                    if row_tags[index-2] == "INCONNU" and re.match("^[0-9]{2,3}$", row_tokens[index-2]):
                        row_tags[index-2] = "PARCELLE"
                    elif row_tags[index-2] in ["INCONNU", "PARCELLE"]:
                        row_tags[index-1] = "PARCELLE"
                        row_tags[index] = "PARCELLE"

        # if several LIBVOIE prefer to keep one with a NUMVOIE before or the first one in the sequence
        if row_tags.count("LIBVOIE") > 1:
            cpt = 0
            for index in range(len(row_tags)):
                if row_tags[index] == 'LIBVOIE':
                    cpt += 1
                if row_tags[index] == 'LIBVOIE' and cpt > 1 and row_tags[index-1] != 'NUMVOIE':
                    # if not the first and not preceded by NUMVOIE
                    row_tags[index] = 'INCONNU'
        
        # identify NUMVOIE after LIEU or LIBVOIE
        for index in range(0, len(row_tags)-1):
            if row_tags[index] in ['LIBVOIE', 'LIEU'] and row_tags[index+1] == 'INCONNU':
                row_tags = tag_numvoie(row_tokens, row_tags, index+1, libvoie_file)


        # if several tags NUMVOIE check if the middle tags between them could be NUMVOIE too
        # objective: detect sequence of NUMVOIE like 1,2,3 RUE JOLIE
        list_index = []
        if row_tags.count("NUMVOIE") > 1:
            for index in range(len(row_tags)):
                if row_tags[index] == 'NUMVOIE':
                    list_index.append(index)

            for i in range(len(list_index)-1):
                for index in range(list_index[i], list_index[i+1]):
                    row_tags = tag_numvoie(row_tokens, row_tags, index-1, libvoie_file)
        
        # idem for PARCELLE
        list_index = []
        if row_tags.count("PARCELLE") > 1:
            for index in range(len(row_tags)):
                if row_tags[index] == 'PARCELLE':
                    list_index.append(index)
            if not (sum(list_index) == (len(list_index) * (len(list_index)-1))/2):
                for i in range(len(list_index)-1):
                    for index in range(list_index[i], list_index[i+1]):
                        row_tags[index] = 'PARCELLE'

        # identify LIEU after NUMVOIE
        if 'LIBVOIE' not in row_tags:
            for index in range(0, len(row_tags)-1):
                if row_tags[index] == 'NUMVOIE' and row_tags[index+1]=='INCONNU' and not re.match(".*[0-9]+.*", row_tokens[index+1]):
                    row_tags[index+1] = 'LIEU'

        # tags INCONNU token after a LIBVOIE, a COMP or a PARCELLE tag after a first one and before the next tag (or the end)
        for index in range(len(row_tags)):
            if row_tags[index] == 'LIBVOIE':
                row_tags = complete_tags(row_tags, 'LIBVOIE', index)

            elif row_tags[index] == 'COMP':
                row_tags = complete_tags(row_tags, 'COMP', index)
            
            elif row_tags[index] == 'PARCELLE':
                row_tags = complete_tags(row_tags, 'PARCELLE', index)

            elif row_tags[index] == 'LIEU':
                row_tags = complete_tags(row_tags, 'LIEU', index)

            elif row_tags[index] == 'COMMUNE':
                row_tags = complete_tags(row_tags, 'COMMUNE', index)

            # clean LIBVOIE (remove sequence of digits or tokens containing both digits and letters)
            # which are not PARCELLE and remove LIBVOIE or LIEU containing only one token of 2 letters
            
            if row_tags[index] in ['LIBVOIE', 'LIEU'] and re.match("[A-Z]+[0-9]+|[0-9]+[A-Z]+", row_tokens[index]):
                row_tags[index] = 'INCONNU'
            
            elif row_tags[index] == 'LIBVOIE' and row_tags.count("LIBVOIE") == 1 and len(row_tokens[row_tags.index('LIBVOIE')]) < 3:
                row_tags[index] = 'INCONNU'
            
            elif row_tags[index] == 'LIEU' and row_tags.count("LIEU") == 1 and len(row_tokens[row_tags.index('LIEU')]) < 3:
                row_tags[index] = 'INCONNU'

            # if nothing after COMMUNE (probably end of LIBVOIE or LIEU)
            if row_tokens[index] in ['COMMUNE', 'COMMUNES'] and index == len(row_tags) - 1:
                if 'LIBVOIE' in row_tags:
                    row_tags[index] = 'LIBVOIE'
                elif 'LIEU' in row_tags:
                    row_tags[index] = 'LIEU'

        list_tags.append(row_tags)
    return list(zip(tokenized_field, list_tags))

def df_tags(tags):
    '''
    df_tags: create a clean dataframe composed of elements return by tag function
    '''
    list_tags = ['LIEU', 'NUMVOIE', 'SUFFIXE', 'LIBVOIE', 'PARCELLE', 'COMP', 'CP', 'COMMUNE', 'INCONNU']
    res = {}
    for elem in list_tags:
        res[elem] = []
        for index in range(len(tags)):
            tags_adresse = []
            for index2 in range(len(tags[index][0])):
                if elem == tags[index][1][index2]:
                    tags_adresse.append(tags[index][0][index2])

            res[elem].append(" ".join(tags_adresse))

    df = pd.DataFrame()
    for tag in list_tags:
        df[tag] = res[tag]

    return df