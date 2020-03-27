import logging
from typing import Tuple, Callable, List

import numpy as np

from pandas_ml_common import Typing
from pandas_ml_common.utils import call_if_not_none, loc_if_not_none
from pandas_ml_utils.ml.data.splitting import Splitter

_log = logging.getLogger(__name__)


class Sampler(object):
    def __init__(self,
                 train: List[Typing.PatchedDataFrame],
                 test: List[Typing.PatchedDataFrame],
                 cross_validation: Tuple[int, Callable] = None):
        self.cross_validation = cross_validation
        self.train = train
        self.test = test

    def __getitem__(self, item) -> Tuple[Typing.PatchedDataFrame, Typing.PatchedDataFrame]:
        return self.train[item], self.test[item]

    def training(self) -> Tuple[List[np.ndarray], Typing.PdIndex]:
        return [t.ml.values if t is not None else None for t in self.train], self.train[0].index

    def validation(self) -> Tuple[List[np.ndarray], Typing.PdIndex]:
        return [t.ml.values if t is not None else None for t in self.test], self.test[0].index

    def sample(self) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        train = [t.ml.values if t is not None else None for t in self.train]
        test = [t.ml.values if t is not None else None for t in self.test]
        cv = self.cross_validation

        # add a default fold epoch of 1
        if callable(cv):
            cv = (1, cv)

        # loop through folds and yield data until done then raise StopIteration
        if cv is not None and isinstance(cv, Tuple) and callable(cv[1]):
            for fold_epoch in range(cv[0]):
                # cross validation, make sure we re-shuffle every fold_epoch
                for f, (train_idx, test_idx) in enumerate(cv[1](train[0], train[1])):
                    _log.info(f'fit fold {f}')
                    yield ([t[train_idx] if t is not None else None for t in train],
                           [t[test_idx] if t is not None else None for t in train])
        else:
            # fit without cross validation
            yield train, test


class DataGenerator(object):
    # the idea is to pass a yielding data generator to the "fit" method instad of x/y values
    # the cross validation loop goes as default implementation into to Model class.
    # this way each model can implement cross validation on their own and we can use the data generator for the gym

    def __init__(self, splitter: Splitter, *frames: Typing.PatchedDataFrame):
        self.splitter = splitter
        self.frames = frames

    def train_test_split(self) -> Sampler:
        train_idx, test_idx = self.splitter.train_test_split(self.frames[0].index)
        train = [loc_if_not_none(frame, train_idx) for frame in self.frames]
        test = [loc_if_not_none(frame, test_idx) for frame in self.frames]
        return Sampler(train, test, self.splitter.cross_validation)
