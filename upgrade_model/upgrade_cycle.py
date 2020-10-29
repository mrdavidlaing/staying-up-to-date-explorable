import pandas as pd
from datetime import datetime
from datetime import date
from datetime import timedelta

from dataclasses import dataclass
from typing import List

@dataclass
class Environment:
    name:        str
    nodes:       int = 3
    pods:        int = 30

@dataclass
class EnvironmentGroup:
    name:         str
    environments: List[Environment]

def compute_next_upgrade_cycle(start_date:date, environment_groups:List[EnvironmentGroup]):
    ignore_days = 14
    plan_days = 1
    prework_days = 1

    df_steps = pd.DataFrame([
        dict(phase="Global", step="ignore",   start_date=start_date,                                         finish_date=start_date + timedelta(days=ignore_days)),
        dict(phase="Global", step="plan",     start_date=start_date + timedelta(days=ignore_days),           finish_date=start_date + timedelta(days=ignore_days+plan_days)),
        dict(phase="Global", step="pre-work", start_date=start_date + timedelta(days=ignore_days+plan_days), finish_date=start_date + timedelta(days=ignore_days+plan_days+prework_days)),
    ])

    for group in environment_groups:
        group_start_date = df_steps.finish_date.iloc[-1]
        for env in group.environments:
            wait_days        = 3 # TODO: compute dates until next maintenance window (eg: weekend)
            upgrade_days     = 1 # TODO: this should be based on the size of the environment
            recover_days     = 1 # TODO: this should be probability based

            df_steps = pd.concat([df_steps, 
                pd.DataFrame([
                    dict(phase=f"{group.name}: {env.name}", step="wait",     start_date=group_start_date,                                          finish_date=group_start_date + timedelta(days=wait_days)),
                    dict(phase=f"{group.name}: {env.name}", step="upgrade",  start_date=group_start_date + timedelta(days=wait_days),              finish_date=group_start_date + timedelta(days=wait_days+upgrade_days)),
                    dict(phase=f"{group.name}: {env.name}", step="recover",  start_date=group_start_date + timedelta(days=wait_days+upgrade_days), finish_date=group_start_date + timedelta(days=wait_days+upgrade_days+recover_days)),
                ])
            ])
 
    return df_steps.reset_index(drop=True)