import numpy as np
from sklearn import decomposition
from sklearn.utils import check_array

from .base import BaseDetector, OneDimArray, TwoDimArray

__all__ = ['PCA']


class PCA(BaseDetector):
    """Outlier detector using Principal Component Analysis (PCA).

    Parameters
    ----------
    fpr : float, default 0.01
        False positive rate. Used to compute the threshold.

    kwargs : dict
        All other keyword arguments are passed to decomposition.PCA().

    Attributes
    ----------
    components_ : array-like of shape (n_components, n_features)
        Principal axes in feature space, representing the directions of maximum
        variance in the data.

    explained_variance_ : array-like of shape (n_components,)
        Amount of variance explained by each of the selected components.

    explained_variance_ratio_ : array-like of shape (n_components,)
        Percentage of variance explained by each of the selected components.

    mean_ : array-like of shape (n_features,)
        Per-feature empirical mean, estimated from the training set.

    noise_variance_ : float
        Estimated noise covariance following the Probabilistic PCA model from
        Tipping and Bishop 1999.

    n_components_ : int
        Estimated number of components.

    singular_values_ : array-like of shape (n_components,)
        Singular values corresponding to each of the selected components.

    threshold_ : float
        Threshold.

    X_ : array-like of shape (n_samples, n_features)
        Training data.
    """

    @property
    def components_(self) -> TwoDimArray:
        return self._pca.components_

    @property
    def explained_variance_(self) -> OneDimArray:
        return self._pca.explained_variance_

    @property
    def explained_variance_ratio_(self) -> OneDimArray:
        return self._pca.explained_variance_ratio_

    @property
    def mean_(self) -> OneDimArray:
        return self._pca.mean_

    @property
    def noise_variance_(self) -> float:
        return self._pca.noise_variance_

    @property
    def n_components_(self) -> int:
        return self._pca.n_components_

    @property
    def singular_values_(self) -> OneDimArray:
        return self._pca.singular_values_

    def __init__(self, fpr: float = 0.01, **kwargs) -> None:
        self.fpr  = fpr
        self._pca = decomposition.PCA(**kwargs)

        self.check_params()

    def check_params(self) -> None:
        """Check validity of parameters and raise ValueError if not valid."""

        if self.fpr < 0. or self.fpr > 1.:
            raise ValueError(
                f'fpr must be between 0.0 and 1.0 inclusive but was {self.fpr}'
            )

    def fit(self, X: TwoDimArray, y: OneDimArray = None) -> 'PCA':
        """Fit the model according to the given training data.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training data.

        y : ignored

        Returns
        -------
        self : PCA
            Return self.
        """

        self.X_         = check_array(X)

        self._pca.fit(self.X_)

        anomaly_score   = self.anomaly_score()
        self.threshold_ = np.percentile(anomaly_score, 100. * (1. - self.fpr))

        return self

    def reconstruct(self, X: TwoDimArray) -> OneDimArray:
        """Apply dimensionality reduction to the given data, and transform the
        data back to its original space.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Data.

        Returns
        -------
        X_rec : array-like of shape (n_samples, n_features)
        """

        return self._pca.inverse_transform(self._pca.transform(X))

    def anomaly_score(self, X: TwoDimArray = None) -> OneDimArray:
        """Compute the anomaly score for each sample.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features), default None
            Data.

        Returns
        -------
        anomaly_score : array-like of shape (n_samples,)
            Anomaly score for each sample.
        """

        if X is None:
            X = self.X_

        return np.sqrt(np.sum((X - self.reconstruct(X)) ** 2, axis=1))

    def score(self, X: TwoDimArray, y: OneDimArray = None) -> float:
        """Compute the mean log-likelihood of the given data.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Data.

        y : ignored

        Returns
        -------
        score : float
            Mean log-likelihood of the given data.
        """

        return self._pca.score(X)
