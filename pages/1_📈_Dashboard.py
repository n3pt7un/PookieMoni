import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="Dashboard",
    page_icon="📈",
    layout="wide",
)

# --- Main Application ---
def main():
    st.title("📈 Financial Dashboard")

    if not st.user.is_logged_in:
        st.warning("Please log in from the main page to view the dashboard.")
        return

    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        st.error(f"Failed to connect to Google Sheets: {e}")
        st.info("Please ask the app owner to configure the Google Sheets connection.")
        return

    # --- Load Data ---
    try:
        expenses_df = conn.read(worksheet="expenses_taras", ttl=0)
        income_df = conn.read(worksheet="income_taras", ttl=0)
    except Exception as e:
        st.error(f"Could not load data from Google Sheets. Error: {e}")
        st.info("Have you added any transactions yet from the main page?")
        return


    # --- Data Cleaning ---
    if not expenses_df.empty:
        expenses_df['Amount'] = pd.to_numeric(expenses_df['Amount'])
        # Handle multiple date formats: ISO (YYYY-MM-DD), dd-M-Y, or mixed formats
        expenses_df['Date'] = pd.to_datetime(expenses_df['Date'], format='mixed', dayfirst=True)

    if not income_df.empty:
        income_df['Amount'] = pd.to_numeric(income_df['Amount'])
        # Handle multiple date formats: ISO (YYYY-MM-DD), dd-M-Y, or mixed formats
        income_df['Date'] = pd.to_datetime(income_df['Date'], format='mixed', dayfirst=True)

    if expenses_df.empty and income_df.empty:
        st.info("No transaction data found. Please add some from the main page.")
        return
    
    # --- Date Range Filter ---
    st.header("Filter Data by Date")

    min_date = min(expenses_df['Date'].min() if not expenses_df.empty else datetime.now(),
                   income_df['Date'].min() if not income_df.empty else datetime.now()).date()
    max_date = max(expenses_df['Date'].max() if not expenses_df.empty else datetime.now(),
                   income_df['Date'].max() if not income_df.empty else datetime.now()).date()

    if min_date > max_date:
        min_date = max_date


    start_date, end_date = st.date_input(
        "Select a date range",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date,
    )

    if start_date and end_date:
        start_datetime = pd.to_datetime(start_date)
        end_datetime = pd.to_datetime(end_date)
        # Filter dataframes
        expenses_df = expenses_df[(expenses_df['Date'] >= start_datetime) & (expenses_df['Date'] <= end_datetime)]
        income_df = income_df[(income_df['Date'] >= start_datetime) & (income_df['Date'] <= end_datetime)]


    # --- Key Metrics ---
    st.header("Key Metrics")
    total_income = income_df['Amount'].sum()
    total_expenses = expenses_df['Amount'].sum()
    net_savings = total_income - total_expenses

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Income", f"£{total_income:,.2f}")
    col2.metric("Total Expenses", f"£{total_expenses:,.2f}")
    col3.metric("Net Savings", f"£{net_savings:,.2f}")

    # --- Visualizations ---
    st.header("Expenses Analysis")
    if not expenses_df.empty:
        # Pie chart of expenses by category
        fig_cat = px.pie(expenses_df, names='Category', values='Amount', title='Expenses by Category')
        st.plotly_chart(fig_cat, use_container_width=True)

        # Treemap of expenses
        fig_treemap = px.treemap(expenses_df, path=['Category', 'Store'], values='Amount', title='Expenses Breakdown')
        st.plotly_chart(fig_treemap, use_container_width=True)

        # Bar chart of expenses over time
        expenses_over_time = expenses_df.set_index('Date').resample('M')['Amount'].sum().reset_index()
        fig_time = px.bar(expenses_over_time, x='Date', y='Amount', title='Monthly Expenses')
        st.plotly_chart(fig_time, use_container_width=True)
    else:
        st.info("No expense data to display for the selected range.")

    st.header("Income Analysis")
    if not income_df.empty:
        # Pie chart of income by source
        fig_source = px.pie(income_df, names='Source', values='Amount', title='Income by Source')
        st.plotly_chart(fig_source, use_container_width=True)
    else:
        st.info("No income data to display for the selected range.")
        
    st.header("Income vs. Expenses")
    if not income_df.empty or not expenses_df.empty:
        # Combine data for comparison
        income_summary = income_df.set_index('Date').resample('M')['Amount'].sum().rename('Income')
        expenses_summary = expenses_df.set_index('Date').resample('M')['Amount'].sum().rename('Expenses')
        comparison_df = pd.concat([income_summary, expenses_summary], axis=1).fillna(0).reset_index()
        
        if not comparison_df.empty:
            fig_comparison = px.bar(comparison_df, x='Date', y=['Income', 'Expenses'], barmode='group', title='Monthly Income vs. Expenses')
            st.plotly_chart(fig_comparison, use_container_width=True)
        else:
            st.info("No data for income vs. expenses comparison in the selected range.")
    else:
        st.info("Insufficient data for income vs. expenses comparison.")

    # --- Detailed Transactions ---
    st.header("Recent Transactions")
    if not expenses_df.empty:
        st.dataframe(expenses_df.sort_values('Date', ascending=False).head(10))
    else:
        st.write("No recent expenses in the selected date range.")

if __name__ == "__main__":
    main() 