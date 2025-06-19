# methods/bootstrap_test.py

import numpy as np
import pandas as pd

def run_bootstrap_test(df, num_iterations=10000):
    groups = df['group'].unique()
    if len(groups) != 2:
        return "Bootstrap currently supports only 2 groups."

    group1 = df[df['group'] == groups[0]]['value'].values
    group2 = df[df['group'] == groups[1]]['value'].values

    obs_diff = abs(np.mean(group1) - np.mean(group2))

    combined = np.concatenate([group1, group2])
    count = 0
    diffs = []

    for _ in range(num_iterations):
        np.random.shuffle(combined)
        new_group1 = combined[:len(group1)]
        new_group2 = combined[len(group1):]
        diff = abs(np.mean(new_group1) - np.mean(new_group2))
        diffs.append(diff)
        if diff >= obs_diff:
            count += 1

    p_value = count / num_iterations

    conclusion = "✅ Statistically significant difference (p < 0.05)" if p_value < 0.05 else "⚠️ No statistically significant difference (p ≥ 0.05)"
    
    return {
        "observed_diff": obs_diff,
        "p_value": p_value,
        "conclusion": conclusion,
        "distribution": diffs
    }
