import pandas as pd

def validate_csv(df):
    # Clean column names
    df.columns = [col.lower().strip() for col in df.columns]

    # Try identifying group and metric columns
    group_suggestions, metric_suggestions = suggest_group_and_metric_columns(df)

    if not group_suggestions:
        return False, "❌ No suitable group column found. Please include at least one categorical column with 2–10 unique values."
    if not metric_suggestions:
        return False, "❌ No suitable metric column found. Please include at least one numeric column with more than 5 unique values."

    # Use top suggestions as default 'group' and 'value'
    group_col = group_suggestions[0]
    metric_col = metric_suggestions[0]

    # Drop missing values
    df = df.dropna(subset=[group_col, metric_col])

    try:
        df[metric_col] = pd.to_numeric(df[metric_col])
    except ValueError:
        return False, f"❌ Column '{metric_col}' must be numeric."

    if df[group_col].nunique() < 2:
        return False, "❌ Need at least 2 unique groups for A/B testing."

    # Rename to standard columns for internal consistency
    df = df.rename(columns={group_col: 'group', metric_col: 'value'})

    return True, df

def suggest_group_and_metric_columns(df):
    possible_groups = []
    possible_metrics = []

    for col in df.columns:
        if df[col].dtype == 'object' or pd.api.types.is_categorical_dtype(df[col]):
            unique_vals = df[col].nunique()
            if 2 <= unique_vals <= 10:
                possible_groups.append(col)

        elif pd.api.types.is_numeric_dtype(df[col]):
            if df[col].nunique() > 5:
                possible_metrics.append(col)

    return possible_groups, possible_metrics



# 💡 New Feature: LLM-Powered Column Suggestion

def suggest_columns_with_llm(df, openai_client):
    try:
        from openai import OpenAI
        client = openai_client

        prompt = f"""
        You are a data analyst helping with A/B testing.

        Here is the dataset summary:
        {df.describe(include='all').to_string()}

        Head of the dataset:
        {df.head(3).to_string()}

        Based on this, suggest one GROUP column and one METRIC (value) column for A/B testing. Explain briefly why you chose them.
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful A/B testing assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        suggestion = response.choices[0].message.content.strip()
        return suggestion

    except Exception as e:
        return f"LLM suggestion failed: {e}"
