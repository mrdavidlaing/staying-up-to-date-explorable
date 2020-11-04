from io import StringIO
from datetime import datetime
import pandas as pd
from pandas._testing import assert_frame_equal

from upgrade_model import upgrade_cycle

def parse_steps(csv_data):
    return pd.read_csv(
      StringIO(csv_data), sep = r'\s+',
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
    # print("\n",steps)

    assert_frame_equal(steps.reset_index(drop=True), parse_steps('''
phase                 step       start_date   finish_date
Global                ignoring   2020-01-01  2020-01-15
Global                planning   2020-01-15  2020-01-16
Global                pre-work   2020-01-16  2020-01-17
"Group 1: Cluster 1"  waiting    2020-01-17  2020-01-18
"Group 1: Cluster 1"  upgrading  2020-01-18  2020-01-19
"Group 1: Cluster 1"  recovering 2020-01-19  2020-01-21
''').reset_index(drop=True))

def test_multi_group_and_cluster_should_contain_all_the_steps():

    steps = upgrade_cycle.compute_next_upgrade_cycle(
        start_date = datetime.fromisoformat('2020-01-01'),
        environment_groups = [
            upgrade_cycle.EnvironmentGroup(
            'Group 1',[
                upgrade_cycle.Environment('Cluster 1'),
                upgrade_cycle.Environment('Cluster 2'),
            ]),
            upgrade_cycle.EnvironmentGroup(
            'Group 2',[
                upgrade_cycle.Environment('Cluster 3'),
                upgrade_cycle.Environment('Cluster 4'),
            ]),
        ]
    )
    # print("\n",steps)

    assert_frame_equal(steps.reset_index(drop=True), parse_steps('''
phase                   step      start_date  finish_date
Global                  ignoring  2020-01-01  2020-01-15
Global                  planning  2020-01-15  2020-01-16
Global                  pre-work  2020-01-16  2020-01-17
"Group 1: Cluster 1"     waiting  2020-01-17  2020-01-18
"Group 1: Cluster 1"   upgrading  2020-01-18  2020-01-19
"Group 1: Cluster 1"  recovering  2020-01-19  2020-01-21
"Group 1: Cluster 2"     waiting  2020-01-17  2020-01-18
"Group 1: Cluster 2"   upgrading  2020-01-18  2020-01-19
"Group 1: Cluster 2"  recovering  2020-01-19  2020-01-21
"Group 2: Cluster 3"     waiting  2020-01-21  2020-01-25
"Group 2: Cluster 3"   upgrading  2020-01-25  2020-01-26
"Group 2: Cluster 3"  recovering  2020-01-26  2020-01-28
"Group 2: Cluster 4"     waiting  2020-01-21  2020-01-25
"Group 2: Cluster 4"   upgrading  2020-01-25  2020-01-26
"Group 2: Cluster 4"  recovering  2020-01-26  2020-01-28
''').reset_index(drop=True))


def test_chance_of_upgrade_failure():

    steps = upgrade_cycle.compute_next_upgrade_cycle(
        start_date = datetime.fromisoformat('2020-01-01'),
        environment_groups = [
            upgrade_cycle.EnvironmentGroup(
            'Group 1',[
                upgrade_cycle.Environment(f'Cluster {i+1}') for i in range(10) 
            ])
        ],
        upgrade_failure_percentage = 0.3
    )
    steps['step_length'] = steps.finish_date - steps.start_date

    recover_steps = steps[steps.step == 'recovering']
    # print("\n",recover_steps)

    assert len(recover_steps[recover_steps.step_length != '0 days']) == 3