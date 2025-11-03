import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, timedelta
from config_utils import get_categories
from user_utils import (
    get_current_user,
    get_user_display_name,
    render_user_selector,
    get_worksheet_names,
    get_user_and_shared_data
)

# --- Page Configuration ---
st.set_page_config(
    page_title="Recurring Expenses",
    page_icon="🔄",
    layout="wide",
)

def calculate_next_due_date(last_paid: datetime, frequency: str) -> datetime:
    """Calculate next due date based on frequency."""
    if frequency == "Daily":
        return last_paid + timedelta(days=1)
    elif frequency == "Weekly":
        return last_paid + timedelta(weeks=1)
    elif frequency == "Bi-weekly":
        return last_paid + timedelta(weeks=2)
    elif frequency == "Monthly":
        # Approximate month as 30 days
        return last_paid + timedelta(days=30)
    elif frequency == "Quarterly":
        return last_paid + timedelta(days=90)
    elif frequency == "Yearly":
        return last_paid + timedelta(days=365)
    else:
        return last_paid + timedelta(days=30)

def main():
    st.title("🔄 Recurring Expenses & Subscriptions")
    
    # Render user selector
    render_user_selector()
    
    current_user = get_current_user()
    user_name = get_user_display_name(current_user)
    
    # Check if authentication is configured
    try:
        is_logged_in = st.user.is_logged_in
    except (AttributeError, KeyError):
        is_logged_in = True
    
    if not is_logged_in:
        st.warning("Please log in from the main page.")
        return
    
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        st.error(f"Failed to connect to Google Sheets: {e}")
        return
    
    st.markdown(f"""
    Manage your recurring expenses and subscriptions. Track monthly bills, 
    subscriptions, and other regular payments for **{user_name}**.
    """)
    
    # Create tabs for different operations
    tab1, tab2, tab3 = st.tabs(["📋 View All", "➕ Add New", "📊 Analysis"])
    
    with tab1:
        view_recurrings(conn, current_user, user_name)
    
    with tab2:
        add_recurring(conn, current_user, user_name)
    
    with tab3:
        analyze_recurrings(conn, current_user, user_name)

def view_recurrings(conn, current_user, user_name):
    """View and manage existing recurring expenses."""
    st.header(f"Recurring Expenses for {user_name}")
    
    try:
        if current_user in ["user1", "user2"]:
            recurrings_df = get_user_and_shared_data(conn, current_user, "recurrings")
        else:
            worksheets = get_worksheet_names("shared")
            recurrings_df = conn.read(worksheet=worksheets["recurrings"], ttl=0)
    except Exception as e:
        st.info("No recurring expenses found. Add your first one in the 'Add New' tab!")
        return
    
    if recurrings_df.empty:
        st.info("No recurring expenses found. Add your first one in the 'Add New' tab!")
        return
    
    # Data cleaning
    if 'Amount' in recurrings_df.columns:
        recurrings_df['Amount'] = pd.to_numeric(recurrings_df['Amount'], errors='coerce')
    
    if 'Next_Due' in recurrings_df.columns:
        recurrings_df['Next_Due'] = pd.to_datetime(recurrings_df['Next_Due'], format='mixed', dayfirst=True, errors='coerce')
    
    # Sort by next due date
    if 'Next_Due' in recurrings_df.columns:
        recurrings_df = recurrings_df.sort_values('Next_Due')
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_monthly = recurrings_df[recurrings_df['Frequency'] == 'Monthly']['Amount'].sum() if 'Frequency' in recurrings_df.columns else 0
        st.metric("Total Monthly", f"€{total_monthly:,.2f}")
    
    with col2:
        active_count = len(recurrings_df[recurrings_df.get('Status', 'Active') == 'Active'])
        st.metric("Active Subscriptions", active_count)
    
    with col3:
        if 'Next_Due' in recurrings_df.columns:
            upcoming = len(recurrings_df[
                (pd.notna(recurrings_df['Next_Due'])) &
                (recurrings_df['Next_Due'] <= datetime.now() + timedelta(days=7))
            ])
            st.metric("Due This Week", upcoming)
        else:
            st.metric("Due This Week", "—")
    
    with col4:
        total_yearly = recurrings_df['Amount'].sum() * 12 if not recurrings_df.empty else 0
        st.metric("Est. Yearly Cost", f"€{total_yearly:,.2f}")
    
    st.markdown("---")
    
    # Display recurring expenses in cards
    st.subheader("All Recurring Expenses")
    
    for idx, row in recurrings_df.iterrows():
        name = row.get('Name', 'Unknown')
        amount = row.get('Amount', 0)
        frequency = row.get('Frequency', 'Monthly')
        category = row.get('Category', 'Other')
        next_due = row.get('Next_Due', None)
        status = row.get('Status', 'Active')
        source = row.get('_source', 'personal')
        
        # Determine status color
        if pd.notna(next_due):
            days_until = (next_due - datetime.now()).days
            if days_until < 0:
                status_color = "🔴"
                status_text = "Overdue"
            elif days_until <= 3:
                status_color = "🟡"
                status_text = f"Due in {days_until} days"
            else:
                status_color = "🟢"
                status_text = f"Due in {days_until} days"
        else:
            status_color = "⚪"
            status_text = "No due date"
        
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
        
        with col1:
            st.markdown(f"**{status_color} {name}**")
            st.caption(f"{category} • {frequency}")
        
        with col2:
            st.markdown(f"**€{amount:,.2f}**")
            st.caption(f"per {frequency.lower()}")
        
        with col3:
            st.markdown(f"**{status_text}**")
            if pd.notna(next_due):
                st.caption(next_due.strftime("%b %d, %Y"))
        
        with col4:
            badge = "🤝 Shared" if source == 'shared' else "👤 Personal"
            st.caption(badge)
        
        with col5:
            if st.button("🗑️", key=f"delete_{idx}"):
                st.warning("Delete functionality coming soon!")

def add_recurring(conn, current_user, user_name):
    """Add a new recurring expense."""
    st.header(f"Add New Recurring Expense for {user_name}")
    
    categories = get_categories()
    
    # Option to choose between personal and shared
    if current_user in ["user1", "user2"]:
        scope = st.radio(
            "Add to:",
            ["Personal", "Shared"],
            horizontal=True,
            help="Personal recurrings are only visible to you. Shared recurrings are visible to both users."
        )
    else:
        scope = "Shared"
    
    with st.form("add_recurring_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Name",
                placeholder="e.g., Netflix, Spotify, Rent",
                help="Name of the recurring expense or subscription"
            )
            
            amount = st.number_input(
                "Amount (€)",
                min_value=0.0,
                step=1.0,
                format="%.2f"
            )
            
            category = st.selectbox(
                "Category",
                options=categories,
                help="Category for this recurring expense"
            )
        
        with col2:
            frequency = st.selectbox(
                "Frequency",
                options=["Daily", "Weekly", "Bi-weekly", "Monthly", "Quarterly", "Yearly"],
                index=3,  # Default to Monthly
                help="How often this expense recurs"
            )
            
            next_due = st.date_input(
                "Next Due Date",
                value=datetime.now() + timedelta(days=30),
                help="When is this expense next due?"
            )
            
            status = st.selectbox(
                "Status",
                options=["Active", "Paused", "Cancelled"],
                help="Current status of this recurring expense"
            )
        
        notes = st.text_area(
            "Notes (optional)",
            placeholder="Add any additional notes about this recurring expense"
        )
        
        submitted = st.form_submit_button("Add Recurring Expense", type="primary")
        
        if submitted:
            if not name:
                st.error("Please enter a name for this recurring expense.")
            elif amount <= 0:
                st.error("Please enter a valid amount.")
            else:
                # Create dataframe
                recurring_df = pd.DataFrame([{
                    "Name": name,
                    "Amount": amount,
                    "Category": category,
                    "Frequency": frequency,
                    "Next_Due": next_due.strftime("%d-%m-%Y"),
                    "Status": status,
                    "Notes": notes,
                    "Added_Date": datetime.now().strftime("%d-%m-%Y")
                }])
                
                # Determine worksheet
                if scope == "Shared":
                    worksheets = get_worksheet_names("shared")
                    worksheet_name = worksheets["recurrings"]
                else:
                    worksheets = get_worksheet_names(current_user)
                    worksheet_name = worksheets["recurrings"]
                
                try:
                    # Read existing data and append
                    existing_data = conn.read(worksheet=worksheet_name, ttl=0)
                    updated_df = pd.concat([existing_data, recurring_df], ignore_index=True)
                    conn.update(worksheet=worksheet_name, data=updated_df)
                    st.success(f"✅ Recurring expense '{name}' added successfully to {scope} account!")
                except Exception as e:
                    if "WorksheetNotFound" in str(e):
                        # Create new worksheet
                        conn.update(worksheet=worksheet_name, data=recurring_df)
                        st.success(f"✅ Recurring expense '{name}' added successfully to {scope} account!")
                    else:
                        st.error(f"Error adding recurring expense: {e}")

def analyze_recurrings(conn, current_user, user_name):
    """Analyze recurring expenses."""
    st.header(f"Recurring Expenses Analysis for {user_name}")
    
    try:
        if current_user in ["user1", "user2"]:
            recurrings_df = get_user_and_shared_data(conn, current_user, "recurrings")
        else:
            worksheets = get_worksheet_names("shared")
            recurrings_df = conn.read(worksheet=worksheets["recurrings"], ttl=0)
    except Exception:
        st.info("No data available for analysis.")
        return
    
    if recurrings_df.empty:
        st.info("No data available for analysis. Add recurring expenses first!")
        return
    
    # Data cleaning
    if 'Amount' in recurrings_df.columns:
        recurrings_df['Amount'] = pd.to_numeric(recurrings_df['Amount'], errors='coerce')
    
    # Analysis by category
    st.subheader("Spending by Category")
    
    if 'Category' in recurrings_df.columns:
        category_spending = recurrings_df.groupby('Category')['Amount'].sum().sort_values(ascending=False)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            for category in category_spending.index:
                amount = category_spending[category]
                percentage = (amount / category_spending.sum() * 100)
                
                st.markdown(f"**{category}**")
                st.progress(percentage / 100)
                st.caption(f"€{amount:,.2f} per month ({percentage:.1f}%)")
        
        with col2:
            import plotly.express as px
            fig = px.pie(
                values=category_spending.values,
                names=category_spending.index,
                title="Monthly Recurrings by Category",
                hole=0.4
            )
            st.plotly_chart(fig, width='stretch')
    
    # Analysis by frequency
    st.subheader("Spending by Frequency")
    
    if 'Frequency' in recurrings_df.columns:
        frequency_spending = recurrings_df.groupby('Frequency')['Amount'].sum().sort_values(ascending=False)
        
        for frequency in frequency_spending.index:
            amount = frequency_spending[frequency]
            count = len(recurrings_df[recurrings_df['Frequency'] == frequency])
            
            st.markdown(f"**{frequency}**: €{amount:,.2f} ({count} items)")
    
    # Upcoming expenses
    st.subheader("Upcoming Expenses (Next 30 Days)")
    
    if 'Next_Due' in recurrings_df.columns:
        recurrings_df['Next_Due'] = pd.to_datetime(recurrings_df['Next_Due'], format='mixed', dayfirst=True, errors='coerce')
        
        thirty_days = datetime.now() + timedelta(days=30)
        upcoming = recurrings_df[
            (pd.notna(recurrings_df['Next_Due'])) &
            (recurrings_df['Next_Due'] <= thirty_days)
        ].sort_values('Next_Due')
        
        if not upcoming.empty:
            upcoming_total = upcoming['Amount'].sum()
            st.metric("Total Due in Next 30 Days", f"€{upcoming_total:,.2f}")
            
            st.dataframe(upcoming[['Name', 'Amount', 'Category', 'Next_Due']], width='stretch')
        else:
            st.info("No expenses due in the next 30 days.")

if __name__ == "__main__":
    main()

