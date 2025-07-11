# Developer Guide

This document provides instructions for developers who want to contribute to or extend the Personal Finance Tracker application.

## Project Structure

```
PookieMoni/
├── .streamlit/
│   └── secrets.toml
├── docs/
│   └── developer_guide.md
├── pages/
│   └── 1_📈_Dashboard.py
├── app.py
├── config.yaml
├── generate_keys.py
├── README.md
└── requirements.txt
```

## Setup

### 1. Google Cloud Project

1.  Create a new project on the [Google Cloud Console](https://console.cloud.google.com/).
2.  Enable the **Google Drive API** and **Google Sheets API**.
3.  Create OAuth 2.0 Client IDs for a Web application.
    -   Add `http://localhost:8501` to the Authorized JavaScript origins.
    -   Add `http://localhost:8501` to the Authorized redirect URIs.
    -   Copy the **Client ID** and **Client Secret** to `.streamlit/secrets.toml`.
4.  Create a service account.
    -   Create a JSON key and download it.
    -   Place the key file at `.streamlit/your_service_account.json` (as specified in `secrets.toml`).
    -   Share your Google Sheets with the service account's email address.

### 2. Google Sheets

1.  Create a new Google Sheet.
2.  Rename the first sheet to `Expenses`.
3.  Set the headers for the `Expenses` sheet: `date`, `amount`, `store`, `category`, `payment_option`, `card`.
4.  Create a new sheet and name it `Income`.
5.  Set the headers for the `Income` sheet: `date`, `amount`, `source`, `payment_option`.

### 3. Application Configuration
1.  **Secrets**: Configure your Google Cloud credentials and a cookie secret key in `.streamlit/secrets.toml`.
2.  **Users**: Add or modify user information in `config.yaml`.
3.  **Passwords**: Use the `generate_keys.py` script to create hashed passwords for your users.
    ```bash
    python generate_keys.py
    ```
    Copy the generated hashes into the `password` field for each user in `config.yaml`.

## Architecture

The application is built with Streamlit and uses the following main components:

-   **Authentication**: `streamlit-authenticator` is used for handling Google OAuth2.
-   **Data Storage**: `gspread` and `gspread-dataframe` are used to interact with Google Sheets.
-   **Visualization**: `plotly` is used for creating interactive charts.

## How to Extend

-   **Add new charts**: Modify `pages/1_📈_Dashboard.py` to add new Plotly visualizations.
-   **Support more data sources**: Create new modules to fetch data from other sources and integrate them into the app.
-   **Improve data entry forms**: Enhance the forms in `app.py` with more validation or new fields. 