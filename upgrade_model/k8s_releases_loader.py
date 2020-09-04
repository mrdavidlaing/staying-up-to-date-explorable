import os
import pandas as pd

K8S_RELEASE_DATE_CSV = os.path.join(os.path.dirname(__file__), 'k8s-releases.csv')

def load():
    return pd.read_csv(K8S_RELEASE_DATE_CSV, parse_dates=['release_date','end_of_support_date'] )