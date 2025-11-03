# PookieMoni - Code Analysis & Feature Implementation Plan

## Executive Summary

The PookieMoni application is a well-structured Personal Finance Tracker built with Streamlit. The codebase is in good working condition with no critical errors. The application successfully runs and enforces authentication properly. This document provides a comprehensive analysis and detailed implementation plan for the two requested features.

---

## 1. Current State Analysis

### 1.1 Application Architecture

**Technology Stack:**
- **Frontend/Backend:** Streamlit (v1.51.0)
- **Data Storage:** Google Sheets (via st-gsheets-connection)
- **Authentication:** Streamlit built-in authentication features
- **Configuration:** TOML file for categories and stores
- **Data Visualization:** Plotly

**Application Structure:**
```
PookieMoni/
├── app.py                          # Main page (transaction entry)
├── config_utils.py                 # Configuration management system
├── config.toml                     # Categories, stores, keywords config
├── pages/
│   ├── 1_📈_Dashboard.py          # Financial analytics dashboard
│   ├── 2_📤_Upload_CSV.py         # CSV import functionality
│   └── 3_⚙️_Settings.py           # Configuration interface
├── requirements.txt                # Python dependencies
└── pyproject.toml                  # Poetry configuration
```

### 1.2 Current Features

✅ **Working Features:**
1. **Authentication System**
   - Google OAuth integration via Streamlit
   - Proper authentication checks on all pages
   - Session management

2. **Transaction Management**
   - Manual expense/income entry
   - CSV bulk import from bank statements
   - Auto-categorization based on store names and keywords

3. **Dashboard & Analytics**
   - Key metrics (Total Income, Total Expenses, Net Savings)
   - Date range filtering
   - Multiple visualizations:
     - Expenses by category (pie chart)
     - Expense breakdown (treemap)
     - Monthly expenses (bar chart)
     - Income vs. Expenses comparison

4. **Configuration System**
   - Category management (add, remove, rename)
   - Store management per category
   - Keyword-based auto-categorization
   - Settings interface with tabs

5. **CSV Import**
   - Italian bank statement processing
   - Automatic merchant name cleaning
   - Duplicate detection
   - Payment method detection

### 1.3 Code Quality Assessment

**Strengths:**
✅ Clean, modular code structure
✅ Well-documented functions with docstrings
✅ No linter errors
✅ Proper separation of concerns
✅ Good error handling patterns
✅ Type hints in config_utils.py

**Minor Issues Identified:**

1. **Dependency Management Inconsistency**
   - `requirements.txt` contains full dependencies
   - `pyproject.toml` is incomplete (minimal dependencies)
   - **Impact:** Low - doesn't affect functionality
   - **Recommendation:** Synchronize dependencies or choose one approach

2. **Authentication Configuration**
   - Uses Streamlit's `st.user` API (requires proper OAuth setup)
   - Currently will not work without Google OAuth credentials
   - **Impact:** Medium - app runs but login won't work without setup
   - **Recommendation:** Add `.streamlit/secrets.toml` documentation

3. **Hard-coded Worksheet Names**
   - "expenses_taras" and "income_taras" are hard-coded
   - **Impact:** Low - works for single user
   - **Recommendation:** Consider making configurable per user

**No Critical Issues Found:** The application is stable and functional.

---

## 2. Feature Implementation Plan

### Feature 1: Initial Account Balance Management

#### 2.1.1 Objectives
Allow users to set an initial account balance at any moment from the settings menu, enabling accurate net worth tracking and financial overview.

#### 2.1.2 User Stories
- As a user, I want to set my initial account balance to reflect my starting financial position
- As a user, I want to update my initial balance if I made an error or want to reset it
- As a user, I want to see my current balance calculated from the initial balance plus all transactions

#### 2.1.3 Technical Design

**Database Schema Changes:**
```python
# New worksheet: "account_balance_taras"
Columns:
- Date (dd-MM-YYYY)        # When the balance was set
- Balance (float)          # The balance amount
- Notes (string)           # Optional user notes
```

**Configuration Changes:**
```toml
# Addition to config.toml
[account_settings]
initial_balance = 0.0
initial_balance_date = ""
currency = "EUR"
```

**Code Changes Required:**

1. **config_utils.py** - Add balance management functions:
```python
def get_initial_balance() -> float
def set_initial_balance(amount: float, date: str, notes: str = "") -> bool
def get_balance_history() -> List[Dict]
```

2. **pages/3_⚙️_Settings.py** - Add new tab "💰 Account Balance":
```python
def account_balance_management():
    - Display current initial balance
    - Form to set/update initial balance
    - Display balance history
    - Validation for positive/negative balances
```

3. **pages/1_📈_Dashboard.py** - Update metrics calculation:
```python
# Modify Key Metrics section to include:
- Initial Balance
- Current Balance = Initial Balance + Total Income - Total Expenses
- Add visual indicator (progress bar or gauge)
```

4. **app.py** - Update sidebar info:
```python
# Add quick balance overview to sidebar
st.sidebar.metric("Current Balance", f"€{current_balance:,.2f}")
```

#### 2.1.4 Implementation Steps

**Phase 1: Backend (config_utils.py)**
1. Add balance configuration to TOML structure
2. Implement `get_initial_balance()` function
3. Implement `set_initial_balance()` function
4. Implement `get_balance_history()` function
5. Add unit tests for balance functions

**Phase 2: Settings Page**
1. Create new tab "💰 Account Balance"
2. Add form for setting initial balance
   - Date picker (default to today)
   - Number input for amount
   - Text area for optional notes
   - Submit button
3. Display current balance settings
4. Add balance history table
5. Add validation and error handling

**Phase 3: Dashboard Integration**
1. Read initial balance from config
2. Calculate current balance
3. Update Key Metrics section with 4 metrics:
   - Initial Balance
   - Total Income
   - Total Expenses
   - **Current Balance** (new, highlighted)
4. Add visual progress indicator
5. Ensure date filtering doesn't affect initial balance

**Phase 4: Google Sheets Integration**
1. Create "account_balance_taras" worksheet if not exists
2. Implement worksheet update logic
3. Add duplicate prevention
4. Test Google Sheets connection

**Phase 5: Testing**
1. Test setting initial balance
2. Test updating initial balance
3. Test balance calculations with various transaction combinations
4. Test with empty transaction history
5. Test date filtering doesn't break balance calculation

#### 2.1.5 UI Mockup

**Settings Page - New Tab:**
```
💰 Account Balance
─────────────────────────────────────────
Current Account Settings
┌─────────────────────────────────────┐
│ Initial Balance: €1,000.00          │
│ Set On: 01-11-2025                  │
└─────────────────────────────────────┘

Set/Update Initial Balance
┌─────────────────────────────────────┐
│ Date: [01-11-2025        ]          │
│ Amount: [___________] EUR           │
│ Notes: [________________________]   │
│                                     │
│ [Update Balance]                    │
└─────────────────────────────────────┘

Balance History
┌─────────────────────────────────────┐
│ Date       │ Balance  │ Notes       │
├────────────┼──────────┼─────────────┤
│ 01-11-2025 │ €1000.00 │ Initial set │
└─────────────────────────────────────┘
```

**Dashboard - Updated Metrics:**
```
Key Metrics
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│ Initial Balance │ Total Income    │ Total Expenses  │ Current Balance │
│   €1,000.00     │   €2,500.00     │   €1,800.00     │   €1,700.00     │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘
                    ╚═══════════════════════════════╝ (+€700.00 / +70%)
```

---

### Feature 2: Budget Planning by Category

#### 2.2.1 Objectives
Enable users to plan monthly/weekly budgets per category and track spending progress in real-time, providing actionable insights for better financial management.

#### 2.2.2 User Stories
- As a user, I want to set monthly budget limits for each expense category
- As a user, I want to see how much of my budget I've used in real-time
- As a user, I want to receive visual warnings when approaching budget limits
- As a user, I want to see budget vs. actual spending comparisons
- As a user, I want to set both monthly and weekly budget periods

#### 2.2.3 Technical Design

**Database Schema Changes:**
```python
# New worksheet: "budgets_taras"
Columns:
- Category (string)          # Category name
- Period (string)            # "monthly" or "weekly"
- Amount (float)             # Budget amount
- Start_Date (dd-MM-YYYY)    # Budget period start
- End_Date (dd-MM-YYYY)      # Budget period end (optional, can be recurring)
- Is_Active (boolean)        # Whether budget is currently active
```

**Configuration Changes:**
```toml
# Addition to config.toml
[budget_settings]
default_period = "monthly"      # "monthly" or "weekly"
warning_threshold = 80          # % threshold for warnings
alert_threshold = 100           # % threshold for alerts
```

**Code Changes Required:**

1. **config_utils.py** - Add budget management functions:
```python
def get_budgets() -> Dict[str, Dict]
def set_budget(category: str, amount: float, period: str) -> bool
def update_budget(category: str, amount: float) -> bool
def delete_budget(category: str) -> bool
def get_budget_status(category: str, start_date: str, end_date: str) -> Dict
def calculate_budget_progress() -> Dict[str, Dict]
```

2. **pages/3_⚙️_Settings.py** - Add new tab "📊 Budget Planning":
```python
def budget_management():
    - List all categories with current budgets
    - Set/update budget per category
    - Choose budget period (monthly/weekly)
    - Set budget thresholds
    - Bulk budget setup option
```

3. **pages/1_📈_Dashboard.py** - Add budget section:
```python
def budget_overview():
    - Budget progress cards per category
    - Visual progress bars with color coding:
      * Green: < 80% used
      * Yellow: 80-100% used  
      * Red: > 100% used
    - Budget vs. Actual comparison chart
    - Month-to-date spending rate
    - Projected end-of-period total
```

4. **app.py** - Add budget alerts:
```python
# After transaction entry, show budget impact:
- "You've used 75% of your Food budget this month"
- "Warning: This transaction puts you at 95% of your Transport budget"
```

#### 2.2.4 Implementation Steps

**Phase 1: Backend Infrastructure**
1. Create budget data structure in config.toml
2. Implement budget CRUD functions in config_utils.py:
   - `get_budgets()`
   - `set_budget()`
   - `update_budget()`
   - `delete_budget()`
3. Implement budget calculation logic:
   - `get_budget_status()` - spending vs. budget for period
   - `calculate_budget_progress()` - all categories
   - `get_current_period_dates()` - calculate period start/end
4. Add budget validation functions
5. Write unit tests

**Phase 2: Settings Interface**
1. Create "📊 Budget Planning" tab in Settings
2. Implement budget list view:
   - Table showing all categories
   - Current budget amounts
   - Period (monthly/weekly)
   - Status (active/inactive)
3. Add budget setup form:
   - Category selector
   - Amount input (with currency)
   - Period selector (monthly/weekly)
   - Start date picker
   - Recurring checkbox
   - Submit button
4. Add bulk budget setup:
   - Quick setup for all categories
   - Template options (e.g., "Conservative", "Balanced", "Flexible")
5. Add budget threshold settings:
   - Warning threshold slider (default 80%)
   - Alert threshold slider (default 100%)
6. Implement edit/delete functionality

**Phase 3: Dashboard Budget Visualization**
1. Add "Budget Overview" section to Dashboard
2. Create budget progress cards:
   ```
   ┌─────────────────────────────┐
   │ 🍔 Food                     │
   │ €450 / €500 (90%)           │
   │ ████████████████████░░  90% │
   │ €50 remaining               │
   └─────────────────────────────┘
   ```
3. Implement color coding:
   - Green: spending < warning_threshold
   - Yellow: warning_threshold ≤ spending < alert_threshold
   - Red: spending ≥ alert_threshold
4. Add Budget vs. Actual bar chart (by category)
5. Add spending rate indicator:
   - "On track" / "Over pace" / "Under pace"
   - Projected month-end total
6. Create budget summary metrics:
   - Total budgeted
   - Total spent
   - Total remaining
   - % of budget used

**Phase 4: Transaction Integration**
1. Update app.py transaction entry:
   - After successful expense entry, calculate budget impact
   - Show inline budget alert if approaching/exceeding limit
   - Display remaining budget for selected category
2. Add budget context to transaction form:
   - Show current budget usage for selected category
   - Real-time update as amount is entered

**Phase 5: Google Sheets Integration**
1. Create "budgets_taras" worksheet
2. Implement sync logic for budget data
3. Add worksheet initialization
4. Test read/write operations

**Phase 6: Advanced Features**
1. Budget recommendations:
   - Analyze historical spending
   - Suggest realistic budget amounts
2. Budget alerts system:
   - Daily/weekly email summaries (if email configured)
   - In-app notifications
3. Budget reports:
   - Monthly budget performance report
   - Category-wise budget adherence trends
   - Export budget data

**Phase 7: Testing**
1. Unit tests for budget calculations
2. Test budget creation/update/delete
3. Test budget progress calculations with various scenarios
4. Test date period calculations (monthly/weekly)
5. Test edge cases:
   - No budgets set
   - Budget set but no transactions
   - Overspending scenarios
   - Multiple budget periods
6. Integration testing with dashboard
7. UI/UX testing for responsiveness

#### 2.2.5 UI Mockups

**Settings Page - Budget Planning Tab:**
```
📊 Budget Planning
─────────────────────────────────────────────────────────────

Current Budgets
┌─────────────────────────────────────────────────────────┐
│ Category   │ Period   │ Budget    │ Spent     │ Status  │
├────────────┼──────────┼───────────┼───────────┼─────────┤
│ Food       │ Monthly  │ €500.00   │ €450.00   │ 🟡 90%  │
│ Transport  │ Monthly  │ €200.00   │ €180.00   │ 🟢 90%  │
│ Shopping   │ Monthly  │ €300.00   │ €350.00   │ 🔴 117% │
│ Bills      │ Monthly  │ €400.00   │ €0.00     │ 🟢 0%   │
└─────────────────────────────────────────────────────────┘

Set Budget for Category
┌─────────────────────────────────────────────────────────┐
│ Category: [Food              ▼]                         │
│ Amount: [500] EUR                                       │
│ Period: ○ Monthly  ○ Weekly                             │
│ Start Date: [01-11-2025     ]                           │
│ ☑ Recurring (auto-renew each period)                    │
│                                                         │
│ [Set Budget]  [Clear]                                   │
└─────────────────────────────────────────────────────────┘

Budget Alert Settings
┌─────────────────────────────────────────────────────────┐
│ Warning Threshold: [████████░░] 80%                     │
│ Alert Threshold:   [██████████] 100%                    │
│                                                         │
│ [Save Settings]                                         │
└─────────────────────────────────────────────────────────┘

Quick Setup
┌─────────────────────────────────────────────────────────┐
│ [Conservative Budget] [Balanced Budget] [Flexible Budget]
│                                                         │
│ Conservative: Tight budget limits based on essential    │
│ spending only.                                          │
└─────────────────────────────────────────────────────────┘
```

**Dashboard - Budget Overview Section:**
```
📊 Budget Overview (November 2025)
─────────────────────────────────────────────────────────────

Overall Budget Status
┌──────────────────┬──────────────────┬──────────────────┐
│ Total Budgeted   │ Total Spent      │ Remaining        │
│    €1,400.00     │    €980.00       │    €420.00       │
└──────────────────┴──────────────────┴──────────────────┘
         ████████████████░░░░░░  70% used (On track 🟢)

Category Budgets
┌────────────────────────────────┬────────────────────────────────┐
│ 🍔 Food                        │ 🚗 Transport                   │
│ €450 / €500 (90%)              │ €180 / €200 (90%)              │
│ ████████████████████░░  90% 🟡 │ ████████████████████░░  90% 🟢 │
│ €50 remaining                  │ €20 remaining                  │
│ Pace: On track                 │ Pace: On track                 │
└────────────────────────────────┴────────────────────────────────┘

┌────────────────────────────────┬────────────────────────────────┐
│ 🛍️ Shopping                    │ 📄 Bills                       │
│ €350 / €300 (117%)             │ €0 / €400 (0%)                 │
│ ████████████████████████  117% 🔴 €0░░░░░░░░░░░░░░░░░░░░░░  0% 🟢 │
│ ⚠️ €50 over budget!            │ €400 remaining                 │
│ Pace: Over                     │ Pace: Under                    │
└────────────────────────────────┴────────────────────────────────┘

[Budget vs. Actual Chart]
     Budgeted    Actual
Food    ████████  ███████░
Transport ████    ███░
Shopping  ██████  ████████
Bills     ████████

Spending Rate Analysis
┌─────────────────────────────────────────────────────────────┐
│ Today is Day 10 of 30 (33% through month)                  │
│ You've spent 70% of your budget                            │
│ Status: ⚠️ Spending faster than expected                    │
│ Projected month-end total: €1,470.00 (5% over budget)      │
│                                                             │
│ 💡 Tip: Reduce Shopping spending to stay on budget         │
└─────────────────────────────────────────────────────────────┘
```

**Transaction Entry Page - Budget Alert:**
```
[After submitting €50 expense to "Food"]

✅ Expense added successfully!
ℹ️ Budget Impact: You've used €450 / €500 (90%) of your Food budget this month.
   €50 remaining. You're on track! 🟢
```

---

## 3. Implementation Timeline

### Phase Breakdown

**Week 1: Feature 1 - Account Balance**
- Days 1-2: Backend implementation (config_utils.py)
- Days 3-4: Settings page UI
- Day 5: Dashboard integration
- Days 6-7: Testing and refinement

**Week 2: Feature 2 - Budget Planning (Part 1)**
- Days 1-3: Backend infrastructure and budget calculations
- Days 4-7: Settings interface for budget management

**Week 3: Feature 2 - Budget Planning (Part 2)**
- Days 1-4: Dashboard budget visualization
- Days 5-7: Transaction integration and alerts

**Week 4: Integration, Testing & Polish**
- Days 1-2: Google Sheets integration for both features
- Days 3-5: Comprehensive testing
- Days 6-7: Bug fixes, documentation, and final polish

### Estimated Effort

| Task | Estimated Hours |
|------|----------------|
| **Feature 1: Account Balance** | |
| - Backend functions | 4 hours |
| - Settings UI | 6 hours |
| - Dashboard integration | 4 hours |
| - Testing | 4 hours |
| **Feature 1 Subtotal** | **18 hours** |
| | |
| **Feature 2: Budget Planning** | |
| - Backend infrastructure | 8 hours |
| - Budget calculations | 6 hours |
| - Settings UI | 10 hours |
| - Dashboard visualization | 12 hours |
| - Transaction integration | 6 hours |
| - Advanced features | 8 hours |
| - Testing | 8 hours |
| **Feature 2 Subtotal** | **58 hours** |
| | |
| **Integration & Polish** | |
| - Google Sheets integration | 6 hours |
| - End-to-end testing | 6 hours |
| - Documentation | 4 hours |
| - Bug fixes & refinement | 6 hours |
| **Integration Subtotal** | **22 hours** |
| | |
| **TOTAL ESTIMATED TIME** | **98 hours** |

---

## 4. Technical Considerations

### 4.1 Data Storage Strategy

**Option 1: Continue with Google Sheets (Recommended)**
- ✅ Consistent with current architecture
- ✅ No additional infrastructure needed
- ✅ Easy data backup and sharing
- ⚠️ May have performance limitations with large datasets
- Implementation: Create new worksheets for balance and budget data

**Option 2: Hybrid Approach**
- Store transactional data in Google Sheets
- Store configuration (budgets, balance) in TOML
- ✅ Faster configuration access
- ✅ No API calls for config data
- ⚠️ Less portable, tied to local file system

**Recommendation:** Start with Google Sheets for consistency, migrate to hybrid if performance issues arise.

### 4.2 Date Period Calculations

**Monthly Budgets:**
- Start: First day of current month
- End: Last day of current month
- Handle different month lengths (28-31 days)

**Weekly Budgets:**
- Start: Monday of current week
- End: Sunday of current week
- ISO week numbering for consistency

**Implementation:**
```python
from datetime import datetime, timedelta
import calendar

def get_monthly_period(date: datetime = None):
    if date is None:
        date = datetime.now()
    start = date.replace(day=1)
    last_day = calendar.monthrange(date.year, date.month)[1]
    end = date.replace(day=last_day)
    return start, end

def get_weekly_period(date: datetime = None):
    if date is None:
        date = datetime.now()
    start = date - timedelta(days=date.weekday())  # Monday
    end = start + timedelta(days=6)  # Sunday
    return start, end
```

### 4.3 Performance Optimization

**Caching Strategy:**
- Cache budget calculations using Streamlit's `@st.cache_data`
- TTL of 60 seconds for real-time data
- Invalidate cache on transaction entry or budget update

**Query Optimization:**
- Minimize Google Sheets API calls
- Batch read operations when possible
- Use date filtering at query level, not in Python

### 4.4 Error Handling

**Google Sheets Connection:**
```python
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    data = conn.read(worksheet="expenses_taras", ttl=0)
except Exception as e:
    st.error(f"Failed to connect to Google Sheets: {e}")
    st.info("Please check your connection and try again.")
    return
```

**Budget Calculation:**
```python
try:
    budget_status = calculate_budget_progress(category, start_date, end_date)
except ValueError as e:
    st.warning(f"Budget calculation issue: {e}")
    budget_status = {"spent": 0, "budget": 0, "percentage": 0}
```

### 4.5 Data Validation

**Initial Balance:**
- Accept negative balances (debt starting point)
- Validate currency format
- Ensure date is not in future (with option to override)

**Budget Amounts:**
- Must be positive numbers
- Maximum limit: €1,000,000 (sanity check)
- Warning if budget is 0

### 4.6 Security Considerations

1. **Authentication:**
   - All pages already check `st.user.is_logged_in`
   - No additional security changes needed

2. **Data Access:**
   - User-specific worksheet names (e.g., "expenses_taras")
   - Consider adding user ID prefix in future for multi-user support

3. **Input Validation:**
   - Sanitize all user inputs
   - Prevent SQL injection (not applicable with Google Sheets)
   - Validate date formats

---

## 5. Testing Strategy

### 5.1 Unit Tests

**Test config_utils.py functions:**
```python
def test_set_initial_balance():
    assert set_initial_balance(1000.0, "01-11-2025") == True
    assert get_initial_balance() == 1000.0

def test_budget_calculations():
    set_budget("Food", 500.0, "monthly")
    # Add test expenses
    status = get_budget_status("Food", start_date, end_date)
    assert status["percentage"] == 90.0

def test_period_calculations():
    start, end = get_monthly_period()
    assert start.day == 1
    assert end.month == start.month
```

### 5.2 Integration Tests

1. **Balance Feature:**
   - Set initial balance → verify on dashboard
   - Add transactions → verify balance updates correctly
   - Update initial balance → verify recalculation

2. **Budget Feature:**
   - Set budget → verify in settings and dashboard
   - Add expense → verify budget progress updates
   - Exceed budget → verify alert appears
   - Delete budget → verify removal from dashboard

### 5.3 UI/UX Testing

1. **Responsive Design:**
   - Test on different screen sizes
   - Verify mobile compatibility

2. **User Flow:**
   - Complete end-to-end transaction entry with budget alert
   - Set up all budgets via bulk setup
   - Navigate between pages ensuring data consistency

3. **Edge Cases:**
   - No transactions but budgets set
   - No budgets but transactions exist
   - Initial balance = 0
   - Negative initial balance
   - Budget amount = 0

### 5.4 Performance Testing

1. **Large Dataset:**
   - 1000+ transactions
   - Measure dashboard load time
   - Target: < 3 seconds for initial load

2. **API Calls:**
   - Count Google Sheets API calls per page load
   - Optimize to < 5 calls per dashboard render

---

## 6. Documentation Requirements

### 6.1 User Documentation

Create/Update:
1. **README.md** - Add new feature descriptions
2. **User Guide** - Step-by-step instructions for:
   - Setting initial balance
   - Creating budgets
   - Understanding budget alerts
   - Reading budget progress indicators

### 6.2 Developer Documentation

Create:
1. **docs/FEATURES.md** - Detailed feature specifications
2. **docs/API.md** - config_utils.py function reference
3. **docs/DATA_SCHEMA.md** - Google Sheets worksheets structure
4. Update **docs/developer_guide.md** with new functions

### 6.3 Code Comments

- Add docstrings to all new functions
- Inline comments for complex logic
- Type hints for all function parameters

---

## 7. Post-Implementation Enhancements

### 7.1 Future Feature Ideas

1. **Budget Analytics:**
   - Budget adherence trends over time
   - Category spending patterns
   - Month-over-month comparisons

2. **Smart Budgeting:**
   - AI-powered budget recommendations based on historical data
   - Automatic budget adjustment suggestions
   - Seasonal budget variations

3. **Advanced Balance Features:**
   - Multiple account tracking (checking, savings, credit cards)
   - Net worth tracking with assets/liabilities
   - Account balance synchronization with banks

4. **Alerts & Notifications:**
   - Email/SMS alerts for budget thresholds
   - Daily spending summaries
   - Weekly budget reports

5. **Goals & Savings:**
   - Savings goals with progress tracking
   - Debt payoff calculator
   - Emergency fund tracker

6. **Data Export:**
   - Export budgets to PDF/Excel
   - Annual budget summary reports
   - Tax preparation export

### 7.2 Scalability Improvements

1. **Database Migration:**
   - Consider PostgreSQL or MongoDB for larger datasets
   - Maintain Google Sheets as backup/sync option

2. **Caching Layer:**
   - Redis for frequently accessed data
   - Reduce API calls significantly

3. **Multi-User Support:**
   - User management system
   - Shared budgets for families/teams
   - Permission levels

---

## 8. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Google Sheets API rate limits | Medium | High | Implement caching, batch operations |
| Complex budget calculations slow dashboard | Medium | Medium | Optimize queries, add loading indicators |
| User confusion with budget setup | Low | Medium | Comprehensive UI/UX, tooltips, help text |
| Data inconsistency between features | Low | High | Thorough testing, transaction atomicity |
| Initial balance updates affect historical data | Low | High | Clear warnings, confirmation dialogs |

---

## 9. Success Criteria

### Feature 1: Account Balance
✅ User can set initial balance from settings
✅ Dashboard shows current balance accurately
✅ Balance calculation includes all transactions
✅ Balance history is maintained
✅ Updates are persisted to Google Sheets

### Feature 2: Budget Planning
✅ User can set budgets for all categories
✅ Dashboard shows budget progress for each category
✅ Visual indicators (green/yellow/red) work correctly
✅ Budget alerts appear on transaction entry
✅ Budget vs. Actual comparison is accurate
✅ Monthly and weekly periods calculate correctly
✅ Spending rate projections are displayed

### Overall
✅ No breaking changes to existing functionality
✅ All tests pass
✅ Documentation is complete
✅ Performance targets met (< 3s dashboard load)
✅ Code review approved
✅ User acceptance testing passed

---

## 10. Conclusion

The PookieMoni application is well-architected and ready for the addition of these two significant features. The implementation plan is structured to minimize risk while delivering high-value functionality. 

**Recommended Approach:**
1. Implement Feature 1 (Account Balance) first as it's simpler and provides immediate value
2. Thoroughly test Feature 1 before starting Feature 2
3. Implement Feature 2 (Budget Planning) in phases as outlined
4. Conduct comprehensive integration testing
5. Gather user feedback and iterate

**Key Success Factors:**
- Maintain code quality standards
- Thorough testing at each phase
- Clear user interface design
- Comprehensive documentation
- Performance optimization from the start

The estimated timeline of 4 weeks (98 hours) is realistic for a single developer working full-time. With proper execution, these features will significantly enhance the value proposition of PookieMoni and provide users with powerful tools for financial management.

---

## Appendix: Quick Reference

### Key Files to Modify

**Feature 1:**
- `config_utils.py` - Balance functions
- `pages/3_⚙️_Settings.py` - Balance tab
- `pages/1_📈_Dashboard.py` - Balance metrics
- `app.py` - Sidebar balance display
- `config.toml` - Balance configuration

**Feature 2:**
- `config_utils.py` - Budget functions
- `pages/3_⚙️_Settings.py` - Budget tab
- `pages/1_📈_Dashboard.py` - Budget overview section
- `app.py` - Budget alerts on transaction entry
- `config.toml` - Budget configuration

### New Google Sheets Worksheets
1. `account_balance_taras` - Balance history
2. `budgets_taras` - Budget configurations

### Configuration Additions
```toml
[account_settings]
initial_balance = 0.0
initial_balance_date = ""
currency = "EUR"

[budget_settings]
default_period = "monthly"
warning_threshold = 80
alert_threshold = 100
```

---

**Document Version:** 1.0  
**Date:** November 3, 2025  
**Status:** Ready for Approval

