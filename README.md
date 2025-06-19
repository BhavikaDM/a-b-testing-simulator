## A/B Testing Simulator

An interactive web application for conducting and comparing statistical A/B tests, powered by Streamlit, Python, and LLM-based column recommendations.

🚀 Features

- Upload your own CSV or use sample data
- Smart column detection (manual + OpenAI-powered suggestions)
- Supports multiple statistical methods:
  - ✅ T-Test
  - ✅ ANOVA
  - ✅ Tukey’s HSD
  - ✅ Bootstrap Testing
  - ✅ Bayesian A/B Testing
- Visualize results using boxplots, histograms, KDE plots
- Run a second test for side-by-side method comparison
- Export results as:
  - 📄 PDF summary report

🧠 Use Cases

- Marketing campaign performance
- UX variant testing
- Feature A/B experiments
- Sales strategy comparison

⚙️ Installation
---

# Clone the repository
git clone https://github.com/yourusername/ab-testing-app.git
cd ab-testing-app

# (Optional) Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

---
