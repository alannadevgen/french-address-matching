from sklearn.model_selection import train_test_split
import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from utils.png_io import IOpng
from HMM.transition_matrix import TransitionMatrix
from time import time

class Emission:
    def __init__(self, tags):
        self.tags = tags

    def word_given_tags(self, word, list_tags):
        # count_tag = 0
        # count_tag_word = 0
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

    def compute_emission_word(self, word, smoothing=True, delta=1):
        tm = TransitionMatrix()
        info = tm.display_statistics(self.tags, print_all=False)
        list_tags = list(info[0])
        emission = np.zeros(len(list_tags))
        dict_tags = self.word_given_tags(word, list_tags)
        for i, t in enumerate(list_tags):
            res_word_given_tag = dict_tags[t]
            if smoothing:
                # perform a Laplace smoothing:
                emission[i] = (res_word_given_tag['count_tag_word'] + delta) \
                    / (res_word_given_tag['count_tag'] +
                       delta * len(list(info[1])))
            else:
                emission[i] = res_word_given_tag['count_tag_word'] \
                    / res_word_given_tag['count_tag']
        emission_df = pd.DataFrame(emission,
                                   columns=['probability_given_tag'],
                                   index=list_tags)
        return emission_df
