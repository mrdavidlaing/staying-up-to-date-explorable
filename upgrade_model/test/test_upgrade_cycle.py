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
Global                ignore     2020-01-01  2020-01-15
Global                plan       2020-01-15  2020-01-16
Global                pre-work   2020-01-16  2020-01-17
"Group 1: Cluster 1"  wait       2020-01-17  2020-01-20
"Group 1: Cluster 1"  upgrade    2020-01-20  2020-01-21
"Group 1: Cluster 1"  recover    2020-01-21  2020-01-22
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
phase                  step    start_date  finish_date
Global                 ignore  2020-01-01  2020-01-15
Global                   plan  2020-01-15  2020-01-16
Global               pre-work  2020-01-16  2020-01-17
"Group 1: Cluster 1"     wait  2020-01-17  2020-01-20
"Group 1: Cluster 1"  upgrade  2020-01-20  2020-01-21
"Group 1: Cluster 1"  recover  2020-01-21  2020-01-22
"Group 1: Cluster 2"     wait  2020-01-17  2020-01-20
"Group 1: Cluster 2"  upgrade  2020-01-20  2020-01-21
"Group 1: Cluster 2"  recover  2020-01-21  2020-01-22
"Group 2: Cluster 3"     wait  2020-01-22  2020-01-25
"Group 2: Cluster 3"  upgrade  2020-01-25  2020-01-26
"Group 2: Cluster 3"  recover  2020-01-26  2020-01-27
"Group 2: Cluster 4"    wait   2020-01-22  2020-01-25
"Group 2: Cluster 4"  upgrade  2020-01-25  2020-01-26
"Group 2: Cluster 4"  recover  2020-01-26  2020-01-27
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

    recover_steps = steps[steps.step == 'recover']
    # print("\n",recover_steps)

    assert len(recover_steps[recover_steps.step_length != '0 days']) == 3