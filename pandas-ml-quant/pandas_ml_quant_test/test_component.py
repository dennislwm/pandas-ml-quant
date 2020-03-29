from unittest import TestCase

import pandas_ml_quant
from pandas_ml_quant_test.config import DF_TEST

print(pandas_ml_quant.__version__)


class TestQuantComponent(TestCase):

    def test_all_analysis_functions(self):
        df = DF_TEST.copy()

        ta_functions = [ta for ta in dir(df.q) if ta.startswith("ta_")]
        self.assertEqual(44, len(ta_functions))

        # FIXME call all functions
        df.q.ta_sma(20)
        pass