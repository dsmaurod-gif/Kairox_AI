import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

class Winsorizador(BaseEstimator, TransformerMixin):
    def __init__(self, inferior=0.01, superior=0.99):
        self.inferior = inferior
        self.superior = superior
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=float)
        self.lim_inf_ = np.nanquantile(X, self.inferior, axis=0)
        self.lim_sup_ = np.nanquantile(X, self.superior, axis=0)
        return self
    def transform(self, X):
        return np.clip(np.asarray(X, dtype=float), self.lim_inf_, self.lim_sup_)
