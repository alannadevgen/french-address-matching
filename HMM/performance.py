import numpy as np
import pandas as pd


class Performance:
    def __init__(self, sample, predictions):
        self.true_values = [adr[1] for adr in sample]
        self.predictions = predictions
        self.len_sample = len(sample)
        tags_true = [tag for address in sample for tag in address[1]]
        tags_pred = [tag for address in predictions for tag in address]
        self.tags_true = tags_true
        self.tags_pred = tags_pred
        list_tags = ['NUMVOIE', 'SUFFIXE', 'LIBVOIE', 'LIEU', 'CP', 'COMMUNE',
                     'COMPADR', 'PARCELLE', 'INCONNU', 'PERSO']
        list_tags_true_present = []
        list_tags_pred_present = []
        set_tags_true = list(set(tags_true))
        set_tags_pred = list(set(tags_pred))
        for tag_elem in list_tags:
            if tag_elem in set_tags_true:
                list_tags_true_present.append(tag_elem)
            if tag_elem in set_tags_pred:
                list_tags_pred_present.append(tag_elem)

        self.set_tags_true = list_tags_true_present
        self.set_tags_pred = list_tags_pred_present

    def count_tags(self, set_tags, tags):
        count_tags = np.zeros(len(set_tags))
        for tag in tags:
            ind_vec = set_tags.index(tag)
            np.add.at(count_tags, [ind_vec], 1)
        return count_tags

    def matrix_true_pred(self):
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
            matrix_true_pred,
            columns=self.set_tags_pred, index=self.set_tags_true
            )
        return df_true_df

    def rate_correct_tagged(self):
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
