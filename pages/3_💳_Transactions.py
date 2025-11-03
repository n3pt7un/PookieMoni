import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
from config_utils import (
    get_categories, 
    get_all_stores, 
    auto_categorize_store, 
    add_store_to_category,
    get_budgets,
    calculate_budget_status,
    get_current_period_dates,
    get_budget_settings
)

# --- Page Configuration ---
st.set_page_config(
    page_title="Transactions",
    page_icon="💳",
    layout="wide",
)

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
    st.title("💳 Transaction Management")

    # Check if authentication is configured
    try:
        is_logged_in = st.user.is_logged_in
    except (AttributeError, KeyError):
        # Authentication not configured, run in demo mode
        is_logged_in = True
    
    if not is_logged_in:
        st.warning("Please log in to manage transactions.")
        return

    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        st.error(f"Failed to connect to Google Sheets: {e}")
        st.info("Please configure the Google Sheets connection in Settings.")
        return
    
    # Create tabs for different transaction management features
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Transaction", "✏️ Edit Transactions", "🗑️ Bulk Delete", "📋 View All"])
    
    with tab1:
        add_transaction_form(conn)
    
    with tab2:
        edit_transactions(conn)
    
    with tab3:
        bulk_delete_transactions(conn)
    
    with tab4:
        view_all_transactions(conn)

def add_transaction_form(conn):
    """Form to add a new transaction"""
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
                                "Date": date.strftime("%d-%m-%Y"),
                                "Amount": amount,
                                "Store": store,
                                "Category": category,
                                "Payment Option": payment_option,
                                "Card": card,
                            }
                        ]
                    )
                    try:
                        existing_data = conn.read(worksheet="expenses_taras", ttl=0)
                        updated_df = pd.concat([existing_data, expense_df], ignore_index=True)
                        conn.update(worksheet="expenses_taras", data=updated_df)
                        st.success("✅ Expense added successfully!")
                        if store not in all_stores:
                            st.info(f"Added '{store}' to {category} category for future use.")
                        
                        show_budget_alert(category, amount, conn)
                    except Exception as e:
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
                            "Date": date.strftime("%d-%m-%Y"),
                            "Amount": amount,
                            "Source": source,
                            "Payment Option": payment_option,
                        }
                    ]
                )
                try:
                    existing_data = conn.read(worksheet="income_taras", ttl=0)
                    updated_df = pd.concat([existing_data, income_df], ignore_index=True)
                    conn.update(worksheet="income_taras", data=updated_df)
                    st.success("Income added successfully!")
                except Exception as e:
                    if "gspread.exceptions.WorksheetNotFound" in str(e):
                        st.warning("Worksheet 'income_taras' not found. A new one will be created.")
                        conn.update(worksheet="income_taras", data=income_df)
                        st.success("Income added successfully!")
                    else:
                        st.error(f"An error occurred: {e}")

def edit_transactions(conn):
    """Edit existing transactions"""
    st.header("Edit Transactions")
    
    transaction_type = st.selectbox("Select Transaction Type", ["Expense", "Income"], key="edit_type")
    
    try:
        if transaction_type == "Expense":
            df = conn.read(worksheet="expenses_taras", ttl=0)
        else:
            df = conn.read(worksheet="income_taras", ttl=0)
        
        if df.empty:
            st.info(f"No {transaction_type.lower()}s found.")
            return
        
        # Add index column for selection
        df_display = df.copy()
        df_display.insert(0, 'ID', range(len(df_display)))
        
        st.subheader(f"All {transaction_type}s")
        st.dataframe(df_display, width='stretch')
        
        # Select transaction to edit
        st.subheader("Edit Transaction")
        
        transaction_id = st.number_input(
            "Enter Transaction ID to edit",
            min_value=0,
            max_value=len(df)-1,
            step=1,
            key="edit_id"
        )
        
        if transaction_id < len(df):
            st.info(f"Editing transaction #{transaction_id}")
            
            with st.form("edit_form"):
                if transaction_type == "Expense":
                    # Parse current date
                    try:
                        current_date = pd.to_datetime(df.iloc[transaction_id]['Date'], format='%d-%m-%Y')
                    except:
                        current_date = datetime.now()
                    
                    date = st.date_input("Date", value=current_date)
                    amount = st.number_input("Amount", value=float(df.iloc[transaction_id]['Amount']), format="%.2f")
                    store = st.text_input("Store", value=df.iloc[transaction_id]['Store'])
                    
                    categories = get_categories()
                    current_category = df.iloc[transaction_id]['Category']
                    category_index = categories.index(current_category) if current_category in categories else 0
                    category = st.selectbox("Category", categories, index=category_index)
                    
                    payment_option = st.selectbox(
                        "Payment Option", 
                        ["Cash", "Card"],
                        index=["Cash", "Card"].index(df.iloc[transaction_id]['Payment Option']) if df.iloc[transaction_id]['Payment Option'] in ["Cash", "Card"] else 0
                    )
                    card = st.text_input("Card", value=df.iloc[transaction_id].get('Card', ''))
                    
                else:  # Income
                    try:
                        current_date = pd.to_datetime(df.iloc[transaction_id]['Date'], format='%d-%m-%Y')
                    except:
                        current_date = datetime.now()
                    
                    date = st.date_input("Date", value=current_date)
                    amount = st.number_input("Amount", value=float(df.iloc[transaction_id]['Amount']), format="%.2f")
                    source = st.text_input("Source", value=df.iloc[transaction_id]['Source'])
                    payment_option = st.selectbox(
                        "Payment Option",
                        ["Bank Transfer", "Cash"],
                        index=["Bank Transfer", "Cash"].index(df.iloc[transaction_id]['Payment Option']) if df.iloc[transaction_id]['Payment Option'] in ["Bank Transfer", "Cash"] else 0
                    )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.form_submit_button("💾 Update Transaction", type="primary"):
                        # Update the dataframe
                        if transaction_type == "Expense":
                            df.at[transaction_id, 'Date'] = date.strftime("%d-%m-%Y")
                            df.at[transaction_id, 'Amount'] = amount
                            df.at[transaction_id, 'Store'] = store
                            df.at[transaction_id, 'Category'] = category
                            df.at[transaction_id, 'Payment Option'] = payment_option
                            df.at[transaction_id, 'Card'] = card
                        else:
                            df.at[transaction_id, 'Date'] = date.strftime("%d-%m-%Y")
                            df.at[transaction_id, 'Amount'] = amount
                            df.at[transaction_id, 'Source'] = source
                            df.at[transaction_id, 'Payment Option'] = payment_option
                        
                        # Save to Google Sheets
                        try:
                            worksheet = "expenses_taras" if transaction_type == "Expense" else "income_taras"
                            conn.update(worksheet=worksheet, data=df)
                            st.success(f"✅ Transaction #{transaction_id} updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error updating transaction: {e}")
                
                with col2:
                    if st.form_submit_button("🗑️ Delete This Transaction", type="secondary"):
                        # Delete the row
                        df = df.drop(transaction_id).reset_index(drop=True)
                        
                        try:
                            worksheet = "expenses_taras" if transaction_type == "Expense" else "income_taras"
                            conn.update(worksheet=worksheet, data=df)
                            st.success(f"✅ Transaction #{transaction_id} deleted successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting transaction: {e}")
    
    except Exception as e:
        st.error(f"Error loading transactions: {e}")

def bulk_delete_transactions(conn):
    """Bulk delete transactions with filters"""
    st.header("Bulk Delete Transactions")
    
    st.warning("⚠️ **Warning**: Bulk delete is permanent and cannot be undone!")
    
    transaction_type = st.selectbox("Select Transaction Type", ["Expense", "Income"], key="bulk_type")
    
    try:
        if transaction_type == "Expense":
            df = conn.read(worksheet="expenses_taras", ttl=0)
        else:
            df = conn.read(worksheet="income_taras", ttl=0)
        
        if df.empty:
            st.info(f"No {transaction_type.lower()}s found.")
            return
        
        # Parse dates for filtering
        df['Date_parsed'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', errors='coerce')
        
        st.subheader("Filter Transactions to Delete")
        
        # Filter options
        col1, col2 = st.columns(2)
        
        with col1:
            use_date_filter = st.checkbox("Filter by Date Range")
            if use_date_filter:
                min_date = df['Date_parsed'].min().date()
                max_date = df['Date_parsed'].max().date()
                date_range = st.date_input(
                    "Select Date Range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date
                )
        
        with col2:
            if transaction_type == "Expense":
                use_category_filter = st.checkbox("Filter by Category")
                if use_category_filter:
                    categories_in_data = df['Category'].unique().tolist()
                    selected_categories = st.multiselect(
                        "Select Categories",
                        options=categories_in_data
                    )
            else:
                use_source_filter = st.checkbox("Filter by Source")
                if use_source_filter:
                    sources_in_data = df['Source'].unique().tolist()
                    selected_sources = st.multiselect(
                        "Select Sources",
                        options=sources_in_data
                    )
        
        use_amount_filter = st.checkbox("Filter by Amount Range")
        if use_amount_filter:
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
            min_amount = float(df['Amount'].min())
            max_amount = float(df['Amount'].max())
            amount_range = st.slider(
                "Select Amount Range (€)",
                min_value=min_amount,
                max_value=max_amount,
                value=(min_amount, max_amount),
                step=0.01
            )
        
        # Apply filters
        filtered_df = df.copy()
        
        if use_date_filter and len(date_range) == 2:
            start_date = pd.Timestamp(date_range[0])
            end_date = pd.Timestamp(date_range[1])
            filtered_df = filtered_df[
                (filtered_df['Date_parsed'] >= start_date) &
                (filtered_df['Date_parsed'] <= end_date)
            ]
        
        if transaction_type == "Expense" and use_category_filter and selected_categories:
            filtered_df = filtered_df[filtered_df['Category'].isin(selected_categories)]
        
        if transaction_type == "Income" and use_source_filter and selected_sources:
            filtered_df = filtered_df[filtered_df['Source'].isin(selected_sources)]
        
        if use_amount_filter:
            filtered_df = filtered_df[
                (filtered_df['Amount'] >= amount_range[0]) &
                (filtered_df['Amount'] <= amount_range[1])
            ]
        
        # Show preview of transactions to be deleted
        st.subheader("Preview: Transactions to be Deleted")
        
        if filtered_df.empty:
            st.info("No transactions match the current filters.")
        else:
            st.metric("Total Transactions to Delete", len(filtered_df))
            
            # Show filtered transactions
            display_df = filtered_df.drop('Date_parsed', axis=1)
            st.dataframe(display_df, width='stretch')
            
            # Confirmation
            st.subheader("Confirm Deletion")
            
            confirm_text = st.text_input(
                f"Type 'DELETE {len(filtered_df)}' to confirm deletion",
                key="confirm_delete"
            )
            
            if st.button("🗑️ Delete Selected Transactions", type="secondary"):
                if confirm_text == f"DELETE {len(filtered_df)}":
                    # Get indices to keep (inverse of filtered)
                    indices_to_delete = filtered_df.index
                    df_to_keep = df.drop(indices_to_delete).reset_index(drop=True)
                    df_to_keep = df_to_keep.drop('Date_parsed', axis=1)
                    
                    try:
                        worksheet = "expenses_taras" if transaction_type == "Expense" else "income_taras"
                        conn.update(worksheet=worksheet, data=df_to_keep)
                        st.success(f"✅ Successfully deleted {len(filtered_df)} transactions!")
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting transactions: {e}")
                else:
                    st.error(f"Please type 'DELETE {len(filtered_df)}' exactly to confirm.")
    
    except Exception as e:
        st.error(f"Error loading transactions: {e}")

def view_all_transactions(conn):
    """View all transactions with filtering and search"""
    st.header("View All Transactions")
    
    transaction_type = st.radio("Transaction Type", ["Expense", "Income", "Both"], horizontal=True)
    
    try:
        expenses_df = pd.DataFrame()
        income_df = pd.DataFrame()
        
        if transaction_type in ["Expense", "Both"]:
            try:
                expenses_df = conn.read(worksheet="expenses_taras", ttl=0)
                if not expenses_df.empty:
                    expenses_df['Type'] = 'Expense'
            except:
                pass
        
        if transaction_type in ["Income", "Both"]:
            try:
                income_df = conn.read(worksheet="income_taras", ttl=0)
                if not income_df.empty:
                    income_df['Type'] = 'Income'
            except:
                pass
        
        if transaction_type == "Both":
            df = pd.concat([expenses_df, income_df], ignore_index=True)
        elif transaction_type == "Expense":
            df = expenses_df
        else:
            df = income_df
        
        if df.empty:
            st.info(f"No transactions found.")
            return
        
        # Parse dates and amounts
        df['Date_parsed'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', errors='coerce')
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
        
        # Sort by date (newest first)
        df = df.sort_values('Date_parsed', ascending=False)
        
        # Search and filter
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search = st.text_input("🔍 Search", placeholder="Search in all fields...")
        
        with col2:
            if transaction_type in ["Expense", "Both"] and 'Category' in df.columns:
                categories = ['All'] + sorted(df[df['Type'] == 'Expense']['Category'].dropna().unique().tolist())
                selected_category = st.selectbox("Category", categories)
        
        with col3:
            sort_by = st.selectbox("Sort by", ["Date (Newest)", "Date (Oldest)", "Amount (High-Low)", "Amount (Low-High)"])
        
        # Apply search
        if search:
            mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)
            df = df[mask]
        
        # Apply category filter
        if transaction_type in ["Expense", "Both"] and selected_category != "All":
            df = df[df['Category'] == selected_category]
        
        # Apply sorting
        if sort_by == "Date (Newest)":
            df = df.sort_values('Date_parsed', ascending=False)
        elif sort_by == "Date (Oldest)":
            df = df.sort_values('Date_parsed', ascending=True)
        elif sort_by == "Amount (High-Low)":
            df = df.sort_values('Amount', ascending=False)
        elif sort_by == "Amount (Low-High)":
            df = df.sort_values('Amount', ascending=True)
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Transactions", len(df))
        
        with col2:
            total_amount = df['Amount'].sum()
            st.metric("Total Amount", f"€{total_amount:,.2f}")
        
        with col3:
            avg_amount = df['Amount'].mean()
            st.metric("Average Amount", f"€{avg_amount:,.2f}")
        
        # Display dataframe
        display_df = df.drop('Date_parsed', axis=1).reset_index(drop=True)
        st.dataframe(display_df, width='stretch', height=400)
        
        # Export option
        if st.button("📥 Export to CSV"):
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"transactions_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    except Exception as e:
        st.error(f"Error loading transactions: {e}")

if __name__ == "__main__":
    main()
