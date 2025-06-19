# methods/anova.py

from scipy.stats import f_oneway

def run_anova(df):
    groups = df['group'].unique()
    group_data = [df[df['group'] == g]['value'] for g in groups]

    stat, p_value = f_oneway(*group_data)

    conclusion = "✅ At least one group is significantly different." if p_value < 0.05 else "⚠️ No significant difference found."

    return {
        'statistic': stat,
        'p_value': p_value,
        'conclusion': conclusion
    }
