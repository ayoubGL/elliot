"""
This is the implementation of the normalized Discounted Cumulative Gain metric.
It proceeds from a user-wise computation, and average the values over the users.
"""

__version__ = '0.1'
__author__ = 'Vito Walter Anelli, Claudio Pomo, Alejandro Bellogín'
__email__ = 'vitowalter.anelli@poliba.it, claudio.pomo@poliba.it, alejandro.bellogin@uam.es'

import typing as t

from elliot.evaluation.metrics.base_metric import BaseMetric
from elliot.evaluation.relevance import Relevance


class NDCG(BaseMetric):
    """
    This class represents the implementation of the nDCG recommendation metric.
    Passing 'nDCG' to the metrics list will enable the computation of the metric.
    """

    def __init__(self, recommendations, config, params, eval_objects):
        """
        Constructor
        :param recommendations: list of recommendations in the form {user: [(item1,value1),...]}
        :param config: SimpleNameSpace that represents the configuration of the experiment
        :param params: Parameters of the model
        :param eval_objects: list of objects that may be useful for the computation of the different metrics
        """
        super().__init__(recommendations, config, params, eval_objects)
        self._cutoff = self._evaluation_objects.cutoff
        self._relevance_map = self._evaluation_objects.relevance.get_discounted_relevance()
        self.rel_threshold = self._evaluation_objects.relevance._rel_threshold

    @staticmethod
    def name():
        """
        Metric Name Getter
        :return: returns the public name of the metric
        """
        return "nDCG"

    @staticmethod
    def compute_discount(k: int) -> float:
        """
        Method to compute logarithmic discount
        :param k:
        :return:
        """
        return Relevance.logarithmic_ranking_discount(k)

    @staticmethod
    def compute_idcg(gain_map: t.Dict, cutoff: int) -> float:
        """
        Method to compute Ideal Discounted Cumulative Gain
        :param gain_map:
        :param cutoff:
        :return:
        """
        gains: t.List = sorted(list(gain_map.values()))
        n: int = min(len(gains), cutoff)
        m: int = len(gains)
        return sum(map(lambda g, r: gains[m - r - 1] * NDCG.compute_discount(r), gains, range(n)))

    @staticmethod
    def compute_user_ndcg(user_recommendations: t.List, user_gain_map: t.Dict, cutoff: int) -> float:
        """
        Method to compute normalized Discounted Cumulative Gain
        :param sorted_item_predictions:
        :param gain_map:
        :param cutoff:
        :return:
        """
        idcg: float = NDCG.compute_idcg(user_gain_map, cutoff)
        dcg: float = sum(
            [user_gain_map.get(x, 0) * NDCG.compute_discount(r)
             for r, x in enumerate([item for item, _ in user_recommendations]) if r < cutoff])
        return dcg / idcg if dcg > 0 else 0

    @staticmethod
    def __user_ndcg(user_recommendations: t.List, user_gain_map: t.Dict, cutoff: int):
        """
        Per User normalized Discounted Cumulative Gain
        :param user_recommendations: list of user recommendation in the form [(item1,value1),...]
        :param user_gain_map: dict of discounted relevant items in the form {user1:{item1:value1,...},...}
        :param cutoff: numerical threshold to limit the recommendation list
        :return: the value of the nDCG metric for the specific user
        """

        ndcg: float = NDCG.compute_user_ndcg(user_recommendations[:cutoff], user_gain_map, cutoff)

        return ndcg

    # def eval(self):
    #     """
    #     Evaluation function
    #     :return: the overall averaged value of normalized Discounted Cumulative Gain
    #     """
    #
    #     return np.average(
    #         [NDCG.__user_ndcg(u_r, self._relevance_map[u], self._cutoff)
    #          for u, u_r in self._recommendations.items() if len(self._relevance_map[u])]
    #     )

    def eval_user_metric(self):
        """
        Evaluation function
        :return: the overall averaged value of normalized Discounted Cumulative Gain per user
        """

        return {u: NDCG.__user_ndcg(u_r, self._relevance_map[u], self._cutoff)
             for u, u_r in self._recommendations.items() if len(self._relevance_map[u])}





