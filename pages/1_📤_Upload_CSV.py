import streamlit as st
import pandas as pd
import re
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="Upload CSV Data",
    page_icon="📤",
    layout="wide",
)

def clean_merchant_name(description):
    """Extract clean merchant name from transaction description"""
    # Remove common prefixes and suffixes
    cleaned = description.replace('POS CARTA CA DEBIT VISA N. ****4682 DEL ', '')
    cleaned = re.sub(r'C /O ', '', cleaned)
    cleaned = re.sub(r'AFT CARTA CA DEBIT VISA N\. \*\*\*\*4682 DEL.*?C /O ', '', cleaned)
    cleaned = re.sub(r'\d{2}/\d{2}/\d{2} ORE \d{2}:\d{2} ', '', cleaned)
    cleaned = re.sub(r'\+\d+', '', cleaned)  # Remove phone numbers
    cleaned = re.sub(r'[A-Z]{3}$', '', cleaned)  # Remove country codes at end
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()  # Clean whitespace
    
    # Extract main merchant name (first part before location)
    parts = cleaned.split()
    if len(parts) > 0:
        # Take first few words as merchant name, skip location codes
        merchant_parts = []
        for part in parts[:4]:  # Take first 4 words max
            if not re.match(r'^[A-Z]{2,3}$', part):  # Skip country/city codes
                merchant_parts.append(part)
        return ' '.join(merchant_parts) if merchant_parts else cleaned
    
    return cleaned

def extract_card_info(description):
    """Extract card information from description"""
    card_match = re.search(r'\*\*\*\*(\d{4})', description)
    if card_match:
        return f"****{card_match.group(1)}"
    return ""

def determine_payment_option(reason, description):
    """Determine payment option based on reason and description"""
    if "PAGAMENTO TRAMITE POS" in reason:
        return "Card"
    elif "PRELIEVO" in reason:
        return "Cash"
    elif any(term in reason for term in ["DISPOSIZIONE DI PAGAMENTO", "GIROCONTO/BONIFICO", "ACCREDITO EMOLUMENTI"]):
        return "Bank Transfer"
    elif "VERSAMENTO CONTANTE" in reason:
        return "Cash"
    else:
        return "Other"

def process_csv_data(df):
    """Process CSV data into expenses and income DataFrames"""
    
    # Convert transaction date to datetime
    df['Txn. Date'] = pd.to_datetime(df['Txn. Date'], format='%d/%m/%Y')
    
    # Separate expenses and income
    expenses_data = df[df['Clean_Amount'] < 0].copy()
    income_data = df[df['Clean_Amount'] > 0].copy()
    
    # Process expenses
    expenses_list = []
    for _, row in expenses_data.iterrows():
        merchant_name = clean_merchant_name(row['Description'])
        card_info = extract_card_info(row['Description'])
        payment_option = determine_payment_option(row['Reason'], row['Description'])
        
        expense_record = {
            "Date": row['Txn. Date'].strftime('%d-%m-%Y'),  # Format as dd-MM-YYYY
            "Amount": abs(row['Clean_Amount']),  # Make positive for expenses
            "Store": merchant_name,
            "Category": row['Category'],
            "Payment Option": payment_option,
            "Card": card_info if payment_option == "Card" else ""
        }
        expenses_list.append(expense_record)
    
    # Process income
    income_list = []
    for _, row in income_data.iterrows():
        source_name = clean_merchant_name(row['Description'])
        payment_option = determine_payment_option(row['Reason'], row['Description'])
        
        income_record = {
            "Date": row['Txn. Date'].strftime('%d-%m-%Y'),  # Format as dd-MM-YYYY
            "Amount": row['Clean_Amount'],  # Keep positive for income
            "Source": source_name,
            "Payment Option": payment_option
        }
        income_list.append(income_record)
    
    # Create DataFrames
    expenses_df = pd.DataFrame(expenses_list)
    income_df = pd.DataFrame(income_list)
    
    return expenses_df, income_df

def main():
    st.title("📤 Upload CSV Data to Google Sheets")
    
    # Check if authentication is configured
    try:
        is_logged_in = st.user.is_logged_in
    except (AttributeError, KeyError):
        # Authentication not configured, run in demo mode
        is_logged_in = True
    
    if not is_logged_in:
        st.warning("Please log in from the main page to upload data.")
        return
    
    st.markdown("""
    This page allows you to upload your processed bank transaction CSV file to Google Sheets.
    The data will be automatically categorized and split into expenses and income.
    """)
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload your processed CSV file", 
        type=['csv'],
        help="Upload the CSV file that contains the Clean_Amount and Category columns"
    )
    
    if uploaded_file is not None:
        try:
            # Read the uploaded CSV file
            df = pd.read_csv(uploaded_file, sep=';')
            
            # Validate required columns
            required_columns = ['Txn. Date', 'Description', 'Reason', 'Clean_Amount', 'Category']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"Missing required columns: {missing_columns}")
                st.info("Please make sure your CSV file has been processed with Clean_Amount and Category columns.")
                return
            
            # Display file info
            st.success(f"✅ File uploaded successfully! Found {len(df)} transactions.")
            
            # Process the data
            with st.spinner("Processing transaction data..."):
                expenses_df, income_df = process_csv_data(df)
            
            # Display summary
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📊 Expenses Found", len(expenses_df))
            with col2:
                st.metric("💰 Income Found", len(income_df))
            
            # Show preview of processed data
            st.subheader("📊 Expenses Preview")
            if not expenses_df.empty:
                st.dataframe(expenses_df.head(10))
            else:
                st.info("No expense transactions found.")
            
            st.subheader("💰 Income Preview")
            if not income_df.empty:
                st.dataframe(income_df.head(10))
            else:
                st.info("No income transactions found.")
            
            # Upload to Google Sheets
            st.subheader("📤 Upload to Google Sheets")
            
            col1, col2 = st.columns(2)
            with col1:
                upload_expenses = st.checkbox("Upload Expenses", value=True)
            with col2:
                upload_income = st.checkbox("Upload Income", value=True)
            
            if st.button("🚀 Upload to Google Sheets", type="primary"):
                try:
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    
                    success_count = 0
                    
                    # Upload expenses
                    if upload_expenses and not expenses_df.empty:
                        with st.spinner("Uploading expenses..."):
                            try:
                                # Try to read existing expenses data
                                existing_expenses = conn.read(worksheet="expenses_taras", ttl=0)
                                
                                # Append new data to existing
                                updated_expenses = pd.concat([existing_expenses, expenses_df], ignore_index=True)
                                
                                # Remove duplicates based on Date, Amount, and Store
                                updated_expenses = updated_expenses.drop_duplicates(
                                    subset=['Date', 'Amount', 'Store'], keep='last'
                                )
                                
                                conn.update(worksheet="expenses_taras", data=updated_expenses)
                                st.success(f"✅ Successfully uploaded {len(expenses_df)} expenses!")
                                success_count += 1
                                
                            except Exception as e:
                                if "WorksheetNotFound" in str(e):
                                    # Create new worksheet if it doesn't exist
                                    conn.update(worksheet="expenses_taras", data=expenses_df)
                                    st.success(f"✅ Created new expenses worksheet and uploaded {len(expenses_df)} transactions!")
                                    success_count += 1
                                else:
                                    st.error(f"❌ Error uploading expenses: {e}")
                    
                    # Upload income
                    if upload_income and not income_df.empty:
                        with st.spinner("Uploading income..."):
                            try:
                                # Try to read existing income data
                                existing_income = conn.read(worksheet="income_taras", ttl=0)
                                
                                # Append new data to existing
                                updated_income = pd.concat([existing_income, income_df], ignore_index=True)
                                
                                # Remove duplicates based on Date, Amount, and Source
                                updated_income = updated_income.drop_duplicates(
                                    subset=['Date', 'Amount', 'Source'], keep='last'
                                )
                                
                                conn.update(worksheet="income_taras", data=updated_income)
                                st.success(f"✅ Successfully uploaded {len(income_df)} income transactions!")
                                success_count += 1
                                
                            except Exception as e:
                                if "WorksheetNotFound" in str(e):
                                    # Create new worksheet if it doesn't exist
                                    conn.update(worksheet="income_taras", data=income_df)
                                    st.success(f"✅ Created new income worksheet and uploaded {len(income_df)} transactions!")
                                    success_count += 1
                                else:
                                    st.error(f"❌ Error uploading income: {e}")
                    
                    if success_count > 0:
                        st.balloons()
                        st.success("🎉 Upload completed! You can now view your data in the Dashboard.")
                        
                except Exception as e:
                    st.error(f"❌ Failed to connect to Google Sheets: {e}")
                    st.info("Please make sure your Google Sheets connection is properly configured.")
            
        except Exception as e:
            st.error(f"Error reading CSV file: {e}")
            st.info("Please make sure your CSV file is properly formatted with semicolon separators.")
    
    else:
        st.info("👆 Please upload a CSV file to get started.")
        
        # Show example of expected format
        st.subheader("📋 Expected CSV Format")
        st.markdown("""
        Your CSV file should have these columns:
        - `Txn. Date` - Transaction date (DD/MM/YYYY format)
        - `Description` - Transaction description
        - `Reason` - Transaction reason/type
        - `Clean_Amount` - Numerical amount (negative for expenses, positive for income)
        - `Category` - Transaction category
        """)

if __name__ == "__main__":
    main() 