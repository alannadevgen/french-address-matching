from standardization.cleaning import clean
import string
import re


def tokenize(field, replacement_file):
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
            clean_adress = clean(field.iloc[row])

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
                    for raw in range(replacement_file.shape[0]):
                        if word == replacement_file.iloc[raw, 0]:
                            word = replacement_file.iloc[raw, 1]
                            break

                # remove punctation and N° in one token (useless)
                # if word not in ['', '/', '-']:
                    tokenized_field_new.append(word)

            tokenized_fields.append(tokenized_field_new)
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
