from standardization.cleaning import clean_label, clean_code
import string
import re


def split_digit_letter(word):
    '''
    split a word composed of letters and digits
    into several tokens
    '''
    first = 0
    splited_word = []
    for index in range(1, len(word)):
        prec_digit = word[index-1].isdigit()
        current_digit = word[index].isdigit()
        # detect change letter then digit or vice versa
        if prec_digit != current_digit:
            last = index
            splited_word.append(word[first:last])
            first = index
    last = len(word)
    splited_word.append(word[first:last])
    return splited_word


# def split_libvoie(list_tokens, libvoie_file):
#     '''
#     '''
#     final = []
#     for token in list_tokens:
#         longer = 0
#         res = []

#         for elem in list(libvoie_file['type_voie_maj']):
#             inter = re.findall(
#                 f'[A-Z0-9]+{elem}[A-Z0-9]+|[A-Z0-9]+{elem}|{elem}[A-Z0-9]+',
#                 token)

#             if len(inter) and len(elem) > longer:
#                 res = inter
#                 longer = len(elem)
#                 correct_elem = elem

#         if len(res):

#             first = token.find(correct_elem)
#             end = first + len(correct_elem)
#             first_token = token[0:first]
#             second_token = token[first:end]
#             last_token = token[end:len(token)]

#             for token in [first_token, second_token, last_token]:
#                 if token != '':
#                     final.append(token)
#     if final:
#         list_tokens = final
#         return split_libvoie(list_tokens, libvoie_file=libvoie_file)
#     else:
#         return list_tokens


def tokenize_label(field, replacement_file):
    '''
    tokenize: split field in tokens,
    delete tokens composed only of punctuation and useless spaces
    '''
    nrows = field.shape[0]
    tokenized_fields = []

    for row in range(nrows):

        # check the format of the field before split
        if type(field.iloc[row]) == str:

            # clean the field of the row
            clean_adress = clean_label(field.iloc[row])

            # split tokens
            tokenized_field = re.split(',| |;', clean_adress)

            tokenized_field_new = []

            for word in tokenized_field:

                # ignore tokens only composed of punctuation
                if word not in string.punctuation:

                    # remove any residual blank space
                    for _ in range(10):
                        word = word.strip()

                    # replace common abreviation
                    # if it does not match a PARCELLE
                    for raw in range(replacement_file.shape[0]):
                        to_replace = replacement_file.iloc[raw, 0]
                        if word == to_replace and not (len(to_replace) == 2 and
                                                       re.match(
                                f'^.*[0-9]{{0,3}}\\s*{to_replace}'
                                f'\\s*[0-9]{{1,4}}.*$',
                                ' '.join(tokenized_field))):
                            word = replacement_file.iloc[raw, 1]
                            break

                    # replace N10 by 10
                    if re.match('^N[0-9]{1,4}$', word):
                        word = word[1:len(word)]

                    # separate letters and digits
                    # only when there is more than one letter and one digit
                    words_new = []
                    if re.match('^[0-9]+[A-Z]+|[A-Z]+[0-9]+$', word) \
                            and len(word) > 2 and not\
                            re.match('^[0-9]{1,3}(ER|EME)$', word):
                        words = split_digit_letter(word)

                        for word in words:
                            # replace common abreviation
                            for raw in range(replacement_file.shape[0]):
                                if word == replacement_file.iloc[raw, 0]:
                                    word = replacement_file.iloc[raw, 1]
                                    break
                            words_new.append(word)

                    # separate LIBVOIE from parasite information
                    # if words_new:
                    #     words_new = split_libvoie(words_new, libvoie_file)
                    # else:
                    #     words_new = split_libvoie([word], libvoie_file)

                    # remove punctation and N° in one token (useless)
                    # if word not in ['', '/', '-']:
                    if words_new:
                        tokenized_field_new += words_new
                    elif word != '':
                        tokenized_field_new.append(word)

            if not tokenized_field_new:
                tokenized_field_new = ['VIDE']

            tokenized_fields.append(tokenized_field_new)

        else:
            tokenized_fields.append(str(field.iloc[row]))

    return tokenized_fields


def tokenize_code(field):
    '''
    '''
    nrows = field.shape[0]
    tokenized_fields = []

    for row in range(nrows):
        tokenized_field = ''

        # clean the field of the row
        clean_adress = clean_code(field.iloc[row])

        # split tokens
        tokenized_field = re.split(',| |;', clean_adress)

        # check if only one CP and correct format (5 characters)
        if len(tokenized_field) == 1 and\
            len(tokenized_field[0]) == 5 and\
                re.match('^[A-Z0-9]{2}[0-9]{3}$', tokenized_field[0]):
            tokenized_field = tokenized_field[0]

        tokenized_fields.append(tokenized_field)

    return tokenized_fields


def most_frequent_tokens(tokenized_fields, max_top):
    '''
    return the most frequent tokens
    '''
    frequent_tokens = {}
    for row_tokens in tokenized_fields:
        for token in row_tokens:
            if not token.isdigit():
                if token not in list(frequent_tokens.keys()):
                    frequent_tokens[token] = 1
                else:
                    frequent_tokens[token] += 1

    sort = dict(sorted(
        frequent_tokens.items(),
        key=lambda item: item[1],
        reverse=True)
        )

    top = {}
    for token in list(sort.keys())[0:max_top]:
        top[token] = sort[token]

    return top
