import pandas as pd
from upgrade_model import k8s_releases_loader

k8s_releases = k8s_releases_loader.load()
k8s_releases_by_release_date = k8s_releases.set_index('release_date')

def predict_version(for_date):
    k8s_release = k8s_releases_by_release_date.truncate(after=for_date).tail(1).reset_index()
    release_age = (for_date - k8s_release['release_date']).dt.days
    days_until_end_of_support = (k8s_release['end_of_support_date'] - for_date).dt.days

    return k8s_release['version'][0], k8s_release['release_date'][0], k8s_release['end_of_support_date'][0], release_age[0], days_until_end_of_support[0]

def compute(id, start_date, end_date):
    days = pd.date_range(start=start_date, end=end_date, freq='D')
    
    environment_ids = [id]
    environment_state = pd.DataFrame(
        index=pd.MultiIndex.from_product([environment_ids,days],names=['environment_id','at_date'])
        ,data=[]
    ).reset_index() 

    environment_state[['version', 'release_date', 'end_of_support_date', 'release_age', 'days_until_end_of_support']] = \
        environment_state.apply(lambda r: predict_version(r['at_date']), axis=1, result_type="expand")

    return environment_state