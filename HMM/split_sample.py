from random import sample


class SplitSample:
    def __init__(self, init_sample):
        self.init_sample = init_sample

    def split(self, train_size=0.8):
        '''
        '''
        init_sample_size = len(self.init_sample)
        indexes = [i for i in range(init_sample_size)]
        nb_indexes = round(train_size * init_sample_size)
        train_indexes = sample(indexes, nb_indexes)
        # test_indexes = [i for i in range(init_sample_size)
        #                 if i not in train_indexes]
        train_sample = [self.init_sample[index] for index in train_indexes]
        test_sample = [self.init_sample[index] for index in indexes if index
                       not in train_indexes]
        return (train_sample, test_sample)
