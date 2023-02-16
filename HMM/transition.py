from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd


def create_train_test_sample(tags):
    train_set, test_set = train_test_split(tags, train_size=0.75)
    return (train_set, train_set)


def display_statistics(tags):
    tokens = [token for address in tags for token in address[0]]
    vocabulary = set(tokens)
    nb_distinct_vocab = len(vocabulary)
    tags = [tag for address in tags for tag in address[1]]
    print(tags[0:10])
    set_tags = set(tags)
    nb_distinct_tags = len(set_tags)
    print(f'Number of tokens in the train sample: {len(tokens)}')
    print(f'Number of distinct tokens in the train sample: \
        {nb_distinct_vocab}')
    print(f'Number of distinct tags: {nb_distinct_tags}')
    distribution_tags = {}
    for elem in set_tags:
        distribution_tags[elem] = 0
        for tag in tags:
            if tag == elem:
                distribution_tags[elem] += 1
    print('Number of tokens for each tag:\n', distribution_tags)
    return (set_tags, vocabulary)


def t2_given_t1(t1, t2, tags):
    count_t1 = 0
    count_t1_t2 = 0
    for address in tags:
        for tag in address[1]:
            if tag == t1:
                count_t1 += 1
        for index_tag in range(1, len(address[1])):
            if address[1][index_tag] == t2 and address[1][index_tag-1] == t1:
                count_t1_t2 += 1
    return (count_t1_t2, count_t1)


def compute_transition_matrix(tags):
    info = display_statistics(tags)
    set_tags = info[0]
    nb_distinct_tags = len(info[0])

    # nb_distinct_vocab = len(info[1])
    tags_matrix = np.zeros(
        (nb_distinct_tags, nb_distinct_tags), dtype='float32'
        )
    for i, t1 in enumerate(list(set_tags)):
        for j, t2 in enumerate(list(set_tags)):
            tags_matrix[i, j] = t2_given_t1(t1, t2, tags)[0] /\
                t2_given_t1(t1, t2, tags)[1]

    # convert the matrix to a df for better readability
    tags_df = pd.DataFrame(
        tags_matrix,
        columns=list(set_tags), index=list(set_tags)
        )
    return tags_df
