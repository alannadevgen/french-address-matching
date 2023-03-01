import re
import pandas as pd


sufixes = [
    'BIS', 'TER', 'QUATER', 'QUINQUIES', 'SEXIES', 'SEPTIES', 'OCTIES',
    'NONIES', 'DECIES', 'B', 'T', 'Q', 'A', 'C', 'D', 'E', 'F', 'G', 'H',
    'I', 'J', 'K', 'S', 'BI'
    ]


def tag_numvoie(row_tokens, row_tags, index, libvoie_file):
    '''
    tag_numvoie: give a NUMVOIE tag to a token if it is relevant
    row_tokens: tokens of one row
    row_tags: tags of one row
    index: index of the token to tag
    libvoie_file: file containing all tokens that must be tagged as LIBVOIE
    '''
    # identify common format for NUMVOIE like 42
    if row_tokens[index].isdigit() and\
        len(row_tokens[index]) < 5 and not\
            re.match("^0{3}[0-9]*$", row_tokens[index]):
        row_tags[index] = "NUMVOIE"

    # very rare to have 0B or 0C for a NUMVOIE
    elif row_tokens[index][0] != '0':

        # position of the last digit:
        last_pos = 0

        # identify NUMVOIE composed with a suffix like 42B or 42TER
        for elem in row_tokens[index]:
            if elem.isdigit():
                last_pos += 1
            else:
                break

        if last_pos > 0:
            letter_after_digit =\
                row_tokens[index][last_pos:len(row_tokens[index])]
            if letter_after_digit in sufixes:
                row_tags[index] = "SUFFIXE"

    return row_tags


def complete_tags(row_tags, tag_to_complete, index_first_tag):
    '''
    complete_tags: if we have PARCELLE INCONNU INCONNU PARCELLE,
    replace INCONNU by PARCELLE
    similarly, if we have LIBVOIE INCONNU INCONNU,
    replace the 2 last tags by INCONNU
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


def tag_before(row_tags, tag):
    '''
    '''
    index_numvoie = []
    index_tag = []
    for index in range(len(row_tags)):

        if row_tags[index] in ['NUMVOIE', 'SUFFIXE']:
            index_numvoie.append(index)
        if row_tags[index] == tag:
            index_tag.append(index)

    for libvoie in index_tag:
        before_lib = list(filter(lambda index: index < libvoie,
                                 index_numvoie))

        if before_lib:
            max_num = max(before_lib)
            all_unk = True
            for index_tag in range(max_num+1, libvoie):
                if row_tags[index_tag] != 'INCONNU':
                    all_unk = False
                    break

            if all_unk:
                for index_tag in range(max_num+1, libvoie):
                    row_tags[index_tag] = tag

        else:
            all_unk = True
            for index_tag in range(0, libvoie):
                if row_tags[index_tag] != 'INCONNU':
                    all_unk = False
                    break

            if all_unk:
                for index_tag in range(0, libvoie):
                    row_tags[index_tag] = tag


def tag_tokens(
    tokenized_addresses,
    tokenized_cp,
    tokenized_communes,
    libvoie_file
        ):
    '''
    tag: asociate a tag for each row and for each token
    tokenized_field: list of tokens for each row (tokens is a list of token)
    libvoie_file: file containing all tokens that must be tagged as LIBVOIE
    '''
    list_tags = []
    for index_row in range(len(tokenized_addresses)):

        row_tokens = tokenized_addresses[index_row]

        # initialize all tokens to INCONNU
        row_tags = ["INCONNU" for _ in range(len(row_tokens))]
        for index in range(len(row_tags)):

            # identify LIBVOIE
            if row_tokens[index] in list(libvoie_file.type_voie_maj):

                row_tags[index] = "LIBVOIE"

            # identify PARCELLE
            elif re.match("^PC$|^CADAST|^PARCC?EL|^0{3}$|^FEUIL"
                          "|^SEC?T?ION|^REF\\.?$|REFERENCE?S?$",
                          row_tokens[index]):

                row_tags[index] = "PARCELLE"

            # identify complement COMP
            elif re.match(
                "^CAVE|^COULOIR|^CO[NM]PLEM|^ADRES|^VIDE|"
                "^SAN?IT?AIR|^PARK|^LOCAUX?$|^DIVERS?$|^SORTIE?S?|^SOLS?$|"
                "^ORDUR|^CIR^CULATION|^LOGEM|^AP?PART|^IM?MEUB|^BATIM|"
                "^ENTRE{0,2}S?|^PORTE?S$|^PAVIL|^ETA?GE?S?|RDC|^REZ$|"
                "^CHAUS?SE?ES?$|^DAL?LE{0,2}S?$|^CHAMBR|SDB|^CUISI|"
                "GA[GR]A[GR]E|GRENIER|CHAUFERIES?|CHAUDIERES?"
                    "|^[0-9]{1,2}I?E[MR]E?$", row_tokens[index]):
                row_tags[index] = "COMPADR"

            # identify postal code CP
            elif row_tags[index] == "INCONNU" and re.match("^(?:0[1-9]|\
            |[1-8]\\d|9[0-8])\\d{3}$", row_tokens[index]):
                row_tags[index] = "CP"

            # identify PARCELLE (when elements are not splited by blankspace)

            # and row_tags[index] == "000"
            elif row_tags[index] == "INCONNU" and\
                row_tags[index-1] == 'INCONNU' and\
                    re.match("^[0-9]{0,3}[0-9A-Z]{1}"
                             "[0-9A-Z]{1}[0-9]{1,4}$", row_tokens[index]) and\
                    not row_tokens[index].isdigit():

                row_tags[index] = "PARCELLE"

            # identify COMMUNE
            elif re.match("^COMMUNES?$", row_tokens[index]):

                row_tags[index] = 'COMMUNE'

            # identify PERSO at the beginning
            elif index in [0, 1] and re.match(
                "^[a-zA-Z0-9]+(?:\\.[a-zA-Z0-9]+)*@"
                "[a-zA-Z0-9]+(?:\\.[a-zA-Z0-9]+)*$|^MR\\.?$|^M$|^M\\.$|^MME$"
                    "|^ME?L?LE$|MONSIEUR|MADAME|MADEMOISELLE|CHEZ|EMAIL",
                    row_tokens[index]):

                row_tags[index] = 'PERSO'

            # identify LIEU
            elif not index and not re.match(".*[0-9]+.*", row_tokens[index]):
                row_tags[index] = 'LIEU'

        # identify COMMUNE with commune field
        commune = tokenized_communes[index_row]

        for index_start in range(len(row_tags)-len(commune)+1):
            # detect the first token in commune
            if (row_tokens[index_start] == commune[0] and
                index_start == 0) or\
                    (row_tokens[index_start] == commune[0]
                        and row_tokens[index_start-1] != 'DE'):
                detected = True

                # detect the following ones if needed
                for index_com in range(1, len(commune)):
                    if row_tokens[index_start+index_com] == commune[index_com]:
                        detected *= True
                    else:
                        detected *= False

                if detected:
                    index_end = index_start + len(commune)

                    for position in range(index_start, index_end):
                        row_tags[position] = 'COMMUNE'

                break

        for index in range(0, len(row_tags)-1):
            # identify suffix before LIBVOIE
            if row_tokens[index] in sufixes and\
                    row_tags[index + 1] == 'LIBVOIE':
                row_tags[index] = 'SUFFIXE'
                # identify NUMVOIE before LIBVOIE
                index_possible_numvoie = max(0, index-1)
                tag_numvoie(
                    row_tokens,
                    row_tags,
                    index_possible_numvoie,
                    libvoie_file
                    )

            elif re.match("^ETG|ETAGE$", row_tokens[index]):
                row_tags[index] = "COMPADR"
                if row_tokens[index + 1].isdigit() and\
                        row_tags[index + 1] == 'INCONNU':
                    row_tags[index + 1] = "COMPADR"

        for index in range(1, len(row_tags)):
            # identify NUMVOIE before a LIBVOIE or at the first position
            if row_tags[index] == 'LIBVOIE' or index == 1 and\
                    row_tags[index-1] == 'INCONNU':
                row_tags =\
                    tag_numvoie(row_tokens, row_tags, index-1, libvoie_file)

            # identify suffix after NUMVOIE
            if row_tokens[index] in sufixes and row_tags[index-1] == 'NUMVOIE':
                row_tags[index] = 'SUFFIXE'

        # identify PARCELLE with specific rules
        # when elements of the parcelle are separated with blankspace
        for index in range(2, len(row_tags)):

            if row_tags[index] == "INCONNU" and\
                    re.match("^[0-9]{1,4}$", row_tokens[index]):

                if row_tags[index-1] == "INCONNU" and\
                    row_tokens[index-1] not in ['DU', 'DE', 'DES', 'ET'] and\
                    re.match("^[0-9A-Z]{1}[0-9A-Z]{1}$",
                             row_tokens[index-1]) and\
                        not row_tokens[index-1].isdigit():

                    if row_tags[index-2] == "INCONNU"\
                            and re.match("^[0-9]{2,3}$",
                                            row_tokens[index-2]):

                        row_tags[index-2] = "PARCELLE"
                        row_tags[index-1] = "PARCELLE"
                        row_tags[index] = "PARCELLE"

                    # elif row_tags[index-2] in ["INCONNU", "PARCELLE"]:
                    else:
                        row_tags[index-1] = "PARCELLE"
                        row_tags[index] = "PARCELLE"

            # identify PERSO after a LIBVOIE
            elif re.match(
                "^[a-zA-Z0-9]+(?:\\.[a-zA-Z0-9]+)*@[a-zA-Z0-9]+"
                "(?:\\.[a-zA-Z0-9]+)*$|^MR\\.?$|^M\\.$|^M$|^MME$|^ME?L?LE$|"
                    "MONSIEUR|MADAME|MADEMOISELLE", row_tokens[index]):

                if (row_tags[index - 1] != 'LIBVOIE' and row_tokens[index-1]
                        not in ['DE'] and row_tags[index - 2] != 'LIBVOIE')\
                        or row_tokens[index - 1] == 'CHEZ':

                    row_tags[index] = 'PERSO'

        # if token RESIDENCE / LOTISSEMENT and another token tagged as LIBVOIE
        # tag RESIDENCE or LOTISSEMENT as LIEU
        if row_tags.count("LIBVOIE") > 1:
            cpt = 0

            for index in range(len(row_tags)):
                if row_tags[index] == 'LIBVOIE':
                    if re.match("RESIDENCE|LOTIS?SEMENT", row_tokens[index]):
                        row_tags[index] = 'LIEU'
                    else:
                        cpt += 1

        # identify NUMVOIE after LIEU or LIBVOIE
        for index in range(0, len(row_tags)-1):
            if row_tags[index] in ['LIBVOIE', 'LIEU'] and\
                    row_tags[index+1] == 'INCONNU':

                row_tags =\
                    tag_numvoie(row_tokens, row_tags, index+1, libvoie_file)

        # tag INCONNU tags as LIBVOIE if between NUMVOIE and LIBVOIE
        # allow to identify 1 PETITE RUE DE (PETITE as LIBVOIE)
        # empty list used in the for (below)
        tag_before(row_tags, tag='LIBVOIE')
        tag_before(row_tags, tag='LIEU')

        # if several tags NUMVOIE check if the middle tags between them could
        # be NUMVOIE too
        # objective: detect sequence of NUMVOIE like 1,2,3 RUE JOLIE
        list_index = []
        if (row_tags.count("NUMVOIE") + row_tags.count("SUFFIXE")) > 1:
            middle_tags_unk = True
            for index in range(len(row_tags)):
                if not index and row_tags[index] in ['NUMVOIE', 'SUFFIXE']:
                    list_index.append(index)

                elif middle_tags_unk and row_tags[index] in [
                    'NUMVOIE',
                    'SUFFIXE'
                        ]:
                    list_index.append(index)
                    middle_tags_unk = True

                if row_tags[index] not in ['INCONNU', 'NUMVOIE', 'SUFFIXE']:
                    middle_tags_unk *= False

        if len(list_index) > 1:
            for i in range(len(list_index)-1):
                for index in range(list_index[i], list_index[i+1]):
                    row_tags = tag_numvoie(
                        row_tokens,
                        row_tags,
                        index,
                        libvoie_file
                    )
                    if row_tokens[index] in sufixes:
                        row_tags[index] = "SUFFIXE"

        # identify LIEU after NUMVOIE or SUFFIX
        if 'LIBVOIE' not in row_tags:
            for index in range(0, len(row_tags)-1):
                if row_tags[index] in ['NUMVOIE', 'SUFFIXE'] and\
                    row_tags[index+1] == 'INCONNU' and not\
                        re.match(".*[0-9]+.*", row_tokens[index+1]):
                    row_tags[index+1] = 'LIEU'

        # tags INCONNU token after a LIBVOIE, a COMP or a PARCELLE tag after
        # a first one and before the next tag (or the end)
        for index in range(len(row_tags)):
            if row_tags[index] == 'LIBVOIE':
                row_tags = complete_tags(row_tags, 'LIBVOIE', index)

            elif row_tags[index] == 'COMPADR':
                row_tags = complete_tags(row_tags, 'COMPADR', index)

            elif row_tags[index] == 'PARCELLE':
                row_tags = complete_tags(row_tags, 'PARCELLE', index)

            elif row_tags[index] == 'LIEU':
                row_tags = complete_tags(row_tags, 'LIEU', index)

            elif row_tags[index] == 'COMMUNE':
                row_tags = complete_tags(row_tags, 'COMMUNE', index)

            # clean LIBVOIE (remove sequence of digits or tokens containing
            # both digits and letters)
            # which are not PARCELLE and remove LIBVOIE or LIEU containing
            # only one token of 2 letters

            if row_tags[index] in ['LIBVOIE', 'LIEU']\
                    and re.match(
                        "[A-Z]+[0-9]+|[0-9]+[A-Z]+", row_tokens[index]
                        ):
                row_tags[index] = 'INCONNU'

            # if nothing after COMMUNE (probably end of LIBVOIE or LIEU)
            if row_tokens[index] in ['COMMUNE', 'COMMUNES']\
                    and index == len(row_tags) - 1:

                if 'LIBVOIE' in row_tags:
                    row_tags[index] = 'LIBVOIE'

                elif 'LIEU' in row_tags:
                    row_tags[index] = 'LIEU'

        # if only one LIBVOIE and several LIEU tag LIBVOIE as LIEU
        if row_tags.count("LIBVOIE") == 1 and row_tags.count("LIEU") > 1:
            index_to_replace = row_tags.index('LIBVOIE')
            row_tags[index_to_replace] = 'LIEU'

        # if only one LIEU and several LIBVOIE tag LIEU as LIBVOIE
        if row_tags.count("LIEU") == 1 and row_tags.count("LIBVOIE") > 1:
            index_to_replace = row_tags.index('LIEU')
            row_tags[index_to_replace] = 'LIBVOIE'

        list_tags.append(row_tags)

    return list(zip(tokenized_addresses, list_tags))


def remove_perso_info(tags):
    '''
    remove_perso_info remove personnal information from the final result
    '''
    # iterate over all addresses
    clean_tokens = []
    clean_tags = []
    for index in range(len(tags)):
        clean_tokens_address = []
        clean_tags_address = []

        remove = False
        # iterate over all tags of one address
        for index2 in range(len(tags[index][1])):

            if tags[index][1][index2] != 'PERSO':
                clean_tokens_address.append(tags[index][0][index2])
                clean_tags_address.append(tags[index][1][index2])
            else:
                remove = True

        if not remove:
            clean_tokens.append(clean_tokens_address)
            clean_tags.append(clean_tags_address)

    return list(zip(clean_tokens, clean_tags))


def df_tags(tags):
    '''
    df_tags: create a clean dataframe composed of elements return
    by tag function
    '''
    list_tags = [
        'LIEU', 'NUMVOIE', 'SUFFIXE', 'LIBVOIE', 'PARCELLE', 'COMPADR',
        'CP', 'COMMUNE', 'INCONNU', 'PERSO'
        ]
    res = {}
    for elem in list_tags:
        res[elem] = []
        for index in range(len(tags)):
            tags_adresse = []
            for index2 in range(len(tags[index][1])):
                if elem == tags[index][1][index2]:
                    tags_adresse.append(tags[index][0][index2])

            res[elem].append(" ".join(tags_adresse))

    df = pd.DataFrame()
    for tag in list_tags:
        df[tag] = res[tag]

    return df
