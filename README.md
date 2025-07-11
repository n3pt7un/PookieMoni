# Personal Finance Tracker

A Streamlit application to track your personal income and expenses using Google Sheets as a backend.

## Features

- Secure login with `streamlit-authenticator`.
- Track income and expenses in separate Google Sheets.
- Add new transactions through a user-friendly interface.
- Interactive dashboard with Plotly to visualize financial data.

## Getting Started

1. Clone the repository.
2. Install the dependencies: `pip install -r requirements.txt`
3. Set up your Google Cloud credentials in `.streamlit/secrets.toml`.
4. Configure users in `config.yaml`.
5. Generate hashed passwords for your users using `generate_keys.py` and update `config.yaml`.
6. Run the app: `streamlit run app.py` 