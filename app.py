import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os
import openai

# Custom utility imports
from utils.data_validator import validate_csv, suggest_group_and_metric_columns, suggest_columns_with_llm
from utils.method_recommender import suggest_methods
from methods.t_test import run_t_test
from methods.anova import run_anova
from methods.tukey_hsd import run_tukey_hsd
from methods.bootstrap_test import run_bootstrap_test
from methods.bayesian_ab import run_bayesian_ab_test
from utils.export import convert_df_to_csv
from utils.pdf_export import generate_pdf


# ========================
# Setup
# ========================
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
st.set_page_config(page_title="A/B Testing Web App", layout="wide")
st.title("📊 A/B Testing Simulator")

validated_df = None


# ========================
# Sidebar: Upload & Sample Data
# ========================
with st.sidebar:
    st.header("📂 Upload & Setup")
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
    if st.button("Use Sample Data"):
        raw_df = pd.read_csv("data/sample_anova.csv")
        is_valid, result = validate_csv(raw_df)
        if is_valid:
            validated_df = result
            st.success("✅ Sample data loaded successfully!")
        else:
            st.error(result)

# ========================
# File Validation
# ========================
if uploaded_file:
    try:
        raw_df = pd.read_csv(uploaded_file)
        is_valid, result = validate_csv(raw_df)
        if not is_valid:
            st.error(result)
        else:
            validated_df = result
            st.success("✅ File uploaded and validated successfully!")
            st.dataframe(validated_df.head())
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")

# ========================
# LLM Column Suggestions
# ========================
if validated_df is not None:
    st.markdown("### 🤖 Smart Column Suggestion (LLM-Powered)")
    if st.button("🔍 Get LLM Suggestions"):
        with st.spinner("Thinking..."):
            suggestion = suggest_columns_with_llm(validated_df, openai)
        st.info(suggestion)

# ========================
# Column Selection
# ========================
if validated_df is not None:
    group_suggestions, metric_suggestions = suggest_group_and_metric_columns(validated_df)

    st.markdown("### 🧠 Column Suggestions Based on Your Data")
    col1, col2 = st.columns(2)

    with col1:
        group_col = st.selectbox("📌 Select Group Column", validated_df.columns,
                                 index=validated_df.columns.get_loc(group_suggestions[0]) if group_suggestions else 0)
    with col2:
        value_col = st.selectbox("📊 Select Metric Column", validated_df.columns,
                                 index=validated_df.columns.get_loc(metric_suggestions[0]) if metric_suggestions else 0)

    validated_df = validated_df[[group_col, value_col]].dropna()
    validated_df.columns = ['group', 'value']
    
    if "show_second_test" not in st.session_state:
        st.session_state.show_second_test = False
    if "second_test_result" not in st.session_state:
        st.session_state.second_test_result = None
    if "second_method" not in st.session_state:
        st.session_state.second_method = None

    # ========================
    # Method Recommendations
    # ========================
    st.markdown("### 💡 Method Selection")
    st.caption("Recommended: ANOVA, Tukey’s HSD, Bootstrap")
    suggestions = suggest_methods(validated_df)
    if suggestions:
        for method in suggestions:
            st.markdown(f"- ✅ **{method}**")
    else:
        st.warning("No suitable methods detected for your data.")

    selected_method = st.selectbox("Choose Method", ['T-Test', 'ANOVA', 'Tukey’s HSD', 'Bootstrap', 'Bayesian A/B'])

    # Help Box
    with st.expander("ℹ️ What do these methods mean?"):
        st.markdown("""
        - **T-Test**: Compare means between two groups.
        - **ANOVA**: Compare means across 3+ groups.
        - **Tukey’s HSD**: Find which group pairs differ after ANOVA.
        - **Bootstrap**: Resampling to estimate confidence intervals.
        - **Bayesian A/B**: Probabilistic comparison of groups.
        """)

    # ========================
    # Visual Helpers
    # ========================
    def plot_boxplot(df):
        fig, ax = plt.subplots()
        sns.boxplot(data=df, x='group', y='value', palette='Set2', ax=ax)
        ax.set_title("Group-wise Value Comparison")
        return fig

    def plot_bootstrap_distribution(diffs, obs_diff):
        fig, ax = plt.subplots()
        sns.histplot(diffs, kde=True, color="skyblue", ax=ax)
        ax.axvline(x=obs_diff, color='red', linestyle='--', label=f"Observed Diff: {obs_diff:.2f}")
        ax.set_title("Bootstrap Mean Differences")
        ax.legend()
        return fig

    def plot_bayesian_posteriors(samples, group1, group2):
        g1_samples, g2_samples = samples
        fig, ax = plt.subplots()
        sns.kdeplot(g1_samples, label=group1, shade=True)
        sns.kdeplot(g2_samples, label=group2, shade=True)
        ax.set_title("Posterior Distributions")
        ax.legend()
        return fig

    # ========================
    # Run Selected Test
    # ========================
    
    test_result = None
    if selected_method == 'T-Test':
        if validated_df['group'].nunique() == 2:
            test_result = run_t_test(validated_df)
        else:
            st.warning("T-Test requires exactly 2 groups.")

    elif selected_method == 'ANOVA':
        if validated_df['group'].nunique() >= 3:
            test_result = run_anova(validated_df)
        else:
            st.warning("ANOVA requires 3 or more groups.")

    elif selected_method == 'Tukey’s HSD':
        if validated_df['group'].nunique() >= 3:
            summary_df, tukey_fig = run_tukey_hsd(validated_df, 'group', 'value')
            if isinstance(summary_df, str):
                st.warning(summary_df)
            else:
                st.markdown("### 📋 Tukey's HSD Results")
                st.dataframe(summary_df)
                st.pyplot(tukey_fig)
        else:
            st.warning("Tukey’s HSD needs 3 or more groups.")

    elif selected_method == 'Bootstrap':
        if validated_df['group'].nunique() == 2:
            test_result = run_bootstrap_test(validated_df)
        else:
            st.warning("Bootstrap currently supports only 2 groups.")

    elif selected_method == 'Bayesian A/B':
        if validated_df['group'].nunique() == 2:
            test_result = run_bayesian_ab_test(validated_df)
        else:
            st.warning("Bayesian A/B Test supports exactly 2 groups.")

    # ========================
    # Results Display
    # ========================
    if isinstance(test_result, dict):
        st.markdown(f"### ✅ {selected_method} Results")

        if selected_method == 'T-Test':
            st.write(f"**T-statistic:** {test_result['statistic']:.4f}")
            st.write(f"**P-value:** {test_result['p_value']:.4f}")
            st.success(test_result['conclusion'])
            st.pyplot(plot_boxplot(validated_df))

        elif selected_method == 'ANOVA':
            st.write(f"**F-statistic:** {test_result['statistic']:.4f}")
            st.write(f"**P-value:** {test_result['p_value']:.4f}")
            st.success(test_result['conclusion'])
            st.pyplot(plot_boxplot(validated_df))

        elif selected_method == 'Bootstrap':
            st.write(f"**Observed Difference:** {test_result['observed_diff']:.4f}")
            st.write(f"**P-value:** {test_result['p_value']:.4f}")
            st.success(test_result['conclusion'])
            st.pyplot(plot_bootstrap_distribution(test_result['distribution'], test_result['observed_diff']))

        elif selected_method == 'Bayesian A/B':
            st.success(test_result['conclusion'])
            st.pyplot(plot_bayesian_posteriors(test_result['samples'],
                                               test_result['group1'], test_result['group2']))

        # ========================
        # Export
        # ========================
        #csv_data = convert_df_to_csv(test_result if isinstance(test_result, pd.DataFrame) else validated_df)
        #st.download_button("📥 Download Results as CSV", data=csv_data, file_name="ab_test_results.csv", mime="text/csv")

        #summary = f"""📊 A/B Testing Summary
#-----------------------------
#Method: {selected_method}
#Conclusion: {test_result.get('conclusion', 'N/A')}
#       pdf = generate_pdf(summary)
#        st.download_button("📄 Download Summary as PDF", data=pdf, file_name="ab_test_summary.pdf", mime="application/pdf")
        if "show_second_test" not in st.session_state:
            st.session_state.show_second_test = False
        #if "second_method" not in st.session_state:
            #st.session_state.second_method = None
            #test-2
        if validated_df is not None and isinstance(test_result, dict):
            # Second test trigger button
            if st.button("➕ Run Another Test (Compare)"):
                st.session_state.show_second_test = True

            # IF TRUE, SHOW SECOND METHOD SELECTION
        if st.session_state.show_second_test:
            st.markdown("### 🧪 Second A/B Test")
            second_method = st.selectbox("Choose Second Method", options=suggestions, key="second_method")

            second_test_result = None

            if second_method == 'T-Test':
                if validated_df['group'].nunique() == 2:
                    second_test_result = run_t_test(validated_df)
                else:
                    st.warning("T-Test requires exactly 2 groups.")

            elif second_method == 'ANOVA':
                if validated_df['group'].nunique() >= 3:
                    second_test_result = run_anova(validated_df)
                else:
                    st.warning("ANOVA requires 3 or more groups.")

            elif second_method == 'Tukey’s HSD':
                if validated_df['group'].nunique() >= 3:
                    summary_df, tukey_fig = run_tukey_hsd(validated_df, 'group', 'value')
                    if isinstance(summary_df, str):
                        st.warning(summary_df)
                    else:
                        st.markdown("### 📋 Tukey's HSD Results (Second Test)")
                        st.dataframe(summary_df)
                        st.pyplot(tukey_fig)
                else:
                    st.warning("Tukey’s HSD needs 3 or more groups.")

            elif second_method == 'Bootstrap':
                if validated_df['group'].nunique() == 2:
                    second_test_result = run_bootstrap_test(validated_df)
                else:
                    st.warning("Bootstrap currently supports only 2 groups.")

            elif second_method == 'Bayesian A/B':
                if validated_df['group'].nunique() == 2:
                    second_test_result = run_bayesian_ab_test(validated_df)
                else:
                    st.warning("Bayesian A/B Test supports exactly 2 groups.")

    # Save and show result
            if second_test_result:
                st.session_state.second_test_result = second_test_result
                method_used = st.session_state.second_method


# DISPLAY SECOND TEST RESULTS
        if st.session_state.second_test_result:
            result = st.session_state.second_test_result
            method = st.session_state.second_method
            st.markdown(f"### ✅ Second Test Result: {method}")

            if method in ['T-Test', 'ANOVA']:
                st.write(f"**Statistic:** {result['statistic']:.4f}")
                st.write(f"**P-value:** {result['p_value']:.4f}")
                st.success(result['conclusion'])
                st.pyplot(plot_boxplot(validated_df))

            elif method == 'Bootstrap':
                st.write(f"**Observed Difference:** {result['observed_diff']:.4f}")
                st.write(f"**P-value:** {result['p_value']:.4f}")
                st.success(result['conclusion'])
                st.pyplot(plot_bootstrap_distribution(result['distribution'], result['observed_diff']))

            elif method == 'Bayesian A/B':
                st.success(result['conclusion'])
                st.pyplot(plot_bayesian_posteriors(result['samples'], result['group1'], result['group2']))
                
        # Export Combined Summary (PDF)
        if test_result and st.session_state.get("second_test_result"):
            raw_summary = f"""A/B Testing Comparison Summary
-----------------------------
First Test
Method: {selected_method}
Conclusion: {test_result.get('conclusion', 'N/A')}
Statistic: {test_result.get('statistic', test_result.get('observed_diff', 'N/A'))}
P-value: {test_result.get('p_value', 'N/A')}

Second Test
Method: {st.session_state.second_method}
Conclusion: {st.session_state.second_test_result.get('conclusion', 'N/A')}
Statistic: {st.session_state.second_test_result.get('statistic', st.session_state.second_test_result.get('observed_diff', 'N/A'))}
P-value: {st.session_state.second_test_result.get('p_value', 'N/A')}
"""

    # Remove emojis if present
            clean_summary = raw_summary.encode('ascii', 'ignore').decode()

    # Generate and download PDF
            pdf = generate_pdf(clean_summary)

            if pdf:
                st.download_button(
                "📄 Download Comparison Summary as PDF",
            data=pdf,
            file_name="combined_ab_summary.pdf",
            mime="application/pdf"
        )
            else:
                st.error("PDF generation failed.")

                
        


