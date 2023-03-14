from random import sample, shuffle


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
        train_sample = [self.init_sample[index] for index in train_indexes]
        test_sample = [self.init_sample[index] for index in indexes if index
                       not in train_indexes]
        return (train_sample, test_sample)

    def split_cv(self, k=10):
        '''
        '''
        init_sample_size = len(self.init_sample)
        indexes = [i for i in range(init_sample_size)]
        validation_size = init_sample_size // k
        used_sample_size = validation_size * k
        indexes_to_shuffle = indexes[0:used_sample_size]
        shuffle(indexes_to_shuffle)
        validation_sample = []
        for i in range(0, used_sample_size, validation_size):
            cv_indexes = indexes_to_shuffle[i:i+validation_size]
            cv_sample = [self.init_sample[index] for index in cv_indexes]
            validation_sample.append(cv_sample)
        return validation_sample
