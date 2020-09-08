import pandas as pd

from upgrade_model import remain_on_latest

def test_should_generate_a_row_for_every_day():
    environment_state = remain_on_latest.compute(id='remain-on-latest', start_date='2018-01-01', end_date='2019-01-01')
    #print("\n",environment_state.tail(10))
    assert len(environment_state)==366
