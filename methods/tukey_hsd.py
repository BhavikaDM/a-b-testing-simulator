from statsmodels.stats.multicomp import pairwise_tukeyhsd
import pandas as pd
import matplotlib.pyplot as plt

def run_tukey_hsd(df, group_col, value_col):
    try:
        # Run Tukey's HSD
        tukey_result = pairwise_tukeyhsd(endog=df[value_col], groups=df[group_col], alpha=0.05)

        # Convert the result summary to a DataFrame
        summary_df = pd.DataFrame(
            data=tukey_result.summary().data[1:],
            columns=tukey_result.summary().data[0]
        )

        # Create the Tukey plot
        fig = tukey_result.plot_simultaneous(figsize=(10, 6))
        plt.title("Tukey HSD Confidence Intervals")
        plt.xlabel("Mean Difference")

        return summary_df, fig

    except Exception as e:
        # Return error as string and None for fig
        return f"Error running Tukey's HSD: {e}", None
