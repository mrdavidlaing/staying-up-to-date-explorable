import pandas as pd
from upgrade_model import k8s_releases_loader

k8s_releases = k8s_releases_loader.load()

def compute(id, start_date, end_date, first_version, upgrade_every):
    months = pd.date_range(start=start_date, end=end_date, freq='D')
    
    environment_ids = [id]
    environment_state = pd.DataFrame(
        index=pd.MultiIndex.from_product([environment_ids,months],names=['environment_id','at_date'])
        ,data=[]
    ).reset_index() 

    days_since_last_upgrade=0
    current_k8s_version_idx = k8s_releases.index[k8s_releases['version']==first_version].values[0]
    for row in environment_state.itertuples():
        if days_since_last_upgrade >= upgrade_every:
            next_k8s_version_idx = min(len(k8s_releases)-1, current_k8s_version_idx+1)
            if k8s_releases.at[next_k8s_version_idx,'release_date'] <= row.at_date: #only upgrade if next version has been released
                current_k8s_version_idx = next_k8s_version_idx
                days_since_last_upgrade=0
        
        environment_state.loc[row.Index,['version', 'release_date', 'end_of_support_date']] = [
            k8s_releases.at[current_k8s_version_idx,'version'], 
            k8s_releases.at[current_k8s_version_idx,'release_date'], 
            k8s_releases.at[current_k8s_version_idx,'end_of_support_date'], 
        ]

        days_since_last_upgrade+=1

    environment_state['release_age'] = (environment_state['at_date'] - environment_state['release_date']).dt.days
    environment_state['release_date'] = pd.to_datetime(environment_state['release_date'])
    environment_state['end_of_support_date'] = pd.to_datetime(environment_state['end_of_support_date'])

    return environment_state