import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from utils.png_io import IOpng
import io


class Performance:
    '''
    '''
    def __init__(self, sample, predictions):
        '''
        '''
        self.true_values = [adr[1] for adr in sample]
        self.predictions = predictions
        self.len_sample = len(sample)

        tags_true = [tag for address in sample for tag in address[1]]
        tags_pred = [tag for address in predictions for tag in address]
        self.tags_true = tags_true
        self.tags_pred = tags_pred

        list_set_tags = self.list_set_tag()
        self.set_tags_true = list_set_tags[0]
        self.set_tags_pred = list_set_tags[1]

    def list_set_tag(self):
        '''
        count the distinct tags present in the true distrib and in the pred
        '''
        list_tags = ['NUMVOIE', 'SUFFIXE', 'LIBVOIE', 'LIEU', 'CP', 'COMMUNE',
                     'COMPADR', 'PARCELLE', 'INCONNU', 'PERSO']
        list_tags_true_present = []
        list_tags_pred_present = []
        set_tags_true = list(set(self.tags_true))
        set_tags_pred = list(set(self.tags_pred))
        for tag_elem in list_tags:
            if tag_elem in set_tags_true:
                list_tags_true_present.append(tag_elem)
            if tag_elem in set_tags_pred:
                list_tags_pred_present.append(tag_elem)

        return (list_tags_true_present, list_tags_pred_present)

    def count_tags(self, set_tags, tags):
        '''
        compute frequency of each tag
        '''
        count_tags = np.zeros(len(set_tags))
        for tag in tags:
            if tag in set_tags:
                ind_vec = set_tags.index(tag)
                np.add.at(count_tags, [ind_vec], 1)
        return count_tags

    def count_true_pos(self):
        '''
        count the number of true positives
        '''
        assert len(self.tags_true) == len(self.tags_pred)
        len_vec = min(len(self.set_tags_true),
                      len(self.set_tags_pred))
        vec_true_pos = np.zeros(len_vec)
        if len_vec == len(self.set_tags_true):
            set_tags = self.set_tags_true
        else:
            set_tags = self.set_tags_pred
        for ind in range(len(self.tags_true)):
            if self.tags_true[ind] == self.tags_pred[ind]:
                ind_true_pos = set_tags.index(self.tags_true[ind])
                vec_true_pos[ind_true_pos] += 1
        return (vec_true_pos, set_tags)

    def matrix_performance(self):
        '''
        compute the performance matrix
        '''
        res_true_pos = self.count_true_pos()
        nb_true_pos = res_true_pos[0]
        list_tags = res_true_pos[1]
        nb_tags_true = self.count_tags(list_tags, self.tags_true)
        nb_tags_pred = self.count_tags(list_tags, self.tags_pred)

        precision = np.divide(nb_true_pos, nb_tags_pred)
        recall = np.divide(nb_true_pos, nb_tags_true)
        f1_score = (2 * (precision * recall)) / (precision + recall)
        performance = pd.DataFrame()
        performance['precision'] = np.round(precision, 3)
        performance['recall'] = np.round(recall, 3)
        performance['f1-score'] = np.round(f1_score, 3)
        performance.index = list_tags
        return performance

    def matrix_true_pred(self):
        '''
        compute the cross matrix between true tags and predicted tags
        '''
        count_tags_true = self.count_tags(self.set_tags_true, self.tags_true)
        assert len(self.tags_true) == len(self.tags_pred)
        matrix_count = np.zeros((len(self.set_tags_true),
                                 len(self.set_tags_pred)))
        for ind in range(len(self.tags_true)):
            ind_true = self.set_tags_true.index(self.tags_true[ind])
            ind_pred = self.set_tags_pred.index(self.tags_pred[ind])
            matrix_count[ind_true, ind_pred] += 1

        matrix_true_pred = np.dot(np.diag(1/count_tags_true),
                                  matrix_count)

        df_true_df = pd.DataFrame(
            np.round(matrix_true_pred, 3),
            columns=self.set_tags_pred, index=self.set_tags_true
            )
        return df_true_df

    def rate_correct_tagged(self):
        '''
        compute the rate of corrected predicted tags
        '''
        nb_good_addresses = 0
        nb_bad_addresses = 0
        for ind_adr, adr in enumerate(self.predictions):
            nb_good_tokens = 0
            for ind_token, token in enumerate(adr):
                if token == self.true_values[ind_adr][ind_token]:
                    nb_good_tokens += 1
            if nb_good_tokens == len(adr):
                nb_good_addresses += 1
            else:
                nb_bad_addresses += 1
        rate_correct_addresses = round(nb_good_addresses / self.len_sample, 3)
        rate_bad_addresses = round(nb_bad_addresses / self.len_sample, 3)
        return (rate_correct_addresses, rate_bad_addresses)

    def autolabel(self, ax, rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8)

    def plot_distrib_tags(self):
        '''
        plot the distribution of the tags
        '''
        fig = plt.figure()
        ax = fig.add_axes([0, 0, 1, 1])
        list_tags = ['NUMVOIE', 'SUFFIXE', 'LIBVOIE', 'LIEU', 'CP', 'COMMUNE',
                     'COMPADR', 'PARCELLE', 'INCONNU']
        title = 'Distribution of the true and the predicted tags'
        nb_tags_true = self.count_tags(list_tags, self.tags_true)
        nb_tags_pred = self.count_tags(list_tags, self.tags_pred)

        ind = np.arange(len(list_tags))  # the x locations for the groups
        width = 0.4

        rects_true = ax.bar(ind - width/2, np.int_(nb_tags_true), width, label='true')
        rects_pred = ax.bar(ind + width/2, np.int_(nb_tags_pred), width, label='predicted')

        plt.title(title, weight="bold",
                  size=16)
        plt.draw()
        ax.set_xticks([i for i in range(len(list_tags))])
        ax.set_xticklabels(list_tags, rotation=30, ha='right')
        # ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha='right')
        ax.set_ylabel('Number of tags')
        self.autolabel(ax, rects_true)
        self.autolabel(ax, rects_pred)
        img_data = io.BytesIO()
        plt.savefig(img_data, format='png', bbox_inches='tight')
        img_data.seek(0)
        return img_data

    def save_barplot(self, image, bucket, file):
        png_file_io = IOpng()
        png_file_io.export_file(image=image, bucket=bucket, file_key_s3=file)
