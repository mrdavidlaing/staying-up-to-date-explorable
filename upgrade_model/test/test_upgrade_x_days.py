from io import StringIO
import pandas as pd
from pandas._testing import assert_frame_equal

from upgrade_model import upgrade_every_x_days

def parse_environment_state(csv_data):
    TESTDATA = StringIO(csv_data)
    return pd.read_csv(
      TESTDATA, sep = r'\s+',
      parse_dates=['at_date', 'release_date', 'end_of_support_date']
    )

def rows_with_changes_in(df, column):
    return df[df[column].ne(df[column].shift())]

def test_should_generate_a_row_for_every_day():
    environment_state = upgrade_every_x_days.compute(
        id='upgrade-every-90-days', start_date='2018-01-01', end_date='2019-01-01', 
        first_version='1.9.0', upgrade_every=90
    )
    # print("\n",environment_state.tail(10))
    assert len(environment_state)==366

def test_should_change_version_every_upgrade():
    environment_state = upgrade_every_x_days.compute(
        id='upgrade-every-30-days', start_date='2018-01-01', end_date='2018-03-15', 
        first_version='1.7.0', upgrade_every=30
    )
    # print("\n",rows_with_changes_in(environment_state,'version'))
    
    assert_frame_equal(rows_with_changes_in(environment_state,'version').reset_index(drop=True), parse_environment_state('''
environment_id          at_date     version release_date  end_of_support_date  release_age
upgrade-every-30-days   2018-01-01   1.7.0  2017-06-30    2018-03-26           185
upgrade-every-30-days   2018-01-31   1.8.0  2017-09-29    2018-06-27           124
upgrade-every-30-days   2018-03-02   1.9.0  2017-12-15    2018-09-27           77
''').reset_index(drop=True))

def test_should_not_upgrade_if_new_version_not_available():
    environment_state = upgrade_every_x_days.compute(
        id='upgrade-every-1-day', start_date='2018-01-01', end_date='2018-10-01', 
        first_version='1.8.0', upgrade_every=1
    )
    #print("\n",rows_with_changes_in(environment_state,'version'))
    
    assert_frame_equal(rows_with_changes_in(environment_state,'version').reset_index(drop=True), parse_environment_state('''
environment_id      at_date     version  release_date end_of_support_date  release_age
upgrade-every-1-day 2018-01-01   1.8.0   2017-09-29   2018-06-27           94
upgrade-every-1-day 2018-01-02   1.9.0   2017-12-15   2018-09-27           18
upgrade-every-1-day 2018-03-26  1.10.0   2018-03-26   2018-12-03            0
upgrade-every-1-day 2018-06-27  1.11.0   2018-06-27   2019-03-25            0
upgrade-every-1-day 2018-09-27  1.12.0   2018-09-27   2019-06-19            0
''').reset_index(drop=True))