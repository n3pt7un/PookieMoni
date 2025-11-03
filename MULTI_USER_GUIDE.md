# Multi-User Finance Tracker Guide

## Overview

Your Personal Finance Tracker has been completely overhauled with a modern Copilot Money-inspired design and comprehensive multi-user support. This guide explains all the new features and how to use them.

## 🆕 What's New

### 1. **Multi-User Support**

The app now supports three spending "channels":

- **User 1 (Taras)**: Personal expenses, income, budgets, and recurring payments
- **User 2 (Dana)**: Personal expenses, income, budgets, and recurring payments  
- **Shared**: Joint expenses, income, and budgets visible to both users

#### Key Features:
- Each user can see their personal data + shared data
- Users cannot see each other's personal data
- Easy user switching via the sidebar
- All transactions can be marked as "Personal" or "Shared"

### 2. **Modern Dashboard** 📈

The dashboard has been completely redesigned with:

#### Top Metrics Cards
- **Budget**: Shows remaining budget with color-coded status
  - 🟢 Green: Under 80% of budget (on track)
  - 🟡 Yellow: 80-100% of budget (warning)
  - 🔴 Red: Over budget (alert)
- **Spending**: Total spending with trend vs. last month
- **Recurrings**: Monthly recurring payments overview
- **Net Income**: Income minus expenses for current month

#### Spending Breakdown
- Visual category breakdown with progress bars
- Budget vs. actual spending comparison
- Trend indicators (↑/↓) showing changes from previous month
- Top 5 categories pie chart
- Color-coded status per category

#### Spending Trend Chart
- 6-month spending history visualization
- Budget threshold line (if configured)
- Interactive line chart with hover details

#### Recurring Payments Section
- Active subscriptions list
- Due date tracking with color coding:
  - 🔴 Overdue
  - 🟡 Due within 3 days
  - 🟢 Due later
- Monthly total and subscription count

#### Transaction Rules Display
- Shows configured auto-categorization rules
- Keywords that trigger automatic category assignment

#### Recent Transactions
- Last 10 transactions with details
- Personal/Shared badges
- Sorted by most recent

### 3. **Recurring Expenses Management** 🔄

New dedicated page for managing subscriptions and recurring payments:

#### Features:
- **View All**: See all recurring expenses with status
- **Add New**: Create new recurring expenses with:
  - Name, amount, category
  - Frequency (Daily, Weekly, Bi-weekly, Monthly, Quarterly, Yearly)
  - Next due date
  - Status (Active, Paused, Cancelled)
  - Notes
- **Analysis**: 
  - Spending by category
  - Spending by frequency
  - Upcoming expenses (next 30 days)
  - Yearly cost estimates

#### Metrics:
- Total monthly recurring costs
- Active subscription count
- Items due this week
- Estimated yearly cost

### 4. **Enhanced Transaction Entry**

The main page now includes:
- User-aware transaction entry
- Personal/Shared toggle for users (Taras & Dana)
- Auto-categorization based on store names
- Budget alerts after adding expenses
- Recent transactions filtered by user

### 5. **User Interface Improvements**

#### Visual Design:
- Dark theme with gradient backgrounds
- Smooth hover effects on cards
- Color-coded budget indicators
- Modern typography and spacing
- Responsive layout

#### User Experience:
- Easy user switching in sidebar
- Clear visual indicators for personal vs. shared data
- Real-time budget status updates
- Intuitive navigation

## 📋 Configuration

### Google Sheets Setup

Your app now uses separate worksheets for each user:

```toml
[connections.gsheets.worksheets]
# User 1 (Taras)
expenses_user1 = "expenses_taras"
income_user1 = "income_taras"
recurrings_user1 = "recurrings_taras"
investments_user1 = "investments_taras"

# User 2 (Dana)
expenses_user2 = "expenses_dana"
income_user2 = "income_dana"
recurrings_user2 = "recurrings_dana"
investments_user2 = "investments_dana"

# Shared
expenses_shared = "expenses_shared"
income_shared = "income_shared"
recurrings_shared = "recurrings_shared"
investments_shared = "investments_shared"
```

### Required Worksheets

Create these worksheets in your Google Sheets:

#### For Taras:
- `expenses_taras`
- `income_taras`
- `recurrings_taras`

#### For Dana:
- `expenses_dana`
- `income_dana`
- `recurrings_dana`

#### For Shared:
- `expenses_shared`
- `income_shared`
- `recurrings_shared`

### Worksheet Columns

#### Expenses
- Date
- Amount
- Store
- Category
- Payment Option
- Card

#### Income
- Date
- Amount
- Source
- Payment Option

#### Recurrings
- Name
- Amount
- Category
- Frequency
- Next_Due
- Status
- Notes
- Added_Date

## 🎯 Usage Guide

### Switching Users

1. Look at the sidebar
2. Under "👤 Active User", select:
   - **Taras**: See personal + shared data
   - **Dana**: See personal + shared data
   - **Shared**: See only shared data

### Adding Transactions

1. Go to the main page (💰 Personal Finance Tracker)
2. Select your active user in the sidebar
3. Choose "Personal" or "Shared" for the transaction
4. Select "Expense" or "Income"
5. Fill in the details
6. Submit

**Tips:**
- Personal transactions are only visible to you
- Shared transactions are visible to both users
- Budget alerts appear automatically for expenses

### Managing Recurring Expenses

1. Go to 🔄 Recurrings page
2. Select your user
3. Use tabs:
   - **View All**: See and manage existing recurrings
   - **Add New**: Create new recurring expense
   - **Analysis**: View spending patterns

### Viewing Dashboard

1. Go to 📈 Dashboard
2. Select your user
3. View:
   - Budget status at a glance
   - Spending breakdown by category
   - 6-month spending trend
   - Recurring payments status
   - Recent transactions

### Managing Settings

Settings page remains the same but now works with the multi-user system:
- Categories apply to all users
- Budgets can be set per category
- Auto-categorization rules apply to all users

## 🎨 Design Features

### Color Coding

- **Green (🟢)**: On track, healthy spending
- **Yellow (🟡)**: Warning, approaching limit
- **Red (🔴)**: Alert, over budget or overdue
- **Blue (🔵)**: Neutral, informational

### Badges

- **👤 Personal**: Personal transaction/data
- **🤝 Shared**: Shared transaction/data
- **↑**: Spending increased vs. previous period
- **↓**: Spending decreased vs. previous period
- **=**: Spending remained stable

### Status Indicators

Recurring expenses:
- **🔴 Overdue**: Past due date
- **🟡 Due soon**: Due within 3 days
- **🟢 On schedule**: Due in 4+ days
- **⚪ No date**: No due date set

## 📊 Data Privacy

- Each user's personal data is completely separate
- Users can only see their own personal data + shared data
- Shared data is visible to both users
- No user can see the other user's personal transactions

## 🔧 Technical Details

### New Files Created

1. **user_utils.py**: Multi-user management utilities
2. **pages/4_🔄_Recurrings.py**: Recurring expenses page

### Modified Files

1. **app.py**: Added multi-user support
2. **pages/1_📈_Dashboard.py**: Complete redesign
3. **.streamlit/secrets.toml**: Added user-specific worksheet names

### Key Functions

- `get_current_user()`: Get active user
- `set_current_user(user_id)`: Switch user
- `get_user_and_shared_data()`: Combine personal + shared data
- `get_worksheet_names(user_id)`: Get worksheet names for user
- `render_user_selector()`: Display user switcher UI

## 💡 Tips for Best Experience

1. **Set up budgets** in Settings for automatic tracking
2. **Add recurring expenses** to track subscriptions
3. **Use categories consistently** for better insights
4. **Switch users** to see different perspectives
5. **Mark transactions** as Personal or Shared appropriately
6. **Check dashboard regularly** for spending insights

## 🚀 Future Enhancements

Potential features to add:
- Investment tracking (worksheets ready)
- Transaction search and filters
- Custom date ranges on dashboard
- Export reports
- Mobile-responsive improvements
- Notification system for due payments

## ❓ Troubleshooting

### User selector not appearing
- Make sure you're on a page that has been updated
- Refresh the page
- Check that secrets.toml has user configuration

### Worksheets not found
- Create the required worksheets in Google Sheets
- Ensure worksheet names match secrets.toml exactly
- Check Google Sheets connection

### Data not showing
- Verify correct user is selected
- Check that data exists in the correct worksheet
- Ensure date formats are consistent (dd-MM-YYYY)

### Budget alerts not working
- Set up budgets in Settings first
- Ensure categories match between transactions and budgets
- Check budget period settings

## 📞 Support

For issues or questions:
1. Check this guide first
2. Review IMPLEMENTATION_SUMMARY.md for technical details
3. Check developer_guide.md for development info

---

**Enjoy your new multi-user finance tracking experience! 🎉**

