# methods/t_test.py

from scipy.stats import ttest_ind
import pandas as pd

def run_t_test(df):
    groups = df['group'].unique()
    group1 = df[df['group'] == groups[0]]['value']
    group2 = df[df['group'] == groups[1]]['value']

    stat, p_value = ttest_ind(group1, group2)

    conclusion = "✅ The difference **is statistically significant**." if p_value < 0.05 else "⚠️ The difference is **not statistically significant**."
    
    return {
        'statistic': stat,
        'p_value': p_value,
        'conclusion': conclusion
    }
