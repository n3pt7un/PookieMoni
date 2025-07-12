import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
from config_utils import get_categories, get_all_stores, auto_categorize_store, add_store_to_category

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

# --- Main Application ---
def main():
    st.title("💰 Personal Finance Tracker")

    if not st.user.is_logged_in:
        login_screen()
        return

    st.sidebar.success(f"Welcome, {st.user.name}!")
    st.button("Log out", on_click=st.logout)
    
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
    st.header("Add a New Transaction")
    
    st.info("💡 **Tip**: Visit the ⚙️ **Settings** page to manage categories, add stores, and configure auto-categorization keywords!")
    
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
                    try:
                        # Read existing data and append the new row
                        existing_data = conn.read(worksheet="expenses_taras", ttl=0)
                        updated_df = pd.concat([existing_data, expense_df], ignore_index=True)
                        conn.update(worksheet="expenses_taras", data=updated_df)
                        st.success("Expense added successfully!")
                        if store not in all_stores:
                            st.info(f"Added '{store}' to {category} category for future use.")
                    except Exception as e:
                        # If the sheet doesn't exist, conn.read will fail.
                        # In this case, we create the sheet with the new data.
                        if "gspread.exceptions.WorksheetNotFound" in str(e):
                            st.warning("Worksheet 'expenses_taras' not found. A new one will be created.")
                            conn.update(worksheet="expenses_taras", data=expense_df)
                            st.success("Expense added successfully!")
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
                try:
                    # Read existing data and append the new row
                    existing_data = conn.read(worksheet="income_taras", ttl=0)
                    updated_df = pd.concat([existing_data, income_df], ignore_index=True)
                    conn.update(worksheet="income_taras", data=updated_df)
                    st.success("Income added successfully!")
                except Exception as e:
                     # If the sheet doesn't exist, conn.read will fail.
                    # In this case, we create the sheet with the new data.
                    if "gspread.exceptions.WorksheetNotFound" in str(e):
                        st.warning("Worksheet 'income_taras' not found. A new one will be created.")
                        conn.update(worksheet="income_taras", data=income_df)
                        st.success("Income added successfully!")
                    else:
                        st.error(f"An error occurred: {e}")

    # --- Display Recent Transactions ---
    st.header("Recent Transactions")
    try:
        if transaction_type == "Expense":
            df = conn.read(worksheet="expenses_taras", ttl=0)
            st.dataframe(df.tail())
        else:
            df = conn.read(worksheet="income_taras", ttl=0)
            st.dataframe(df.tail())
    except Exception as e:
        st.error(f"Could not load recent transactions. Have you added any yet? Error: {e}")


if __name__ == "__main__":
    main()