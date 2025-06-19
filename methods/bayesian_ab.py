# methods/bayesian_ab.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def run_bayesian_ab_test(df, num_samples=10000):
    groups = df['group'].unique()
    if len(groups) != 2:
        return "Bayesian A/B test currently supports only 2 groups."

    group1 = df[df['group'] == groups[0]]['value'].values
    group2 = df[df['group'] == groups[1]]['value'].values

    # Posterior distributions (Normal approximation)
    g1_mean, g1_std = np.mean(group1), np.std(group1) / np.sqrt(len(group1))
    g2_mean, g2_std = np.mean(group2), np.std(group2) / np.sqrt(len(group2))

    # Sampling from posteriors
    g1_samples = np.random.normal(g1_mean, g1_std, num_samples)
    g2_samples = np.random.normal(g2_mean, g2_std, num_samples)

    prob_A_better = np.mean(g1_samples > g2_samples)
    prob_B_better = 1 - prob_A_better

    conclusion = f"✅ There is a **{prob_A_better*100:.1f}%** chance that `{groups[0]}` is better than `{groups[1]}`."

    return {
        "group1": groups[0],
        "group2": groups[1],
        "prob_A_better": prob_A_better,
        "prob_B_better": prob_B_better,
        "samples": (g1_samples, g2_samples),
        "conclusion": conclusion
    }
