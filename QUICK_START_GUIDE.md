# Quick Start Guide - New Features

## 🎉 Welcome to Enhanced PookieMoni!

Your Personal Finance Tracker now has two powerful new features:
1. **Account Balance Management** 💰
2. **Budget Planning** 📊

---

## 🚀 Getting Started in 5 Minutes

### Step 1: Set Your Initial Balance (2 minutes)

1. **Run the app**: `streamlit run app.py`
2. **Log in** with Google
3. Go to **⚙️ Settings** (sidebar)
4. Click the **💰 Account Balance** tab
5. Enter:
   - Your current account balance (e.g., €1,000)
   - Today's date
   - Optional note (e.g., "Starting balance")
6. Click **Update Balance**

✅ **Done!** Your balance is now tracked.

### Step 2: Set Up Your Budgets (3 minutes)

1. In **⚙️ Settings**, click the **📊 Budget Planning** tab
2. **Option A - Quick Setup** (fastest):
   - Expand "🚀 Set Budgets for All Categories"
   - Enter a default amount (e.g., €500)
   - Click **Apply to All Categories**
   
   **Option B - Custom Setup** (more control):
   - Select a category (e.g., "Food")
   - Enter budget amount (e.g., €400)
   - Choose period (monthly/weekly)
   - Click **Set Budget**
   - Repeat for other categories

✅ **Done!** Your budgets are active.

---

## 📱 Using the Features

### Viewing Your Balance

**On Every Page (Sidebar):**
- See your current balance at a glance
- Updated automatically with each transaction

**On Dashboard:**
- **Key Metrics** section shows:
  - Initial Balance
  - Total Income
  - Total Expenses
  - **Current Balance** (with change indicator)

### Tracking Your Budgets

**On Dashboard:**
- **Budget Overview** section shows:
  - Total budgeted vs. total spent
  - Individual category progress with color codes:
    - 🟢 Green: You're doing great! (< 80% used)
    - 🟡 Yellow: Watch out! (80-100% used)
    - 🔴 Red: Over budget! (> 100% used)
  - Budget vs. Actual chart
  - Spending rate analysis with projections

**When Adding Expenses:**
- After adding an expense, you'll see a budget alert:
  ```
  ℹ️ Budget Impact: You've used €450 / €500 (90%) of your Food budget.
  €50 remaining. You're on track! 🟢
  ```

### Adjusting Your Budgets

**In Settings → Budget Planning:**
- Update any budget amount
- Activate/deactivate budgets
- Change alert thresholds:
  - **Warning Threshold**: When to show yellow warning (default: 80%)
  - **Alert Threshold**: When to show red alert (default: 100%)

---

## 💡 Tips for Success

### Balance Management
1. **Set it once**: Enter your actual current balance when starting
2. **Update occasionally**: If you get external income/expenses (not tracked in app)
3. **Check regularly**: Glance at sidebar balance to stay aware

### Budget Planning
1. **Start realistic**: Don't set budgets too low initially
2. **Review monthly**: Adjust budgets based on actual spending patterns
3. **Use categories**: Take advantage of per-category budgets
4. **Pay attention to alerts**: Yellow/red alerts are your friends!

### Best Practices
- 📅 **Review weekly**: Check your dashboard every week
- 🎯 **Set goals**: Use budgets to achieve savings goals
- 📊 **Analyze trends**: Look at the spending rate analysis
- ✅ **Act on tips**: When you see budget tips, take action!

---

## 🎨 Understanding the Dashboard

### Key Metrics Section
```
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│ Initial Balance │ Total Income    │ Total Expenses  │ Current Balance │
│   €1,000.00     │   €2,500.00     │   €1,800.00     │   €1,700.00 ↑  │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```
- **Initial Balance**: Your starting point
- **Total Income**: All money in
- **Total Expenses**: All money out
- **Current Balance**: Where you are now (initial + income - expenses)

### Budget Overview Section
```
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│ Total Budgeted  │ Total Spent     │ Remaining       │ Status          │
│   €1,400.00     │   €980.00       │   €420.00       │ 🟢 On Track 70% │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

### Budget Progress Cards
```
🟢 Food                    🟡 Transport
██████████████░░ 90%       ████████████████████░ 95%
€450 / €500                €190 / €200
€50 remaining              €10 remaining
```

### Spending Rate Analysis
```
┌─────────────────────────────────────┐
│ Today is Day 10 of 30 (33% through) │
│ You've spent 70% of your budget     │
│ Status: ⚠️ Spending faster than expected │
│ Projected: €1,470 (€70 over budget) │
└─────────────────────────────────────┘
```

---

## 🆘 Troubleshooting

### "No budget alert showing after expense"
- Check if budget is set for that category (Settings → Budget Planning)
- Ensure budget is marked as "Active"
- Verify you're in the current budget period

### "Balance not updating in sidebar"
- Refresh the page
- Check if initial balance is set (Settings → Account Balance)
- Verify Google Sheets connection is working

### "Budget progress shows 0%"
- Make sure you have expenses in the current month
- Check that categories match between budgets and expenses
- Verify budget amount is greater than 0

---

## 📚 More Information

- **Full Analysis**: See `ANALYSIS_AND_PLAN.md` for detailed planning
- **Implementation Details**: See `IMPLEMENTATION_SUMMARY.md` for technical details
- **Settings**: Visit ⚙️ Settings page for all configuration options

---

## 🎯 Example Scenario

**Starting Out:**
1. Set initial balance: €1,000
2. Set monthly budgets:
   - Food: €400
   - Transport: €200
   - Shopping: €300
   - Bills: €500
   - Total: €1,400

**After 10 days:**
- Income: €2,000 (salary)
- Expenses: €600 (various)
- Current balance: €2,400 (€1,000 + €2,000 - €600)
- Budget used: 43% (spending slower than expected ✅)

**Dashboard shows:**
- Current Balance: €2,400 (+€1,400 since start)
- Budget: €600 / €1,400 spent
- Status: 🟢 On track
- Projected month-end: €1,380 (€20 under budget)

**Action:** Keep it up! You're doing great! 🎉

---

## 💬 Feedback

Found a bug or have a suggestion? Update the app and let us know!

**Happy Budgeting!** 💰📊✨

