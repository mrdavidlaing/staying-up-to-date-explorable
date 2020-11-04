import pandas as pd
from datetime import datetime
from datetime import date
from datetime import timedelta
import random
import uuid
import calendar

from dataclasses import dataclass
from typing import List

@dataclass
class Environment:
    name:        str
    nodes:       int = 3
    pods:        int = 30
    id:          uuid = None

    def __post_init__(self):
        if self.id == None:
            self.id = uuid.uuid4()

@dataclass
class EnvironmentGroup:
    name:         str
    environments: List[Environment]

def compute_next_upgrade_cycle(start_date:date, environment_groups:List[EnvironmentGroup], upgrade_failure_percentage=1, maintenance_window='weekends'):
    ignore_days = 14
    plan_days = 1
    prework_days = 1

    df_steps = pd.DataFrame([
        dict(phase="Global", step="ignoring", start_date=start_date,                                         finish_date=start_date + timedelta(days=ignore_days)),
        dict(phase="Global", step="planning", start_date=start_date + timedelta(days=ignore_days),           finish_date=start_date + timedelta(days=ignore_days+plan_days)),
        dict(phase="Global", step="pre-work", start_date=start_date + timedelta(days=ignore_days+plan_days), finish_date=start_date + timedelta(days=ignore_days+plan_days+prework_days)),
    ])

    all_envs = []
    for group in environment_groups:
        all_envs.extend([env for env in group.environments])
    envs_with_upgrade_failures = random.sample(all_envs, round(len(all_envs)*upgrade_failure_percentage))
    
    for group in environment_groups:
        group_start_date = df_steps.finish_date.max()
        for env in group.environments:
            upgrade_days     = 1 # TODO: this should be based on the size of the environment
           
            if maintenance_window == 'weekends':
                wait_days = max(0,calendar.SATURDAY - group_start_date.weekday()) #days til Sat or 0 if Sunday
            else:
                wait_days = 0
           
            if env in envs_with_upgrade_failures:
                recover_days = 1 + upgrade_days # Assume recover takes 1 day + having to rerun original upgrade
            else:
                recover_days = 0

            df_steps = pd.concat([df_steps, 
                pd.DataFrame([
                    dict(phase=f"{group.name}: {env.name}", step="waiting",    start_date=group_start_date,                                          finish_date=group_start_date + timedelta(days=wait_days)),
                    dict(phase=f"{group.name}: {env.name}", step="upgrading",  start_date=group_start_date + timedelta(days=wait_days),              finish_date=group_start_date + timedelta(days=wait_days+upgrade_days)),
                    dict(phase=f"{group.name}: {env.name}", step="recovering", start_date=group_start_date + timedelta(days=wait_days+upgrade_days), finish_date=group_start_date + timedelta(days=wait_days+upgrade_days+recover_days)),
                ])
            ])
 
    return df_steps.reset_index(drop=True)