import numpy as np
import pandas as pd
from HMM.transition_matrix import TransitionMatrix


class Emission:
    def __init__(self, tags):
        self.tags = tags

    def word_given_tags(self, word, list_tags):
        '''
        compute statistics used in the emission probability
        '''
        dict_tags = {}
        for i, t in enumerate(list_tags):
            dict_tags[t] = {}
            dict_tags[t]['count_tag_word'] = 0
            dict_tags[t]['count_tag'] = 0
        for addresse in self.tags:
            for index_tag_adr in range(len(addresse[0])):
                tag_adr = addresse[1][index_tag_adr]
                dict_tags[tag_adr]['count_tag'] += 1
                if addresse[0][index_tag_adr] == word:
                    dict_tags[tag_adr]['count_tag_word'] += 1
        return dict_tags

    def compute_emission_word(self, word, smoothing='laplace', delta=1):
        '''
        compute emission probabilities for a given token
        '''
        tm = TransitionMatrix()
        info = tm.display_statistics(self.tags, print_all=False)
        list_tags = list(info[0])
        emission = np.zeros(len(list_tags))
        dict_tags = self.word_given_tags(word, list_tags)
        for i, t in enumerate(list_tags):
            res_word_given_tag = dict_tags[t]
            if smoothing == 'laplace':
                # perform a Laplace smoothing:
                emission[i] = (res_word_given_tag['count_tag_word'] + delta) \
                    / (res_word_given_tag['count_tag'] +
                       delta * len(list(info[1])))
            else:
                # no smoothing
                emission[i] = res_word_given_tag['count_tag_word'] \
                        / res_word_given_tag['count_tag']
        emission_df = pd.DataFrame(emission,
                                   columns=['probability_given_tag'],
                                   index=list_tags)
        return emission_df
