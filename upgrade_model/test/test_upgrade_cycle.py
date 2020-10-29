from io import StringIO
import pandas as pd
from pandas._testing import assert_frame_equal
from datetime import datetime

from upgrade_model import upgrade_cycle

def parse_steps(csv_data):
    return pd.read_csv(
      StringIO(csv_data), sep = '\s+',
      parse_dates=['start_date', 'finish_date']
    )

def test_single_cluster_should_contain_all_the_steps():

    steps = upgrade_cycle.compute_next_upgrade_cycle(
        start_date = datetime.fromisoformat('2020-01-01'),
        environment_groups = [
            upgrade_cycle.EnvironmentGroup(
            'Group 1',[
                upgrade_cycle.Environment('Cluster 1')
            ])
        ]
    )
    print("\n",steps)

    assert_frame_equal(steps.reset_index(drop=True), parse_steps('''
phase                 step       start_date   finish_date
Global                ignore     2020-01-01  2020-01-15
Global                plan       2020-01-15  2020-01-16
Global                pre-work   2020-01-16  2020-01-17
"Group 1: Cluster 1"  wait       2020-01-17  2020-01-20
"Group 1: Cluster 1"  upgrade    2020-01-20  2020-01-21
"Group 1: Cluster 1"  recover    2020-01-21  2020-01-22
''').reset_index(drop=True))