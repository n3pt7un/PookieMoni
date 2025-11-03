import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
from config_utils import (
    get_initial_balance,
    get_budgets,
    get_budget_settings,
    calculate_budget_status,
    get_current_period_dates
)

# --- Page Configuration ---
st.set_page_config(
    page_title="PookieMoni - Personal Finance Tracker",
    page_icon="💰",
    layout="wide",
)

# --- Main Application ---
def main():
    st.title("💰 PookieMoni - Financial Dashboard")

    # Check if authentication is configured
    try:
        is_logged_in = st.user.is_logged_in
        user_name = st.user.name if is_logged_in else "Guest"
    except (AttributeError, KeyError):
        # Authentication not configured, run in demo mode
        is_logged_in = True
        user_name = "Demo User"
    
    if not is_logged_in:
        st.header("This app is private.")
        st.subheader("Please log in.")
        st.button("Log in with Google", on_click=st.login)
        return
    
    # Show welcome message
    if user_name != "Demo User":
        st.sidebar.success(f"Welcome, {user_name}!")
        st.button("Log out", on_click=st.logout)
    else:
        st.sidebar.info("Running in demo mode (authentication not configured)")
        st.sidebar.caption("Configure `.streamlit/secrets.toml` for Google OAuth")
    
    # Balance overview in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💰 Account Overview")
    
    try:
        balance_info = get_initial_balance()
        currency = balance_info['currency']
        initial_balance = balance_info['balance']
        
        # Get total income and expenses
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            expenses_df = conn.read(worksheet="expenses_taras", ttl=0)
            income_df = conn.read(worksheet="income_taras", ttl=0)
            
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
            st.sidebar.caption("Configure Google Sheets to see current balance")
    except Exception:
        pass
    
    # Navigation info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📍 Navigation")
    st.sidebar.markdown("- **💳 Transactions**: Add, edit & manage transactions")
    st.sidebar.markdown("- **📤 Upload CSV**: Import bank transactions")
    st.sidebar.markdown("- **⚙️ Settings**: Configure categories & budgets")
    st.sidebar.markdown("---")

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
        st.info("Have you added any transactions yet? Go to **💳 Transactions** page to add some!")
        st.info("📝 **Tip**: Configure your Google Sheets connection in **⚙️ Settings** → Google Sheets tab")
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
    
    # Get balance info
    balance_info = get_initial_balance()
    initial_balance = balance_info['balance']
    currency = balance_info['currency']
    
    total_income = income_df['Amount'].sum() if not income_df.empty else 0
    total_expenses = expenses_df['Amount'].sum() if not expenses_df.empty else 0
    net_savings = total_income - total_expenses
    current_balance = initial_balance + net_savings

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Initial Balance", f"{currency} {initial_balance:,.2f}")
    col2.metric("Total Income", f"{currency} {total_income:,.2f}")
    col3.metric("Total Expenses", f"{currency} {total_expenses:,.2f}")
    
    # Show current balance with delta
    balance_delta = current_balance - initial_balance
    col4.metric(
        "Current Balance", 
        f"{currency} {current_balance:,.2f}",
        delta=f"{balance_delta:+,.2f}",
        delta_color="normal"
    )
    
    # Visual progress indicator
    if initial_balance != 0:
        balance_change_pct = (balance_delta / abs(initial_balance)) * 100
        st.progress(
            min(max(balance_change_pct / 100, 0), 1),
            text=f"Balance Change: {balance_delta:+,.2f} {currency} ({balance_change_pct:+.1f}%)"
        )

    # --- Budget Overview ---
    st.header("📊 Budget Overview")
    
    budgets = get_budgets()
    budget_settings = get_budget_settings()
    
    if budgets:
        # Calculate spending by category for current period
        if not expenses_df.empty:
            # Get current period dates
            current_period_start, current_period_end = get_current_period_dates("monthly")
            
            # Filter expenses to current period
            period_expenses = expenses_df[
                (expenses_df['Date'] >= current_period_start) & 
                (expenses_df['Date'] <= current_period_end)
            ]
            
            if not period_expenses.empty:
                spending_by_category = period_expenses.groupby('Category')['Amount'].sum().to_dict()
            else:
                spending_by_category = {}
        else:
            spending_by_category = {}
        
        # Overall budget status
        total_budgeted = sum(b.get('amount', 0) for b in budgets.values() if b.get('is_active', True))
        total_spent = sum(spending_by_category.values())
        total_remaining = total_budgeted - total_spent
        
        if total_budgeted > 0:
            overall_percentage = (total_spent / total_budgeted) * 100
        else:
            overall_percentage = 0
        
        # Determine overall status
        if overall_percentage >= budget_settings['alert_threshold']:
            overall_status = "🔴"
            status_text = "Over Budget"
        elif overall_percentage >= budget_settings['warning_threshold']:
            overall_status = "🟡"
            status_text = "Warning"
        else:
            overall_status = "🟢"
            status_text = "On Track"
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Budgeted", f"€{total_budgeted:,.2f}")
        col2.metric("Total Spent", f"€{total_spent:,.2f}")
        col3.metric("Remaining", f"€{total_remaining:,.2f}")
        col4.metric("Status", f"{overall_status} {status_text}", f"{overall_percentage:.1f}%")
        
        # Budget progress bars by category
        st.subheader("Budget Progress by Category")
        
        # Create columns for budget cards
        num_budgets = len(budgets)
        cols_per_row = 2
        
        budget_items = list(budgets.items())
        for i in range(0, num_budgets, cols_per_row):
            cols = st.columns(cols_per_row)
            
            for j, col in enumerate(cols):
                if i + j < num_budgets:
                    category, budget = budget_items[i + j]
                    
                    with col:
                        spent = spending_by_category.get(category, 0)
                        budget_amount = budget.get('amount', 0)
                        
                        if budget_amount > 0:
                            percentage = (spent / budget_amount) * 100
                        else:
                            percentage = 0
                        
                        remaining = budget_amount - spent
                        
                        # Determine color based on percentage
                        if percentage >= budget_settings['alert_threshold']:
                            status_emoji = "🔴"
                            progress_color = "red"
                        elif percentage >= budget_settings['warning_threshold']:
                            status_emoji = "🟡"
                            progress_color = "orange"
                        else:
                            status_emoji = "🟢"
                            progress_color = "green"
                        
                        # Display budget card
                        st.markdown(f"**{status_emoji} {category}**")
                        st.progress(min(percentage / 100, 1.0))
                        st.caption(f"€{spent:,.2f} / €{budget_amount:,.2f} ({percentage:.1f}%)")
                        
                        if remaining >= 0:
                            st.caption(f"€{remaining:,.2f} remaining")
                        else:
                            st.caption(f"⚠️ €{abs(remaining):,.2f} over budget!")
        
        # Budget vs Actual Comparison Chart
        st.subheader("Budget vs. Actual Spending")
        
        comparison_data = []
        for category, budget in budgets.items():
            if budget.get('is_active', True):
                spent = spending_by_category.get(category, 0)
                budget_amount = budget.get('amount', 0)
                
                comparison_data.append({
                    'Category': category,
                    'Budgeted': budget_amount,
                    'Actual': spent
                })
        
        if comparison_data:
            comparison_df = pd.DataFrame(comparison_data)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Budgeted',
                x=comparison_df['Category'],
                y=comparison_df['Budgeted'],
                marker_color='lightblue'
            ))
            fig.add_trace(go.Bar(
                name='Actual',
                x=comparison_df['Category'],
                y=comparison_df['Actual'],
                marker_color='salmon'
            ))
            
            fig.update_layout(
                barmode='group',
                title='Budget vs. Actual by Category',
                xaxis_title='Category',
                yaxis_title='Amount (€)',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Spending rate analysis
        st.subheader("Spending Rate Analysis")
        
        # Calculate days into the month
        now = datetime.now()
        current_period_start, current_period_end = get_current_period_dates("monthly")
        
        days_in_period = (current_period_end - current_period_start).days + 1
        days_elapsed = (now - current_period_start).days + 1
        period_progress = (days_elapsed / days_in_period) * 100
        
        if total_budgeted > 0:
            spending_rate = (total_spent / total_budgeted) * 100
            
            if spending_rate > period_progress + 10:
                pace_status = "⚠️ Spending faster than expected"
                pace_color = "red"
            elif spending_rate < period_progress - 10:
                pace_status = "✅ Spending slower than expected"
                pace_color = "green"
            else:
                pace_status = "➡️ Spending on pace"
                pace_color = "blue"
            
            # Project end of period spending
            if days_elapsed > 0:
                projected_total = (total_spent / days_elapsed) * days_in_period
                projected_over = projected_total - total_budgeted
            else:
                projected_total = 0
                projected_over = 0
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Period Progress",
                    f"Day {days_elapsed} of {days_in_period}",
                    f"{period_progress:.1f}%"
                )
            
            with col2:
                st.metric(
                    "Spending Rate",
                    f"{spending_rate:.1f}%",
                    pace_status
                )
            
            with col3:
                if projected_over > 0:
                    st.metric(
                        "Projected Month-End",
                        f"€{projected_total:,.2f}",
                        f"€{projected_over:+,.2f} over",
                        delta_color="inverse"
                    )
                else:
                    st.metric(
                        "Projected Month-End",
                        f"€{projected_total:,.2f}",
                        f"€{abs(projected_over):,.2f} under",
                        delta_color="normal"
                    )
            
            # Tips based on spending
            if spending_rate > period_progress + 10:
                # Find categories that are over budget
                over_categories = []
                for category, budget in budgets.items():
                    spent = spending_by_category.get(category, 0)
                    budget_amount = budget.get('amount', 0)
                    if budget_amount > 0 and (spent / budget_amount) > 1.0:
                        over_categories.append(category)
                
                if over_categories:
                    st.warning(f"💡 **Tip**: Consider reducing spending in: {', '.join(over_categories)}")
    else:
        st.info("No budgets configured. Visit the ⚙️ Settings page to set up your budgets!")

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
        expenses_over_time = expenses_df.set_index('Date').resample('MS')['Amount'].sum().reset_index()
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
        income_summary = income_df.set_index('Date').resample('MS')['Amount'].sum().rename('Income')
        expenses_summary = expenses_df.set_index('Date').resample('MS')['Amount'].sum().rename('Expenses')
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