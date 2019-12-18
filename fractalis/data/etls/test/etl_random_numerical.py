"""This module provides sample data."""

import pandas as pd
import numpy as np
import string
import random

from fractalis.data.etl import ETL
from fractalis.data_services_config import Handler


class RandomNumericalETL(ETL):

    name = 'test_numerical_etl'
    produces = 'numerical'

    @staticmethod
    def can_handle(handler: Handler, descriptor: dict) -> bool:
        return handler == Handler.TEST and \
               descriptor['data_type'] == 'numerical'

    def extract(self, server: str,
                token: str, descriptor: dict) -> pd.DataFrame:
        feature = ''.join(random.choice(string.ascii_letters + string.digits)
                          for _ in range(30))
        data = pd.DataFrame(
            np.random.randn(descriptor['num_samples']).tolist(),
            columns=[feature])
        return data

    def transform(self, raw_data: pd.DataFrame,
                  descriptor: dict) -> pd.DataFrame:
        raw_data.insert(0, 'id', raw_data.index.astype('str'))
        df = pd.melt(raw_data, id_vars='id', var_name='feature')
        return df
