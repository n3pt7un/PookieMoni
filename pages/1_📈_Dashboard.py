import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, timedelta
from config_utils import (
    get_initial_balance,
    get_budgets,
    get_budget_settings,
    get_current_period_dates,
    get_categories
)
from user_utils import (
    get_current_user,
    get_user_and_shared_data,
    get_user_display_name,
    render_user_selector,
    get_worksheet_names
)

# --- Page Configuration ---
st.set_page_config(
    page_title="Dashboard",
    page_icon="📈",
    layout="wide",
)

# Custom CSS for Copilot Money-inspired design
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
    }
    
    /* Card styling */
    .metric-card {
        background: linear-gradient(135deg, #1e2746 0%, #2a3454 100%);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 48px rgba(0, 0, 0, 0.4);
    }
    
    /* Budget card colors */
    .budget-on-track {
        border-left: 4px solid #00e676;
    }
    
    .budget-warning {
        border-left: 4px solid #ffd600;
    }
    
    .budget-alert {
        border-left: 4px solid #ff5252;
    }
    
    /* Typography */
    .metric-title {
        color: #9ca3af;
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 8px;
    }
    
    .metric-value {
        color: #ffffff;
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 4px;
    }
    
    .metric-subtitle {
        color: #6b7280;
        font-size: 12px;
    }
    
    /* Category chip */
    .category-chip {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin: 4px;
    }
    
    /* Spending status */
    .spending-up {
        color: #ff5252;
    }
    
    .spending-down {
        color: #00e676;
    }
    
    .spending-neutral {
        color: #ffd600;
    }
    
    /* Section headers */
    .section-header {
        color: #ffffff;
        font-size: 24px;
        font-weight: 700;
        margin: 32px 0 16px 0;
    }
    
    /* User avatar */
    .user-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)

def format_currency(amount: float) -> str:
    """Format currency with proper symbol."""
    return f"€{amount:,.2f}"

def get_trend_indicator(current: float, previous: float) -> tuple:
    """Get trend indicator (arrow and color)."""
    if previous == 0:
        return "→", "neutral"
    
    change_pct = ((current - previous) / abs(previous)) * 100
    
    if abs(change_pct) < 3:
        return "=", "neutral"
    elif change_pct > 0:
        return f"↑ {abs(change_pct):.0f}%", "up"
    else:
        return f"↓ {abs(change_pct):.0f}%", "down"

def main():
    # Render user selector in sidebar
    render_user_selector()
    
    current_user = get_current_user()
    user_name = get_user_display_name(current_user)
    
    # Header with user info
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"# 👋 Welcome back, {user_name}!")
        st.markdown(f"*{datetime.now().strftime('%A, %B %d, %Y')}*")
    
    # Check if authentication is configured
    try:
        is_logged_in = st.user.is_logged_in
    except (AttributeError, KeyError):
        is_logged_in = True
    
    if not is_logged_in:
        st.warning("Please log in from the main page to view the dashboard.")
        return

    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        st.error(f"Failed to connect to Google Sheets: {e}")
        return

    # --- Load Data ---
    try:
        if current_user in ["user1", "user2"]:
            expenses_df = get_user_and_shared_data(conn, current_user, "expenses")
            income_df = get_user_and_shared_data(conn, current_user, "income")
            try:
                recurrings_df = get_user_and_shared_data(conn, current_user, "recurrings")
            except:
                recurrings_df = pd.DataFrame()
        else:
            # Shared view
            worksheets = get_worksheet_names("shared")
            expenses_df = conn.read(worksheet=worksheets["expenses"], ttl=0)
            income_df = conn.read(worksheet=worksheets["income"], ttl=0)
            try:
                recurrings_df = conn.read(worksheet=worksheets["recurrings"], ttl=0)
            except:
                recurrings_df = pd.DataFrame()
    except Exception as e:
        st.error(f"Could not load data: {e}")
        st.info("Have you added any transactions yet?")
        return

    # --- Data Cleaning ---
    if not expenses_df.empty and 'Amount' in expenses_df.columns and 'Date' in expenses_df.columns:
        expenses_df['Amount'] = pd.to_numeric(expenses_df['Amount'], errors='coerce')
        expenses_df['Date'] = pd.to_datetime(expenses_df['Date'], format='mixed', dayfirst=True, errors='coerce')
        expenses_df = expenses_df.dropna(subset=['Amount', 'Date'])
    elif not expenses_df.empty:
        expenses_df = pd.DataFrame()  # Reset if columns are missing

    if not income_df.empty and 'Amount' in income_df.columns and 'Date' in income_df.columns:
        income_df['Amount'] = pd.to_numeric(income_df['Amount'], errors='coerce')
        income_df['Date'] = pd.to_datetime(income_df['Date'], format='mixed', dayfirst=True, errors='coerce')
        income_df = income_df.dropna(subset=['Amount', 'Date'])
    elif not income_df.empty:
        income_df = pd.DataFrame()  # Reset if columns are missing
    
    if not recurrings_df.empty and 'Amount' in recurrings_df.columns:
        recurrings_df['Amount'] = pd.to_numeric(recurrings_df['Amount'], errors='coerce')
        if 'Next_Due' in recurrings_df.columns:
            recurrings_df['Next_Due'] = pd.to_datetime(recurrings_df['Next_Due'], format='mixed', dayfirst=True, errors='coerce')

    if expenses_df.empty and income_df.empty:
        st.info("No transaction data found. Start by adding some transactions from the main page!")
        return
    
    # --- Calculate Key Metrics ---
    current_period_start, current_period_end = get_current_period_dates("monthly")
    
    # Filter to current period
    period_expenses = expenses_df[
        (expenses_df['Date'] >= current_period_start) & 
        (expenses_df['Date'] <= current_period_end)
    ] if not expenses_df.empty else pd.DataFrame()
    
    period_income = income_df[
        (income_df['Date'] >= current_period_start) & 
        (income_df['Date'] <= current_period_end)
    ] if not income_df.empty else pd.DataFrame()
    
    # Previous period for comparison
    prev_period_start = current_period_start - timedelta(days=30)
    prev_period_end = current_period_start - timedelta(days=1)
    
    prev_expenses = expenses_df[
        (expenses_df['Date'] >= prev_period_start) & 
        (expenses_df['Date'] <= prev_period_end)
    ] if not expenses_df.empty else pd.DataFrame()
    
    total_spent = period_expenses['Amount'].sum() if not period_expenses.empty else 0
    total_income = period_income['Amount'].sum() if not period_income.empty else 0
    prev_spent = prev_expenses['Amount'].sum() if not prev_expenses.empty else 0
    
    # Budget calculations
    budgets = get_budgets()
    total_budgeted = sum(b.get('amount', 0) for b in budgets.values() if b.get('is_active', True))
    budget_remaining = total_budgeted - total_spent
    
    # --- TOP METRICS ROW ---
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        budget_percentage = (total_spent / total_budgeted * 100) if total_budgeted > 0 else 0
        status_class = "budget-on-track" if budget_percentage < 80 else ("budget-warning" if budget_percentage < 100 else "budget-alert")
        
        st.markdown(f"""
        <div class="metric-card {status_class}">
            <div class="metric-title">BUDGET</div>
            <div class="metric-value">{format_currency(budget_remaining)}</div>
            <div class="metric-subtitle">out of {format_currency(total_budgeted)} budgeted</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        spending_trend, trend_type = get_trend_indicator(total_spent, prev_spent)
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">SPENDING</div>
            <div class="metric-value">{format_currency(total_spent)}</div>
            <div class="metric-subtitle spending-{trend_type}">{spending_trend} vs last month</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        recurrings_total = recurrings_df['Amount'].sum() if not recurrings_df.empty and 'Amount' in recurrings_df.columns else 0
        recurrings_count = len(recurrings_df) if not recurrings_df.empty else 0
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">RECURRINGS</div>
            <div class="metric-value">{format_currency(recurrings_total)}</div>
            <div class="metric-subtitle">{recurrings_count} active subscriptions</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        net_income = total_income - total_spent
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">NET INCOME</div>
            <div class="metric-value">{format_currency(net_income)}</div>
            <div class="metric-subtitle">this month</div>
        </div>
        """, unsafe_allow_html=True)
    
    # --- SPENDING BREAKDOWN ---
    st.markdown("<div class='section-header'>💰 Spending Breakdown</div>", unsafe_allow_html=True)
    
    if not period_expenses.empty and 'Category' in period_expenses.columns:
        spending_by_category = period_expenses.groupby('Category')['Amount'].sum().sort_values(ascending=False)
        
        # Create two columns for spending breakdown
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Category breakdown with progress bars
            for category in spending_by_category.index[:8]:  # Top 8 categories
                amount = spending_by_category[category]
                percentage = (amount / total_spent * 100) if total_spent > 0 else 0
                
                # Get budget for category if exists
                category_budget = budgets.get(category, {}).get('amount', 0)
                budget_pct = (amount / category_budget * 100) if category_budget > 0 else 0
                
                # Determine color based on budget
                if category_budget > 0:
                    if budget_pct >= 100:
                        bar_color = "#ff5252"
                        status_emoji = "🔴"
                    elif budget_pct >= 80:
                        bar_color = "#ffd600"
                        status_emoji = "🟡"
                    else:
                        bar_color = "#00e676"
                        status_emoji = "🟢"
                else:
                    bar_color = "#3b82f6"
                    status_emoji = "🔵"
                
                # Calculate trend vs previous period
                if not prev_expenses.empty and 'Category' in prev_expenses.columns:
                    prev_cat_amount = prev_expenses[prev_expenses['Category'] == category]['Amount'].sum()
                    trend, trend_type = get_trend_indicator(amount, prev_cat_amount)
                else:
                    trend = "→"
                    trend_type = "neutral"
                
                col_a, col_b, col_c = st.columns([3, 1, 1])
                
                with col_a:
                    st.markdown(f"**{status_emoji} {category}**")
                    st.progress(min(percentage / 100, 1.0))
                
                with col_b:
                    st.markdown(f"**{format_currency(amount)}**")
                    st.caption(f"{percentage:.1f}% of spending")
                
                with col_c:
                    if category_budget > 0:
                        st.markdown(f"**{budget_pct:.0f}%**")
                        st.caption(f"of {format_currency(category_budget)}")
                    else:
                        st.markdown(f"**{trend}**")
                        st.caption("vs last month")
        
        with col2:
            # Pie chart
            fig = px.pie(
                values=spending_by_category.values[:5],
                names=spending_by_category.index[:5],
                title="Top 5 Categories",
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                showlegend=True,
                height=300
            )
            st.plotly_chart(fig, width='stretch')
    else:
        st.info("No spending data available for this period.")
    
    # --- SPENDING TREND ---
    st.markdown("<div class='section-header'>📊 Spending Trend</div>", unsafe_allow_html=True)
    
    if not expenses_df.empty:
        # Get last 6 months of data
        six_months_ago = datetime.now() - timedelta(days=180)
        recent_expenses = expenses_df[expenses_df['Date'] >= six_months_ago]
        
        if not recent_expenses.empty:
            # Group by month
            monthly_spending = recent_expenses.set_index('Date').resample('MS')['Amount'].sum().reset_index()
            monthly_spending['Month'] = monthly_spending['Date'].dt.strftime('%b %Y')
            
            # Create line chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=monthly_spending['Month'],
                y=monthly_spending['Amount'],
                mode='lines+markers',
                name='Spending',
                line=dict(color='#3b82f6', width=3),
                marker=dict(size=8, color='#3b82f6'),
                fill='tozeroy',
                fillcolor='rgba(59, 130, 246, 0.1)'
            ))
            
            # Add budget line if available
            if total_budgeted > 0:
                fig.add_hline(
                    y=total_budgeted,
                    line_dash="dash",
                    line_color="#ffd600",
                    annotation_text="Budget",
                    annotation_position="right"
                )
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
                hovermode='x unified',
                height=300
            )
            
            st.plotly_chart(fig, width='stretch')
    
    # --- RECURRING PAYMENTS ---
    st.markdown("<div class='section-header'>🔄 Recurring Payments</div>", unsafe_allow_html=True)
    
    if not recurrings_df.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### Active Subscriptions")
            
            # Sort by next due date
            if 'Next_Due' in recurrings_df.columns:
                recurrings_df = recurrings_df.sort_values('Next_Due')
            
            for idx, row in recurrings_df.head(8).iterrows():
                name = row.get('Name', 'Unknown')
                amount = row.get('Amount', 0)
                frequency = row.get('Frequency', 'Monthly')
                next_due = row.get('Next_Due', None)
                
                col_a, col_b, col_c = st.columns([2, 1, 1])
                
                with col_a:
                    st.markdown(f"**{name}**")
                    st.caption(f"{frequency}")
                
                with col_b:
                    st.markdown(f"**{format_currency(amount)}**")
                
                with col_c:
                    if pd.notna(next_due):
                        days_until = (next_due - datetime.now()).days
                        if days_until < 0:
                            st.markdown(f"🔴 **Overdue**")
                        elif days_until <= 3:
                            st.markdown(f"🟡 **{days_until}d**")
                        else:
                            st.markdown(f"🟢 **{days_until}d**")
                    else:
                        st.markdown("—")
        
        with col2:
            # Summary box
            st.markdown("### Summary")
            st.metric("Total Monthly", format_currency(recurrings_total))
            st.metric("Active Count", recurrings_count)
            
            if not recurrings_df.empty and 'Next_Due' in recurrings_df.columns:
                upcoming = recurrings_df[
                    (pd.notna(recurrings_df['Next_Due'])) &
                    (recurrings_df['Next_Due'] <= datetime.now() + timedelta(days=7))
                ]
                st.metric("Due This Week", len(upcoming))
    else:
        st.info("No recurring payments configured. Add them in Settings to track subscriptions!")
    
    # --- TRANSACTION RULES ---
    st.markdown("<div class='section-header'>🏷️ Transaction Rules</div>", unsafe_allow_html=True)
    
    categories = get_categories()
    
    col1, col2, col3 = st.columns(3)
    
    rule_examples = [
        ("Food & Dining", "🍕", ["pizza", "restaurant", "cafe"]),
        ("Transportation", "🚗", ["uber", "gas", "parking"]),
        ("Shopping", "🛍️", ["amazon", "store", "mall"]),
        ("Bills & Utilities", "💡", ["electric", "water", "internet"]),
        ("Entertainment", "🎬", ["netflix", "spotify", "cinema"]),
        ("Health", "🏥", ["pharmacy", "hospital", "doctor"])
    ]
    
    for idx, (category, emoji, keywords) in enumerate(rule_examples[:6]):
        col = [col1, col2, col3][idx % 3]
        
        with col:
            st.markdown(f"**{emoji} {category}**")
            keywords_str = " • ".join([f"`{kw}`" for kw in keywords[:3]])
            st.caption(keywords_str)
    
    # --- RECENT TRANSACTIONS ---
    st.markdown("<div class='section-header'>📝 Recent Transactions</div>", unsafe_allow_html=True)
    
    if not period_expenses.empty:
        recent = period_expenses.sort_values('Date', ascending=False).head(10)
        
        # Display in a clean format
        for idx, row in recent.iterrows():
            date = row['Date'].strftime('%b %d')
            store = row.get('Store', 'Unknown')
            category = row.get('Category', 'Other')
            amount = row['Amount']
            source = row.get('_source', 'personal')
            
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            
            with col1:
                st.markdown(f"**{store}**")
            
            with col2:
                st.caption(f"{category}")
            
            with col3:
                st.markdown(f"**{format_currency(amount)}**")
            
            with col4:
                badge = "🤝 Shared" if source == 'shared' else "👤 Personal"
                st.caption(badge)

if __name__ == "__main__":
    main()
