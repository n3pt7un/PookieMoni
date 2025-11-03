import streamlit as st
import pandas as pd
from datetime import datetime
from config_utils import (
    get_categories, 
    get_stores_for_category, 
    get_keywords_for_category,
    add_category,
    remove_category,
    rename_category,
    add_store_to_category,
    remove_store_from_category,
    add_keyword_to_category,
    remove_keyword_from_category,
    update_settings,
    config_manager,
    get_initial_balance,
    set_initial_balance,
    add_balance_to_history,
    get_balance_history,
    get_budgets,
    set_budget,
    delete_budget,
    get_budget_settings,
    update_budget_settings,
    get_google_sheets_config,
    update_google_sheets_config
)

# --- Page Configuration ---
st.set_page_config(
    page_title="Settings",
    page_icon="⚙️",
    layout="wide",
)

def main():
    st.title("⚙️ Configuration Settings")
    
    # Check if authentication is configured
    try:
        is_logged_in = st.user.is_logged_in
    except (AttributeError, KeyError):
        # Authentication not configured, run in demo mode
        is_logged_in = True
    
    if not is_logged_in:
        st.warning("Please log in from the main page to access settings.")
        return
    
    # Quick overview
    st.markdown("""
    Welcome to the Configuration Settings! Here you can:
    - **Manage categories** for your expenses
    - **Add and remove stores** for each category
    - **Configure keywords** for automatic categorization
    - **Test auto-categorization** with sample store names
    """)
    
    # Create tabs for different settings sections
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "🔧 General", "📊 Google Sheets", "💰 Account Balance", "📈 Budget Planning", 
        "📂 Categories", "🏪 Stores", "🏷️ Keywords", "❓ Help"
    ])
    
    with tab1:
        general_settings()
    
    with tab2:
        google_sheets_settings()
    
    with tab3:
        account_balance_management()
    
    with tab4:
        budget_planning()
    
    with tab5:
        category_management()
    
    with tab6:
        store_management()
    
    with tab7:
        keyword_management()
    
    with tab8:
        help_documentation()

def general_settings():
    """General application settings."""
    st.header("General Settings")
    
    # Current settings
    current_default = config_manager.get_default_category()
    current_auto_categorize = config_manager.is_auto_categorize_enabled()
    
    st.subheader("Current Settings")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Default Category", current_default)
    
    with col2:
        st.metric("Auto-categorization", "Enabled" if current_auto_categorize else "Disabled")
    
    st.subheader("Update Settings")
    
    with st.form("general_settings_form"):
        categories = get_categories()
        
        new_default = st.selectbox(
            "Default Category",
            options=categories,
            index=categories.index(current_default) if current_default in categories else 0,
            help="Category to use when auto-categorization fails"
        )
        
        new_auto_categorize = st.checkbox(
            "Enable Auto-categorization",
            value=current_auto_categorize,
            help="Automatically suggest categories based on store names and keywords"
        )
        
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if st.form_submit_button("Update Settings", type="primary"):
                if update_settings(new_default, new_auto_categorize):
                    st.success("Settings updated successfully!")
                    st.rerun()
                else:
                    st.error("Failed to update settings.")
        
        with col2:
            if st.form_submit_button("Reset to Defaults"):
                if update_settings("Other", True):
                    st.success("Settings reset to defaults!")
                    st.rerun()
                else:
                    st.error("Failed to reset settings.")

def google_sheets_settings():
    """Google Sheets connection settings."""
    st.header("Google Sheets Configuration")
    
    st.markdown("""
    Configure your Google Sheets connection here. The spreadsheet URL is stored as an 
    **environment variable** for security.
    """)
    
    # Get current configuration
    sheets_config = get_google_sheets_config()
    
    st.subheader("Current Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Expenses Worksheet", sheets_config['expenses_worksheet'])
    
    with col2:
        st.metric("Income Worksheet", sheets_config['income_worksheet'])
    
    # Show connection status
    import os
    has_url = bool(os.environ.get("GOOGLE_SHEETS_URL") or sheets_config['spreadsheet_url'])
    
    if has_url:
        st.success("✅ Spreadsheet URL is configured")
        st.info("🔒 Spreadsheet URL is read from `GOOGLE_SHEETS_URL` environment variable")
    else:
        st.warning("⚠️ Spreadsheet URL not configured")
        st.info("""
        **To configure Google Sheets connection:**
        
        1. **Set environment variable** (recommended):
           ```bash
           export GOOGLE_SHEETS_URL="your-google-sheets-url"
           ```
        
        2. **Or create `.streamlit/secrets.toml`**:
           ```toml
           GOOGLE_SHEETS_URL = "your-google-sheets-url"
           ```
        
        3. **Then restart the app**
        """)
    
    st.subheader("Update Worksheet Names")
    
    with st.form("sheets_config_form"):
        expenses_ws = st.text_input(
            "Expenses Worksheet Name",
            value=sheets_config['expenses_worksheet'],
            help="Name of the worksheet containing expense data"
        )
        
        income_ws = st.text_input(
            "Income Worksheet Name",
            value=sheets_config['income_worksheet'],
            help="Name of the worksheet containing income data"
        )
        
        if st.form_submit_button("Update Worksheet Names", type="primary"):
            if update_google_sheets_config(
                expenses_worksheet=expenses_ws,
                income_worksheet=income_ws
            ):
                st.success("Worksheet names updated successfully!")
                st.rerun()
            else:
                st.error("Failed to update worksheet names.")
    
    st.subheader("📚 Setup Guide")
    
    with st.expander("How to get your Google Sheets URL"):
        st.markdown("""
        1. Open your Google Sheet
        2. Copy the URL from your browser's address bar
        3. It should look like:
           ```
           https://docs.google.com/spreadsheets/d/YOUR-SHEET-ID/edit
           ```
        4. Set it as an environment variable before starting the app
        """)
    
    with st.expander("Security Best Practices"):
        st.markdown("""
        - ✅ **DO** use environment variables for sensitive URLs
        - ✅ **DO** use `.streamlit/secrets.toml` for local development
        - ✅ **DO** add `.streamlit/secrets.toml` to `.gitignore`
        - ❌ **DON'T** commit sensitive URLs to git
        - ❌ **DON'T** share your spreadsheet URL publicly
        """)

def account_balance_management():
    """Manage initial account balance."""
    st.header("Account Balance Management")
    
    # Get current balance settings
    balance_info = get_initial_balance()
    
    # Display current account settings
    st.subheader("Current Account Settings")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Initial Balance", f"{balance_info['currency']} {balance_info['balance']:,.2f}")
    
    with col2:
        if balance_info['date']:
            st.metric("Set On", balance_info['date'])
        else:
            st.metric("Set On", "Not set yet")
    
    with col3:
        if balance_info['notes']:
            st.info(f"📝 {balance_info['notes']}")
    
    # Set/Update Initial Balance
    st.subheader("Set/Update Initial Balance")
    
    st.info("💡 **Tip**: Set your initial balance to reflect your starting financial position. This can be positive or negative (if starting with debt).")
    
    with st.form("balance_form"):
        balance_date = st.date_input(
            "Date",
            value=datetime.now(),
            help="Date when this balance applies"
        )
        
        balance_amount = st.number_input(
            f"Amount ({balance_info['currency']})",
            value=balance_info['balance'],
            step=100.0,
            format="%.2f",
            help="Can be negative if you're starting with debt"
        )
        
        balance_notes = st.text_area(
            "Notes (optional)",
            value=balance_info['notes'],
            placeholder="e.g., 'Initial setup', 'After savings transfer', etc.",
            help="Optional notes about this balance"
        )
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if st.form_submit_button("Update Balance", type="primary"):
                date_str = balance_date.strftime("%d-%m-%Y")
                if set_initial_balance(balance_amount, date_str, balance_notes):
                    # Also add to history
                    add_balance_to_history(balance_amount, date_str, balance_notes)
                    st.success(f"Balance updated to {balance_info['currency']} {balance_amount:,.2f}!")
                    st.rerun()
                else:
                    st.error("Failed to update balance.")
    
    # Balance History
    st.subheader("Balance History")
    
    history = get_balance_history()
    
    if history:
        history_df = pd.DataFrame(history)
        # Reorder columns for better display
        history_df = history_df[['date', 'balance', 'notes']]
        history_df.columns = ['Date', 'Balance', 'Notes']
        history_df['Balance'] = history_df['Balance'].apply(lambda x: f"{balance_info['currency']} {x:,.2f}")
        
        st.dataframe(history_df, use_container_width=True)
    else:
        st.info("No balance history yet. Update your balance above to start tracking.")

def budget_planning():
    """Budget planning and management."""
    st.header("Budget Planning")
    
    categories = get_categories()
    budgets = get_budgets()
    settings = get_budget_settings()
    
    # Overall Budget Summary
    st.subheader("Budget Summary")
    
    if budgets:
        total_budgeted = sum(b.get('amount', 0) for b in budgets.values() if b.get('is_active', True))
        active_count = sum(1 for b in budgets.values() if b.get('is_active', True))
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Monthly Budget", f"€{total_budgeted:,.2f}")
        
        with col2:
            st.metric("Active Budgets", f"{active_count} / {len(categories)}")
    else:
        st.info("No budgets configured yet. Set up your first budget below!")
    
    # Current Budgets Table
    st.subheader("Current Budgets")
    
    if budgets:
        budget_data = []
        for category in categories:
            if category in budgets:
                budget = budgets[category]
                budget_data.append({
                    "Category": category,
                    "Period": budget.get('period', 'monthly').capitalize(),
                    "Budget": f"€{budget.get('amount', 0):,.2f}",
                    "Status": "🟢 Active" if budget.get('is_active', True) else "⚪ Inactive"
                })
            else:
                budget_data.append({
                    "Category": category,
                    "Period": "-",
                    "Budget": "-",
                    "Status": "⚪ No budget"
                })
        
        budget_df = pd.DataFrame(budget_data)
        st.dataframe(budget_df, use_container_width=True, hide_index=True)
    else:
        st.info("No budgets configured.")
    
    # Set Budget for Category
    st.subheader("Set/Update Budget")
    
    with st.form("budget_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            selected_category = st.selectbox(
                "Category",
                options=categories,
                help="Select a category to set budget for"
            )
        
        with col2:
            # Get current budget if exists
            current_budget = budgets.get(selected_category, {})
            budget_amount = st.number_input(
                "Budget Amount (€)",
                min_value=0.0,
                value=current_budget.get('amount', 0.0),
                step=50.0,
                format="%.2f",
                help="Monthly budget limit for this category"
            )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            period = st.selectbox(
                "Period",
                options=["monthly", "weekly"],
                index=0 if current_budget.get('period', 'monthly') == 'monthly' else 1,
                help="Budget renewal period"
            )
        
        with col2:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now(),
                help="When this budget takes effect"
            )
        
        with col3:
            is_active = st.checkbox(
                "Active",
                value=current_budget.get('is_active', True),
                help="Whether this budget is currently active"
            )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.form_submit_button("Set Budget", type="primary"):
                if budget_amount > 0:
                    date_str = start_date.strftime("%d-%m-%Y")
                    if set_budget(selected_category, budget_amount, period, date_str, is_active):
                        st.success(f"Budget set for {selected_category}: €{budget_amount:,.2f} / {period}")
                        st.rerun()
                    else:
                        st.error("Failed to set budget.")
                else:
                    st.error("Budget amount must be greater than 0.")
        
        with col2:
            if st.form_submit_button("Remove Budget", type="secondary"):
                if selected_category in budgets:
                    if delete_budget(selected_category):
                        st.success(f"Budget removed for {selected_category}")
                        st.rerun()
                    else:
                        st.error("Failed to remove budget.")
                else:
                    st.warning(f"No budget set for {selected_category}")
    
    # Quick Setup - Set All Budgets
    st.subheader("Quick Setup")
    
    with st.expander("🚀 Set Budgets for All Categories"):
        st.markdown("""
        Set a default budget for all categories at once. You can customize individual budgets later.
        """)
        
        with st.form("quick_budget_form"):
            default_amount = st.number_input(
                "Default Budget Amount (€)",
                min_value=0.0,
                value=500.0,
                step=100.0,
                format="%.2f"
            )
            
            default_period = st.selectbox(
                "Period",
                options=["monthly", "weekly"]
            )
            
            if st.form_submit_button("Apply to All Categories"):
                if default_amount > 0:
                    date_str = datetime.now().strftime("%d-%m-%Y")
                    success_count = 0
                    for category in categories:
                        if set_budget(category, default_amount, default_period, date_str, True):
                            success_count += 1
                    
                    st.success(f"Successfully set budgets for {success_count} categories!")
                    st.rerun()
                else:
                    st.error("Budget amount must be greater than 0.")
    
    # Budget Alert Settings
    st.subheader("Budget Alert Settings")
    
    st.markdown("""
    Configure when you want to receive warnings about your spending:
    - **Warning Threshold**: Get a yellow warning when spending reaches this percentage
    - **Alert Threshold**: Get a red alert when spending reaches this percentage
    """)
    
    with st.form("alert_settings_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            warning_threshold = st.slider(
                "Warning Threshold (%)",
                min_value=0,
                max_value=100,
                value=settings['warning_threshold'],
                step=5,
                help="Show yellow warning at this spending percentage"
            )
        
        with col2:
            alert_threshold = st.slider(
                "Alert Threshold (%)",
                min_value=0,
                max_value=200,
                value=settings['alert_threshold'],
                step=5,
                help="Show red alert at this spending percentage"
            )
        
        if st.form_submit_button("Update Alert Settings"):
            if update_budget_settings(
                warning_threshold=warning_threshold,
                alert_threshold=alert_threshold
            ):
                st.success("Alert settings updated!")
                st.rerun()
            else:
                st.error("Failed to update alert settings.")

def category_management():
    """Manage expense categories."""
    st.header("Category Management")
    
    categories = get_categories()
    
    # Display current categories
    st.subheader("Current Categories")
    if categories:
        # Create a DataFrame for better display
        category_data = []
        for cat in categories:
            stores_count = len(get_stores_for_category(cat))
            keywords_count = len(get_keywords_for_category(cat))
            category_data.append({
                "Category": cat,
                "Stores": stores_count,
                "Keywords": keywords_count
            })
        
        df = pd.DataFrame(category_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No categories found.")
    
    # Add new category
    st.subheader("Add New Category")
    with st.form("add_category_form"):
        new_category = st.text_input("Category Name", placeholder="Enter new category name")
        
        if st.form_submit_button("Add Category", type="primary"):
            if new_category:
                if new_category not in categories:
                    if add_category(new_category):
                        st.success(f"Category '{new_category}' added successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to add category.")
                else:
                    st.error("Category already exists.")
            else:
                st.error("Please enter a category name.")
    
    # Remove category
    st.subheader("Remove Category")
    if categories:
        with st.form("remove_category_form"):
            category_to_remove = st.selectbox(
                "Select Category to Remove",
                options=categories,
                help="⚠️ This will permanently delete the category and all its stores/keywords"
            )
            
            confirm_removal = st.checkbox("I confirm I want to delete this category")
            
            if st.form_submit_button("Remove Category", type="secondary"):
                if confirm_removal:
                    if remove_category(category_to_remove):
                        st.success(f"Category '{category_to_remove}' removed successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to remove category.")
                else:
                    st.error("Please confirm the removal by checking the box.")
    
    # Rename category
    st.subheader("Rename Category")
    if categories:
        with st.form("rename_category_form"):
            old_name = st.selectbox("Category to Rename", options=categories)
            new_name = st.text_input("New Name", placeholder="Enter new category name")
            
            if st.form_submit_button("Rename Category"):
                if new_name:
                    if new_name not in categories:
                        if rename_category(old_name, new_name):
                            st.success(f"Category '{old_name}' renamed to '{new_name}' successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to rename category.")
                    else:
                        st.error("A category with this name already exists.")
                else:
                    st.error("Please enter a new category name.")

def store_management():
    """Manage stores for each category."""
    st.header("Store Management")
    
    categories = get_categories()
    
    if not categories:
        st.warning("No categories found. Please add categories first.")
        return
    
    # Select category to manage
    selected_category = st.selectbox("Select Category to Manage", options=categories)
    
    if selected_category:
        stores = get_stores_for_category(selected_category)
        
        st.subheader(f"Stores in '{selected_category}' Category")
        
        if stores:
            # Display stores in a more interactive way
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**{len(stores)} stores configured:**")
                
                # Create columns for better layout
                num_cols = 3
                cols = st.columns(num_cols)
                
                for i, store in enumerate(stores):
                    with cols[i % num_cols]:
                        st.write(f"• {store}")
            
            with col2:
                st.write("**Remove Store:**")
                store_to_remove = st.selectbox(
                    "Select store to remove",
                    options=stores,
                    key=f"remove_store_{selected_category}",
                    label_visibility="collapsed"
                )
                
                if st.button("Remove", key=f"remove_btn_{selected_category}"):
                    if remove_store_from_category(selected_category, store_to_remove):
                        st.success(f"Store '{store_to_remove}' removed!")
                        st.rerun()
                    else:
                        st.error("Failed to remove store.")
        else:
            st.info(f"No stores configured for '{selected_category}' category.")
        
        # Add new store
        st.subheader("Add New Store")
        with st.form(f"add_store_form_{selected_category}"):
            new_store = st.text_input("Store Name", placeholder="Enter store name")
            
            if st.form_submit_button("Add Store", type="primary"):
                if new_store:
                    if new_store not in stores:
                        if add_store_to_category(selected_category, new_store):
                            st.success(f"Store '{new_store}' added to '{selected_category}' category!")
                            st.rerun()
                        else:
                            st.error("Failed to add store.")
                    else:
                        st.error("Store already exists in this category.")
                else:
                    st.error("Please enter a store name.")

def keyword_management():
    """Manage keywords for each category."""
    st.header("Keyword Management")
    
    categories = get_categories()
    
    if not categories:
        st.warning("No categories found. Please add categories first.")
        return
    
    # Select category to manage
    selected_category = st.selectbox("Select Category to Manage", options=categories, key="keyword_category")
    
    if selected_category:
        keywords = get_keywords_for_category(selected_category)
        
        st.subheader(f"Keywords for '{selected_category}' Category")
        
        if keywords:
            # Display keywords
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**{len(keywords)} keywords configured:**")
                
                # Display keywords as tags
                keyword_tags = " • ".join([f"`{keyword}`" for keyword in keywords])
                st.markdown(keyword_tags)
                
                st.info("💡 These keywords are used to automatically categorize stores. For example, if a store name contains 'pizza', it will be suggested for the Food category.")
            
            with col2:
                st.write("**Remove Keyword:**")
                keyword_to_remove = st.selectbox(
                    "Select keyword to remove",
                    options=keywords,
                    key=f"remove_keyword_{selected_category}",
                    label_visibility="collapsed"
                )
                
                if st.button("Remove", key=f"remove_keyword_btn_{selected_category}"):
                    if remove_keyword_from_category(selected_category, keyword_to_remove):
                        st.success(f"Keyword '{keyword_to_remove}' removed!")
                        st.rerun()
                    else:
                        st.error("Failed to remove keyword.")
        else:
            st.info(f"No keywords configured for '{selected_category}' category.")
        
        # Add new keyword
        st.subheader("Add New Keyword")
        with st.form(f"add_keyword_form_{selected_category}"):
            new_keyword = st.text_input(
                "Keyword", 
                placeholder="Enter keyword (e.g., 'pizza', 'fuel', 'clothes')",
                help="Keywords are used to automatically categorize stores based on their names"
            )
            
            if st.form_submit_button("Add Keyword", type="primary"):
                if new_keyword:
                    if new_keyword.lower() not in [k.lower() for k in keywords]:
                        if add_keyword_to_category(selected_category, new_keyword):
                            st.success(f"Keyword '{new_keyword}' added to '{selected_category}' category!")
                            st.rerun()
                        else:
                            st.error("Failed to add keyword.")
                    else:
                        st.error("Keyword already exists in this category.")
                else:
                    st.error("Please enter a keyword.")
        
        # Test auto-categorization
        st.subheader("Test Auto-categorization")
        with st.form(f"test_categorization_{selected_category}"):
            test_store = st.text_input("Test Store Name", placeholder="Enter a store name to test categorization")
            
            if st.form_submit_button("Test Categorization"):
                if test_store:
                    from config_utils import auto_categorize_store
                    predicted_category = auto_categorize_store(test_store)
                    
                    if predicted_category == selected_category:
                        st.success(f"✅ '{test_store}' would be categorized as '{predicted_category}'")
                    else:
                        st.info(f"ℹ️ '{test_store}' would be categorized as '{predicted_category}'")
                        if predicted_category != selected_category:
                            st.write(f"💡 To make it categorize as '{selected_category}', add relevant keywords.")
                else:
                    st.error("Please enter a store name to test.")

def help_documentation():
    """Help and documentation for the settings interface."""
    st.header("❓ Help & Documentation")
    
    st.markdown("""
    ## How to Use the Settings Interface
    
    This interface allows you to customize how your Personal Finance Tracker categorizes expenses automatically.
    
    ### 🔧 General Settings
    - **Default Category**: Used when auto-categorization can't determine the right category
    - **Auto-categorization**: Enable/disable the automatic suggestion feature
    
    ### 📂 Categories
    Categories help organize your expenses. Each category can have:
    - **Stores**: Specific store names that belong to this category
    - **Keywords**: Words that help identify stores for this category
    
    **Examples of good categories:**
    - `Food` - restaurants, groceries, takeout
    - `Transport` - gas stations, public transport, parking
    - `Shopping` - clothing, electronics, general retail
    - `Bills` - utilities, insurance, subscriptions
    
    ### 🏪 Stores
    Stores are specific business names that you visit regularly. When you add a store:
    - It appears in the dropdown when adding expenses
    - It's automatically categorized correctly in the future
    
    **Examples:**
    - `McDonald's` → Food category
    - `Shell` → Transport category
    - `Amazon` → Shopping category
    
    ### 🏷️ Keywords
    Keywords help the system automatically categorize new stores you haven't seen before.
    
    **How keywords work:**
    - If you enter `Joe's Pizza House`, the keyword `pizza` will suggest `Food` category
    - If you enter `Downtown Parking Garage`, the keyword `parking` will suggest `Transport` category
    
    **Good keyword examples:**
    - Food: `pizza`, `burger`, `coffee`, `restaurant`, `grocery`
    - Transport: `gas`, `fuel`, `parking`, `taxi`, `bus`
    - Shopping: `store`, `mall`, `clothes`, `electronics`
    
    ### 💡 Tips for Best Results
    
    1. **Start with common stores**: Add stores you visit frequently first
    2. **Use descriptive keywords**: Think about words that commonly appear in store names
    3. **Test your setup**: Use the test feature to see how well your keywords work
    4. **Keep it simple**: Don't add too many similar keywords
    5. **Review regularly**: Check if new stores are being categorized correctly
    
    ### 🔄 How Auto-Categorization Works
    
    When you enter a store name, the system:
    1. **Checks exact matches**: Looks for the exact store name in your configured stores
    2. **Checks keywords**: Looks for keywords in the store name
    3. **Suggests category**: Picks the best matching category
    4. **Falls back to default**: Uses your default category if no match is found
    
    ### 📊 Example Workflow
    
    1. **Add a category**: Create "Entertainment" category
    2. **Add stores**: Add "Cinema City", "Netflix", "Spotify"
    3. **Add keywords**: Add "movie", "music", "entertainment"
    4. **Test**: Try "Downtown Movie Theater" - should suggest "Entertainment"
    5. **Use**: Next time you add an expense at "AMC Theaters", it will auto-suggest "Entertainment"
    
    ### 🚨 Troubleshooting
    
    **Store not auto-categorizing correctly?**
    - Check if there are relevant keywords for that store type
    - Add the store manually to the correct category
    - Add more specific keywords
    
    **Too many stores in wrong category?**
    - Review your keywords - they might be too broad
    - Remove or modify overly general keywords
    - Use the test feature to verify changes
    
    **Settings not saving?**
    - Make sure you have write permissions to the config file
    - Check if the config.toml file exists in your project directory
    - Restart the app if changes don't appear
    """)

if __name__ == "__main__":
    main() 