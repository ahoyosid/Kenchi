import doctest
import unittest

import matplotlib
import matplotlib.axes
import numpy as np
from sklearn.exceptions import NotFittedError
from sklearn.utils.estimator_checks import check_estimator

from kenchi.datasets import make_blobs
from kenchi.outlier_detection import density_based

matplotlib.use('Agg')

import matplotlib.pyplot as plt


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(density_based))

    return tests


class LOFTest(unittest.TestCase):
    def setUp(self):
        self.X, self.y = make_blobs(random_state=0)
        self.sut       = density_based.LOF(n_neighbors=3)
        _, self.ax     = plt.subplots()

    def tearDown(self):
        plt.close()

    @unittest.skip('this test fail in scikit-learn 0.19.1')
    def test_check_estimator(self):
        self.assertIsNone(check_estimator(self.sut))

    def test_fit(self):
        self.assertIsInstance(self.sut.fit(self.X), density_based.LOF)

    def test_fit_predict(self):
        self.assertIsInstance(self.sut.fit_predict(self.X), np.ndarray)

    def test_anomaly_score_notfitted(self):
        with self.assertRaises(NotFittedError):
            self.sut.anomaly_score(self.X)

    def test_predict_notfitted(self):
        with self.assertRaises(NotFittedError):
            self.sut.predict(self.X)

    def test_score(self):
        self.assertIsInstance(
            self.sut.set_params(novelty=True).fit(self.X).score(), float
        )

    def test_plot_anomaly_score(self):
        self.assertIsInstance(
            self.sut.fit(self.X).plot_anomaly_score(ax=self.ax),
            matplotlib.axes.Axes
        )

    @unittest.skip('this test fail in scikit-larn 0.19.1')
    def test_plot_roc_curve(self):
        self.assertIsInstance(
            self.sut.fit(self.X).plot_roc_curve(self.X, self.y, ax=self.ax),
            matplotlib.axes.Axes
        )
