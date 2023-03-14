import numpy as np
from HMM.split_sample import SplitSample
from HMM.viterbi import Viterbi
from HMM.performance import Performance


class CrossValidation:
    def __init__(self, train, delta, k=10):
        sp = SplitSample(train)
        self.samples = sp.split_cv(k=k)
        self.delta = delta

    def find_parameters_cv(self):
        '''
        '''
        rate_error_delta = []
        for param in self.delta:
            rate_error_param = []
            for test in self.samples:
                train = [
                    adr for sample in self.samples for adr in sample
                    if sample != test
                    ]
                viterbi = Viterbi(train)
                predictions = viterbi.predict(test, delta=param)
                perf = Performance(test, predictions)
                bad_class = perf.rate_correct_tagged()[1]
                rate_error_param.append(bad_class)
            rate_error_delta.append(np.mean(rate_error_param))
        delta_ind = np.argmin(rate_error_delta)
        optimal_delta = self.delta[delta_ind]
        return optimal_delta
