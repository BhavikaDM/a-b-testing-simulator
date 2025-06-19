# utils/method_recommender.py

def suggest_methods(df):
    group_count = df['group'].nunique()
    
    if group_count == 2:
        return ['T-Test', 'Bootstrap', 'Bayesian A/B']
    elif group_count > 2:
        return ['ANOVA', 'Tukey’s HSD', 'Bootstrap']
    else:
        return []
