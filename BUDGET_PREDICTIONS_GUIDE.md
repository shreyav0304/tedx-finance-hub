# 💡 Budget Prediction & Suggestions Feature

## Overview
I've added an intelligent budget prediction system that analyzes your spending patterns and provides actionable recommendations on how much more budget your team needs.

---

## ✨ Key Features

### 1. **Financial Overview Dashboard**
- **Total Income**: Shows all funds received (management + sponsorship)
- **Total Spent**: Current approved expenditure
- **Remaining Funds**: Available balance
- **Runway**: Days until funds run out at current spending rate

### 2. **Burn Rate Analysis** 🔥
Calculates your spending velocity across three time frames:
- **Daily Burn Rate**: Average spending per day
- **Weekly Burn Rate**: Spending per week
- **Monthly Burn Rate**: Projected monthly spending

### 3. **Smart Recommendations** 🎯
AI-powered insights that alert you to:
- **Critical Alerts**: When runway < 30 days
- **Warning Alerts**: When runway < 60 days
- **Category Overruns**: Specific categories exceeding budget
- **Funding Needs**: How much additional money required

### 4. **Category-wise Predictions** 📊
For each budget category, see:
- **Current Budget**: Allocated amount
- **Spent**: Amount used so far
- **Utilization**: Percentage of budget used
- **Daily Burn Rate**: Category-specific spending velocity
- **Predicted Total**: Estimated total spending by end date
- **Suggested Budget**: Recommended budget (with 20% buffer)
- **Budget Shortage**: Additional funds needed for this category
- **Status**: Health indicator (Healthy/Moderate/Warning/Critical)

### 5. **Weekly Spending Trend** 📈
Interactive chart showing spending patterns over the last 8 weeks to visualize trends.

### 6. **Additional Funds Summary** 💸
Clear calculation of exactly how much more money you need to:
- Complete the event safely
- Maintain recommended 20% buffer
- Cover all projected category spending

---

## 🎯 How It Works

### Prediction Algorithm
1. **Analyzes last 30 days** of approved transactions
2. **Calculates spending velocity** per category
3. **Projects future spending** based on days remaining in budget period
4. **Adds 20% safety buffer** for unexpected costs
5. **Compares** with current budget allocation
6. **Generates recommendations** with specific actions

### Example Calculation
```
Marketing Category:
- Current Budget: ₹50,000
- Spent (30 days): ₹20,000
- Daily Burn: ₹667 (₹20,000 ÷ 30 days)
- Days Remaining: 45 days
- Predicted Additional Spend: ₹30,015 (₹667 × 45)
- Predicted Total: ₹50,015 (₹20,000 + ₹30,015)
- Suggested Budget: ₹60,018 (₹50,015 × 1.2 buffer)
- Shortage: ₹10,018 (₹60,018 - ₹50,000)
```

---

## 📍 How to Access

### Navigation
- **Desktop**: Click "💡 Predictions" in the top navigation bar
- **Mobile**: Tap menu → "💡 Predictions"
- **Direct URL**: `/budget-suggestions/`

---

## 🎨 Visual Indicators

### Status Colors
- 🟢 **Green (Healthy)**: < 60% utilized
- 🔵 **Blue (Moderate)**: 60-80% utilized  
- 🟡 **Yellow (Warning)**: 80-100% utilized
- 🔴 **Red (Critical)**: > 100% utilized

### Recommendation Types
- 🚨 **Critical**: Immediate action required (runway < 30 days)
- ⚠️ **Warning**: Attention needed (runway < 60 days)
- 💡 **Info**: Helpful suggestions for budget planning
- ✅ **Success**: All good, keep monitoring

---

## 💡 Use Cases

### For Event Organizers
- **Budget Planning**: Know exactly how much to allocate per category
- **Fundraising Goals**: Clear target for sponsor acquisition
- **Risk Management**: Early warning before running out of funds

### For Treasurers
- **Financial Forecasting**: Data-driven predictions instead of guesswork
- **Stakeholder Reports**: Show board/team financial health with evidence
- **Budget Adjustments**: Identify which categories need reallocation

### For Team Leads
- **Category Insights**: Understand your department's spending patterns
- **Justification**: Data to support budget increase requests
- **Planning**: Adjust timeline/scope based on budget runway

---

## 📊 Sample Insights You'll See

### Critical Alert Example
```
🚨 Critical: Funds Running Low
At current spending rate, you have only 23 days of runway. 
Immediate action required!

💡 Action: Secure additional ₹45,000 to ensure 60 days of operations.
```

### Category Alert Example
```
💡 Marketing Budget Increase Needed
Current trend suggests you'll exceed budget by ₹12,500

💡 Action: Consider increasing Marketing budget to ₹62,500
```

### Funding Summary Example
```
💸 Additional Funding Required
To complete event safely, you need ₹85,000 more

Based on current spending trends and projected needs with 20% buffer.
```

---

## 🔧 Technical Details

### Data Sources
- **Transactions**: Last 30 days of approved transactions
- **Budgets**: All active budget allocations
- **Income**: Management funds + Sponsor contributions
- **Time-based**: Analyzes spending velocity trends

### Calculations
- **Burn Rate**: `Total Spent ÷ Days Analyzed`
- **Runway**: `Remaining Funds ÷ Daily Burn Rate`
- **Predicted Spend**: `Daily Burn × Days Remaining`
- **Suggested Budget**: `Predicted Total × 1.2`

### Performance
- Lightweight queries with aggregations
- Caches category insights
- Real-time calculations based on latest data

---

## 🎓 Best Practices

### For Accurate Predictions
1. **Approve transactions promptly** - Predictions use approved transactions only
2. **Set realistic budget end dates** - Ensures accurate day calculations
3. **Review weekly** - Spending patterns change over time
4. **Update budgets** - As you secure more funding, update budget amounts

### Interpreting Results
- **High utilization early** → Need to slow spending or get more funds
- **Low daily burn** → May have overestimated budget
- **Increasing trend** → Events typically accelerate spending near date
- **Negative runway** → Already over budget, need immediate funding

---

## 🚀 Next Steps

### After Viewing Predictions
1. **Review Recommendations**: Read each alert carefully
2. **Prioritize Actions**: Critical alerts first, then warnings
3. **Adjust Spending**: Slow down in overrun categories
4. **Seek Funding**: Use predictions to justify sponsor asks
5. **Reallocate**: Move budget from underutilized to overrun categories
6. **Monitor Weekly**: Track if actions are improving runway

### Using for Sponsor Pitches
```
"Based on our financial analysis, we need ₹85,000 more to 
complete the event successfully. Our prediction model shows:
- Marketing: ₹25,000 (for promotional campaigns)
- Logistics: ₹30,000 (venue and equipment)
- Speakers: ₹30,000 (honorariums and travel)

We have 45 days runway and need to secure these funds within 
30 days to stay on track."
```

---

## 📱 Mobile Friendly
- Fully responsive design
- Touch-friendly buttons and charts
- Horizontal scrolling for tables on small screens

---

## 🎯 Future Enhancements (Potential)
- Export predictions to PDF for board meetings
- Email alerts when runway drops below threshold
- Historical comparison (vs. previous events)
- AI suggestions for cost-cutting measures
- Integration with accounting software

---

## ❓ FAQ

**Q: Why does my suggested budget seem high?**  
A: We add a 20% buffer for unexpected costs. Events typically have surprise expenses.

**Q: The prediction says I need more money, but we're cutting costs?**  
A: Predictions are based on the last 30 days. If you recently cut costs, check again in a week.

**Q: What if I have no budget data?**  
A: Create budgets first in the Budgets page, then predictions will appear.

**Q: Can I change the prediction timeframe?**  
A: Currently uses 30-day rolling window. This balances recency with statistical significance.

---

## 📞 Support
If you have questions about interpreting your budget predictions, contact your treasurer or review this guide.

---

**Built with ❤️ for TEDx Event Organizers**  
Version 1.0 | October 2025
