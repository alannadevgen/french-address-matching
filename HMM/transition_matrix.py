from sklearn.model_selection import train_test_split
import io
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from utils.png_io import IOpng


class TransitionMatrix:
    def __init__(self, file="transition_matrix.png"):
        self.file = file

    def create_train_test_sample(self, tags):
        train_set, test_set = train_test_split(tags, train_size=0.75)
        return (train_set, train_set)

    def display_statistics(self, tags):
        tokens = [token for address in tags for token in address[0]]
        vocabulary = set(tokens)
        nb_distinct_vocab = len(vocabulary)
        tags = [tag for address in tags for tag in address[1]]
        set_tags = list(set(tags))
        list_tags = ['NUMVOIE', 'SUFFIXE', 'LIBVOIE', 'LIEU', 'CP', 'COMMUNE',
                     'COMPADR', 'PARCELLE', 'INCONNU']
        if 'PERSO' in set_tags:
            list_tags.append('PERSO')
        nb_distinct_tags = len(list_tags)
        print(f'Number of tokens in the train sample: {len(tokens)}')
        print(f'Number of distinct tokens in the train sample: {nb_distinct_vocab}')
        print(f'Number of distinct tags: {nb_distinct_tags}')
        distribution_tags = {}
        for elem in list_tags:
            distribution_tags[elem] = 0
            for tag in tags:
                if tag == elem:
                    distribution_tags[elem] += 1
        print("\n----------------------------------------------------------------------------------------------------------------\n")
        print('Number of tokens for each tag:')
        for tag, number in distribution_tags.items():
            print("  ", tag, ":", number)
        return (list_tags, vocabulary)

    def t2_given_t1(self, t1, t2, tags):
        count_t1 = 0
        count_t1_t2 = 0
        for address in tags:
            # for tag in address[1]:
            #     if tag == t1:
            #         count_t1 += 1
            for index_tag in range(1, len(address[1])):
                if address[1][index_tag] == t2 and address[1][index_tag-1] == t1:
                    count_t1_t2 += 1
                if address[1][index_tag-1] == t1:
                    count_t1 += 1

        return (count_t1_t2, count_t1)

    def compute_transition_matrix(self, tags):
        info = self.display_statistics(tags)
        set_tags = info[0]
        nb_distinct_tags = len(info[0])

        # nb_distinct_vocab = len(info[1])
        tags_matrix = np.zeros(
            (nb_distinct_tags, nb_distinct_tags), dtype='float32'
            )
        for i, t1 in enumerate(list(set_tags)):
            for j, t2 in enumerate(list(set_tags)):
                tags_matrix[i, j] = self.t2_given_t1(t1, t2, tags)[0] /\
                    self.t2_given_t1(t1, t2, tags)[1]

        # convert the matrix to a df for better readability
        tags_df = pd.DataFrame(
            tags_matrix,
            columns=list(set_tags), index=list(set_tags)
            )
        return tags_df

    def plot_transition_matrix(self, transition_matrix, file=None):
        if file is None:
            file = self.file
        # plot the transition matrix
        heatmap = sns.heatmap(transition_matrix, cmap="Blues", annot=True, fmt=".1f")
        # add title
        plt.title('Transition matrix', weight="bold", size=16)
        # ajust margins
        plt.tight_layout()
        # add text if >= 0.5
        heatmap.set_xticklabels(heatmap.get_xticklabels(), rotation=60)
        for t in heatmap.texts:
            if float(t.get_text()) >= 0.5:
                t.set_text(t.get_text())
            else:
                t.set_text("")
                # if not it sets an empty text

        # save file
        plt.savefig(file)
        img_data = io.BytesIO()
        plt.savefig(img_data, format='png', bbox_inches='tight')
        img_data.seek(0)
        return img_data

    def save_transition_matrix(self, image, bucket, file=None):
        if file is None:
            file = self.file
        png_file_io = IOpng()
        png_file_io.export_file(image=image, bucket=bucket, file_key_s3=file)
