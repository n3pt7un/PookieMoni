# Personal Finance Tracker

A Streamlit application to track your personal income and expenses using Google Sheets as a backend.

## Features

- Secure login with `streamlit-authenticator`.
- Track income and expenses in separate Google Sheets.
- Add new transactions through a user-friendly interface.
- Interactive dashboard with Plotly to visualize financial data.
- Configurable categories and stores via TOML configuration file.
- Automatic categorization of expenses based on store names and keywords.
- Dynamic store suggestions to speed up data entry.
- **Visual Settings Interface**: Manage categories, stores, and keywords through an intuitive web interface.
- **CSV Upload**: Import bank transactions from CSV files with automatic categorization.

## Getting Started

1. Clone the repository.
2. Install the dependencies: `pip install -r requirements.txt`
3. Set up your Google Cloud credentials in `.streamlit/secrets.toml`.
4. Configure users in `config.yaml`.
5. Generate hashed passwords for your users using `generate_keys.py` and update `config.yaml`.
6. Run the app: `streamlit run app.py` 

## Configuration System

The application uses a `config.toml` file to manage expense categories and store names. This allows for easy customization and automatic categorization of expenses.

### Configuration File Structure

The `config.toml` file contains:
- **Categories**: Different expense categories (Food, Transport, Shopping, etc.)
- **Stores**: List of store names associated with each category
- **Keywords**: Keywords used for automatic categorization
- **Settings**: Default category and auto-categorization preferences

### How It Works

1. **Auto-categorization**: When you enter a store name, the app automatically suggests a category based on:
   - Exact store name matches
   - Keyword matching in store names

2. **Store Suggestions**: The app provides a dropdown with existing stores to speed up data entry.

3. **Dynamic Learning**: When you add a new store, it's automatically added to the selected category for future use.

### Customizing Categories and Stores

You can modify the `config.toml` file to:
- Add new categories
- Add stores to existing categories
- Modify keywords for better auto-categorization
- Change default settings

### Visual Settings Interface

The application includes a comprehensive **Settings page** (⚙️) that provides a user-friendly interface to manage your configuration:

#### **🔧 General Settings Tab**
- View and update the default category
- Enable/disable auto-categorization
- Reset settings to defaults

#### **📂 Categories Tab**
- View all categories with store and keyword counts
- Add new categories
- Remove existing categories (with confirmation)
- Rename categories

#### **🏪 Stores Tab**
- Select a category to manage its stores
- View all stores in a category
- Add new stores to categories
- Remove stores from categories

#### **🏷️ Keywords Tab**
- Manage keywords for auto-categorization
- Add keywords to improve automatic categorization
- Remove keywords that aren't working well
- Test auto-categorization with sample store names

### Testing the Configuration

You can test the configuration system by:
- Using the **Settings page** to manage categories, stores, and keywords
- Adding new expenses to see auto-categorization in action
- Checking that store suggestions appear in the dropdown
- Verifying that new stores are added to the selected category
- Testing categorization with the built-in test tool in the Keywords tab