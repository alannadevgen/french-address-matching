from sklearn.model_selection import train_test_split
import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from utils.png_io import IOpng
from HMM.transition_matrix import TransitionMatrix

class Emission:
    def __init__(self, tags):
        self.tags = tags

    def word_given_tag(self, word, tag):
        count_tag = 0
        count_tag_word = 0
        for addresse in self.tags:
            for index_tag_adr in range(len(addresse[0])):
                if addresse[1][index_tag_adr] == tag:
                    count_tag += 1
                if addresse[0][index_tag_adr] == word and\
                        addresse[1][index_tag_adr] == tag:
                    count_tag_word += 1
        return (count_tag_word, count_tag)

    def compute_emission_word(self, word):
        tm = TransitionMatrix()
        info = tm.display_statistics(self.tags, print_all=False)
        list_tags = list(info[0])
        emission = np.zeros(len(list_tags))
        for i, t in enumerate(list_tags):
            res_word_given_tag = self.word_given_tag(word, t)
            emission[i] = res_word_given_tag[0] / res_word_given_tag[1]
        emission_df = pd.DataFrame(emission,
                                   columns=['probability_given_tag'],
                                   index=list_tags)
        return emission_df
