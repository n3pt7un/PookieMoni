import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
from config_utils import (
    get_categories, 
    get_all_stores, 
    auto_categorize_store, 
    add_store_to_category,
    get_initial_balance,
    get_budgets,
    calculate_budget_status,
    get_current_period_dates
)
from user_utils import (
    get_current_user,
    get_user_display_name,
    render_user_selector,
    get_worksheet_names,
    get_user_and_shared_data
)

# --- Page Configuration ---
st.set_page_config(
    page_title="Personal Finance Tracker",
    page_icon="💰",
    layout="centered",
)

# --- Google Sheets Connection ---
def login_screen():
    st.header("This app is private.")
    st.subheader("Please log in.")
    st.button("Log in with Google", on_click=st.login)

def show_budget_alert(category: str, new_amount: float, conn):
    """
    Show budget alert for a category after adding an expense.
    
    Args:
        category: Category of the expense
        new_amount: Amount of the new expense
        conn: Google Sheets connection
    """
    budgets = get_budgets()
    
    if category not in budgets:
        return
    
    budget = budgets[category]
    if not budget.get('is_active', True):
        return
    
    budget_amount = budget.get('amount', 0)
    
    # Get current period spending
    try:
        current_period_start, current_period_end = get_current_period_dates(budget.get('period', 'monthly'))
        expenses_df = conn.read(worksheet="expenses_taras", ttl=0)
        
        if not expenses_df.empty:
            expenses_df['Amount'] = pd.to_numeric(expenses_df['Amount'])
            expenses_df['Date'] = pd.to_datetime(expenses_df['Date'], format='mixed', dayfirst=True)
            
            # Filter by category and period
            period_category_expenses = expenses_df[
                (expenses_df['Category'] == category) &
                (expenses_df['Date'] >= current_period_start) &
                (expenses_df['Date'] <= current_period_end)
            ]
            
            total_spent = period_category_expenses['Amount'].sum()
        else:
            total_spent = new_amount
    except Exception:
        total_spent = new_amount
    
    if budget_amount > 0:
        percentage = (total_spent / budget_amount) * 100
        remaining = budget_amount - total_spent
        
        # Get budget settings for thresholds
        from config_utils import get_budget_settings
        settings = get_budget_settings()
        
        # Show appropriate alert based on percentage
        if percentage >= settings['alert_threshold']:
            if remaining < 0:
                st.error(f"🔴 **Budget Alert**: You're €{abs(remaining):,.2f} over your {category} budget! ({percentage:.1f}% of budget used)")
            else:
                st.error(f"🔴 **Budget Alert**: You've reached {percentage:.1f}% of your {category} budget!")
        elif percentage >= settings['warning_threshold']:
            st.warning(f"🟡 **Budget Warning**: You've used €{total_spent:,.2f} / €{budget_amount:,.2f} ({percentage:.1f}%) of your {category} budget. €{remaining:,.2f} remaining.")
        else:
            st.info(f"ℹ️ **Budget Impact**: You've used €{total_spent:,.2f} / €{budget_amount:,.2f} ({percentage:.1f}%) of your {category} budget. €{remaining:,.2f} remaining. You're on track! 🟢")

# --- Main Application ---
def main():
    st.title("💰 Personal Finance Tracker")

    # Check if authentication is configured
    try:
        is_logged_in = st.user.is_logged_in
        user_name = st.user.name if is_logged_in else "Guest"
    except (AttributeError, KeyError):
        # Authentication not configured, run in demo mode
        is_logged_in = True
        user_name = "Demo User"
    
    if not is_logged_in:
        login_screen()
        return

    # Render user selector
    render_user_selector()
    
    current_user = get_current_user()
    active_user_name = get_user_display_name(current_user)

    # Show welcome message
    if user_name != "Demo User":
        st.sidebar.success(f"Welcome, {user_name}!")
        st.button("Log out", on_click=st.logout)
    else:
        st.sidebar.info("Running in demo mode (authentication not configured)")
        st.sidebar.caption("Configure `.streamlit/secrets.toml` for Google OAuth")
    
    # Balance overview in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"### 💰 {active_user_name}'s Overview")
    
    try:
        balance_info = get_initial_balance()
        currency = balance_info['currency']
        initial_balance = balance_info['balance']
        
        # Get total income and expenses
        conn = st.connection("gsheets", type=GSheetsConnection)
        try:
            # Load data based on current user
            if current_user in ["user1", "user2"]:
                expenses_df = get_user_and_shared_data(conn, current_user, "expenses")
                income_df = get_user_and_shared_data(conn, current_user, "income")
            else:
                worksheets = get_worksheet_names("shared")
                expenses_df = conn.read(worksheet=worksheets["expenses"], ttl=0)
                income_df = conn.read(worksheet=worksheets["income"], ttl=0)
            
            if not expenses_df.empty:
                expenses_df['Amount'] = pd.to_numeric(expenses_df['Amount'])
                total_expenses = expenses_df['Amount'].sum()
            else:
                total_expenses = 0
            
            if not income_df.empty:
                income_df['Amount'] = pd.to_numeric(income_df['Amount'])
                total_income = income_df['Amount'].sum()
            else:
                total_income = 0
            
            current_balance = initial_balance + total_income - total_expenses
            
            st.sidebar.metric("Current Balance", f"{currency} {current_balance:,.2f}")
            
        except Exception:
            st.sidebar.metric("Initial Balance", f"{currency} {initial_balance:,.2f}")
            st.sidebar.caption("Connect to see current balance")
    except Exception:
        pass
    
    # Navigation info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📍 Navigation")
    st.sidebar.markdown("- **📈 Dashboard**: View your financial analytics")
    st.sidebar.markdown("- **📤 Upload CSV**: Import bank transactions")
    st.sidebar.markdown("- **⚙️ Settings**: Configure categories & stores")
    st.sidebar.markdown("---")

    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        st.error(f"Failed to connect to Google Sheets: {e}")
        st.info("Please ask the app owner to configure the Google Sheets connection.")
        return
    
    # --- Transaction Entry ---
    st.header(f"Add a New Transaction for {active_user_name}")
    
    st.info("💡 **Tip**: Visit the ⚙️ **Settings** page to manage categories, add stores, and configure auto-categorization keywords!")
    
    # Show info about current user
    if current_user in ["user1", "user2"]:
        st.caption(f"📊 You can add transactions to your personal account or shared account.")
    
    # Option to choose between personal and shared (for user1 and user2)
    if current_user in ["user1", "user2"]:
        transaction_scope = st.radio(
            "Add to:",
            ["Personal", "Shared"],
            horizontal=True,
            help="Personal transactions are only visible to you. Shared transactions are visible to both users."
        )
    else:
        transaction_scope = "Shared"
    
    transaction_type = st.selectbox("Transaction Type", ["Expense", "Income"])

    if transaction_type == "Expense":
        with st.form("expense_form", clear_on_submit=True):
            date = st.date_input("Date", datetime.now())
            amount = st.number_input("Amount", min_value=0.0, format="%.2f")
            
            # Store selection with suggestions
            all_stores = get_all_stores()
            store = st.selectbox("Store", options=[""] + all_stores, 
                               help="Select from existing stores or type a new one below")
            
            # Alternative: text input for new stores
            new_store = st.text_input("Or enter a new store name:")
            if new_store:
                store = new_store
            
            # Category selection with auto-categorization
            categories = get_categories()
            
            # Auto-categorize if store is provided
            suggested_category = None
            if store:
                suggested_category = auto_categorize_store(store)
                if suggested_category in categories:
                    default_index = categories.index(suggested_category)
                else:
                    default_index = 0
            else:
                default_index = 0
            
            category = st.selectbox("Category", categories, 
                                  index=default_index,
                                  help=f"Auto-suggested: {suggested_category}" if suggested_category else "Select a category")
            
            payment_option = st.selectbox("Payment Option", ["Cash", "Card"])
            card = st.text_input("Card (if applicable)")
            submitted = st.form_submit_button("Add Expense")
            
            if submitted:
                if not store:
                    st.error("Please enter a store name.")
                elif not amount:
                    st.error("Please enter an amount.")
                else:
                    # Add new store to configuration if it's not already there
                    if store not in all_stores:
                        add_store_to_category(category, store)
                    
                    expense_df = pd.DataFrame(
                        [
                            {
                                "Date": date.strftime("%d-%m-%Y"),  # Format as dd-MM-YYYY
                                "Amount": amount,
                                "Store": store,
                                "Category": category,
                                "Payment Option": payment_option,
                                "Card": card,
                            }
                        ]
                    )
                    
                    # Determine worksheet based on scope
                    if transaction_scope == "Shared":
                        worksheets = get_worksheet_names("shared")
                        worksheet_name = worksheets["expenses"]
                    else:
                        worksheets = get_worksheet_names(current_user)
                        worksheet_name = worksheets["expenses"]
                    
                    try:
                        # Read existing data and append the new row
                        existing_data = conn.read(worksheet=worksheet_name, ttl=0)
                        updated_df = pd.concat([existing_data, expense_df], ignore_index=True)
                        conn.update(worksheet=worksheet_name, data=updated_df)
                        st.success(f"✅ Expense added successfully to {transaction_scope} account!")
                        if store not in all_stores:
                            st.info(f"Added '{store}' to {category} category for future use.")
                        
                        # Show budget alert
                        show_budget_alert(category, amount, conn)
                    except Exception as e:
                        # If the sheet doesn't exist, conn.read will fail.
                        # In this case, we create the sheet with the new data.
                        if "gspread.exceptions.WorksheetNotFound" in str(e):
                            st.warning(f"Worksheet '{worksheet_name}' not found. A new one will be created.")
                            conn.update(worksheet=worksheet_name, data=expense_df)
                            st.success(f"Expense added successfully to {transaction_scope} account!")
                            if store not in all_stores:
                                st.info(f"Added '{store}' to {category} category for future use.")
                        else:
                            st.error(f"An error occurred: {e}")


    elif transaction_type == "Income":
        with st.form("income_form", clear_on_submit=True):
            date = st.date_input("Date", datetime.now())
            amount = st.number_input("Amount", min_value=0.0, format="%.2f")
            source = st.text_input("Source")
            payment_option = st.selectbox("Payment Option", ["Bank Transfer", "Cash"])
            submitted = st.form_submit_button("Add Income")

            if submitted:
                income_df = pd.DataFrame(
                    [
                        {
                            "Date": date.strftime("%d-%m-%Y"),  # Format as dd-MM-YYYY
                            "Amount": amount,
                            "Source": source,
                            "Payment Option": payment_option,
                        }
                    ]
                )
                
                # Determine worksheet based on scope
                if transaction_scope == "Shared":
                    worksheets = get_worksheet_names("shared")
                    worksheet_name = worksheets["income"]
                else:
                    worksheets = get_worksheet_names(current_user)
                    worksheet_name = worksheets["income"]
                
                try:
                    # Read existing data and append the new row
                    existing_data = conn.read(worksheet=worksheet_name, ttl=0)
                    updated_df = pd.concat([existing_data, income_df], ignore_index=True)
                    conn.update(worksheet=worksheet_name, data=updated_df)
                    st.success(f"✅ Income added successfully to {transaction_scope} account!")
                except Exception as e:
                     # If the sheet doesn't exist, conn.read will fail.
                    # In this case, we create the sheet with the new data.
                    if "gspread.exceptions.WorksheetNotFound" in str(e):
                        st.warning(f"Worksheet '{worksheet_name}' not found. A new one will be created.")
                        conn.update(worksheet=worksheet_name, data=income_df)
                        st.success(f"Income added successfully to {transaction_scope} account!")
                    else:
                        st.error(f"An error occurred: {e}")

    # --- Display Recent Transactions ---
    st.header(f"Recent {transaction_type}s for {active_user_name}")
    try:
        if current_user in ["user1", "user2"]:
            if transaction_type == "Expense":
                df = get_user_and_shared_data(conn, current_user, "expenses")
            else:
                df = get_user_and_shared_data(conn, current_user, "income")
        else:
            worksheets = get_worksheet_names("shared")
            if transaction_type == "Expense":
                df = conn.read(worksheet=worksheets["expenses"], ttl=0)
            else:
                df = conn.read(worksheet=worksheets["income"], ttl=0)
        
        if not df.empty:
            # Sort by most recent if Date column exists
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], format='mixed', dayfirst=True, errors='coerce')
                df = df.sort_values('Date', ascending=False)
            
            st.dataframe(df.head(10))
        else:
            st.info("No recent transactions found.")
    except Exception as e:
        st.error(f"Could not load recent transactions. Have you added any yet? Error: {e}")


if __name__ == "__main__":
    main()