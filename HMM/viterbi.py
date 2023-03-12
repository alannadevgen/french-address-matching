from sklearn.model_selection import train_test_split
import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from utils.png_io import IOpng
from HMM.transition_matrix import TransitionMatrix
from HMM.emission import Emission
from time import time


class Viterbi:
    def __init__(self, tags):
        tm = TransitionMatrix()
        transition_matrix = tm.compute_transition_matrix(tags)
        self.list_tags = tm.list_tags
        self.transition = np.matrix(transition_matrix)[1:, :]
        self.emission = Emission(tags)
        self.list_states = transition_matrix.columns
        self.init_distrib = np.matrix(transition_matrix)[0, :].flatten()

    def solve_viterbi(self, observed_sequence, smoothing='laplace', delta=1):
        '''
        Viterbi algorithm
        '''
        nb_states = self.transition.shape[0]
        len_seq = len(observed_sequence)

        proba_matrix = np.zeros((nb_states, len_seq))
        optimal = np.zeros((nb_states, len_seq - 1)).astype(np.int32)
        vec_emission_first_word = np.array(self.emission.compute_emission_word(
            observed_sequence[0], smoothing=smoothing
        )).flatten()
        proba_matrix[:, 0] = np.multiply(self.init_distrib,
                                         vec_emission_first_word)

        for token in range(1, len_seq):
            vec_emission_word = self.emission.compute_emission_word(
                    observed_sequence[token], smoothing=smoothing, delta=delta
                    )
            for state in range(nb_states):
                temp_prod = np.multiply(self.transition[:, state].flatten(),
                                        proba_matrix[:, token-1])
                current_state = self.list_states[state]
                proba_emission_word =\
                    vec_emission_word.loc[current_state,
                                          'probability_given_tag']
                proba_matrix[state, token] = np.max(temp_prod) *\
                    proba_emission_word

                optimal[state, token-1] = np.argmax(temp_prod)

        # Backtracking
        optimal_state_seq = np.zeros(len_seq).astype(np.int32)
        optimal_state_seq[-1] = np.argmax(proba_matrix[:, -1])
        for token in range(len_seq - 2, -1, -1):
            optimal_state_seq[token] =\
                optimal[int(optimal_state_seq[token+1]), token]

        optimal_seq_text = []
        for elem in optimal_state_seq:
            optimal_seq_text.append(self.list_states[elem])

        return optimal_seq_text

    def predict(self, test_sample, smoothing='laplace', delta=1):
        res_predictions = []
        for addresse in test_sample:
            res = self.solve_viterbi(addresse[0], smoothing, delta)
            res_predictions.append(res)
        return res_predictions
