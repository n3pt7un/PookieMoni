import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

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

    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        st.error(f"Failed to connect to Google Sheets: {e}")
        st.info("Please ask the app owner to configure the Google Sheets connection.")
        return
    
    # --- Transaction Entry ---
    st.header("Add a New Transaction")
    
    transaction_type = st.selectbox("Transaction Type", ["Expense", "Income"])

    if transaction_type == "Expense":
        with st.form("expense_form", clear_on_submit=True):
            date = st.date_input("Date", datetime.now())
            amount = st.number_input("Amount", min_value=0.0, format="%.2f")
            store = st.text_input("Store")
            category = st.selectbox("Category", ["Food", "Transport", "Shopping", "Bills", "Fun", "Other"])
            payment_option = st.selectbox("Payment Option", ["Cash", "Card"])
            card = st.text_input("Card (if applicable)")
            submitted = st.form_submit_button("Add Expense")
            
            if submitted:
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
                except Exception as e:
                    # If the sheet doesn't exist, conn.read will fail.
                    # In this case, we create the sheet with the new data.
                    if "gspread.exceptions.WorksheetNotFound" in str(e):
                        st.warning("Worksheet 'expenses_taras' not found. A new one will be created.")
                        conn.update(worksheet="expenses_taras", data=expense_df)
                        st.success("Expense added successfully!")
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