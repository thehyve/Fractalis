import pandas as pd
import numpy as np

from fractalis.data.etl import ETL


class BarETL(ETL):

    name = 'test_bar_task'
    _HANDLER = 'test'
    _DATA_TYPE = 'bar'

    def extract(self, server, token, descriptor):
        fake_raw_data = np.random.randn(10, 5)
        return fake_raw_data

    def transform(self, raw_data):
        fake_df = pd.DataFrame(raw_data)
        return fake_df
