import numpy as np
import numpy_financial as npf
import matplotlib.pyplot as plt
import seaborn as sns

# Define parameters
purchase_price = 100
original_cash_flows = [20, 30, 40, 50, 60]
discount_rate = 0.10
tax_rate = 0.3
short_term_debt = 10
long_term_debt = 50
long_term_rate = 0.05
n_periods = 5

# Calculate long-term debt payments
long_term_payment = long_term_debt * (long_term_rate * (1 + long_term_rate)**n_periods) / ((1 + long_term_rate)**n_periods - 1)
interest_expenses = [long_term_debt * long_term_rate]
principal_repayments = [long_term_payment - interest_expenses[0]]
remaining_debt = long_term_debt - principal_repayments[0]

for i in range(1, n_periods):
    interest_exp = remaining_debt * long_term_rate
    principal_rep = long_term_payment - interest_exp
    interest_expenses.append(interest_exp)
    principal_repayments.append(principal_rep)
    remaining_debt -= principal_rep

# Without debt NPV
total_cash_flows_no_debt = [-purchase_price] + original_cash_flows
npv_no_debt = npf.npv(discount_rate, total_cash_flows_no_debt)

# With debt, no tax effects NPV
adjusted_cash_flows_no_tax = [-purchase_price]
for i in range(5):
    if i == 0:
        adjusted_cash_flows_no_tax.append(original_cash_flows[i] - interest_expenses[i] - principal_repayments[i] - short_term_debt)
    else:
        adjusted_cash_flows_no_tax.append(original_cash_flows[i] - interest_expenses[i] - principal_repayments[i])
npv_with_debt_no_tax = npf.npv(discount_rate, adjusted_cash_flows_no_tax)

# With debt and tax effects NPV
operating_incomes = [cf / (1 - tax_rate) for cf in original_cash_flows]
tax_with_debt = [(oi - interest_expenses[i]) * tax_rate for i, oi in enumerate(operating_incomes)]
cfo_with_debt = [oi - interest_expenses[i] - tax_with_debt[i] for i, oi in enumerate(operating_incomes)]
adjusted_cash_flows_with_tax = [-purchase_price]
for i in range(5):
    if i == 0:
        adjusted_cash_flows_with_tax.append(cfo_with_debt[i] - principal_repayments[i] - short_term_debt)
    else:
        adjusted_cash_flows_with_tax.append(cfo_with_debt[i] - principal_repayments[i])
npv_with_debt_with_tax = npf.npv(discount_rate, adjusted_cash_flows_with_tax)

# Monte Carlo Simulation
num_simulations = 1000
npvs = []
for _ in range(num_simulations):
    varied_cash_flows = [max(0, np.random.normal(cf, 0.05 * cf)) for cf in original_cash_flows]
    operating_incomes = [cf / (1 - tax_rate) for cf in varied_cash_flows]
    tax_with_debt = [(oi - interest_expenses[i]) * tax_rate for i, oi in enumerate(operating_incomes)]
    cfo_with_debt = [oi - interest_expenses[i] - tax_with_debt[i] for i, oi in enumerate(operating_incomes)]
    adjusted_cash_flows = [-purchase_price]
    for i in range(5):
        if i == 0:
            adjusted_cash_flows.append(cfo_with_debt[i] - principal_repayments[i] - short_term_debt)
        else:
            adjusted_cash_flows.append(cfo_with_debt[i] - principal_repayments[i])
    npv = npf.npv(discount_rate, adjusted_cash_flows)
    npvs.append(npv)

mean_npv = np.mean(npvs)
std_npv = np.std(npvs)

# Visualization

# Bar chart for NPV comparison
labels = ['No Debt', 'With Debt, No Tax Effects', 'With Debt, With Tax Effects']
npvs_values = [npv_no_debt, npv_with_debt_no_tax, npv_with_debt_with_tax]

plt.figure(figsize=(10, 6))
plt.bar(labels, npvs_values)
plt.title('Comparison of NPVs in Different Scenarios')
plt.ylabel('NPV (Million Dollars)')
plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)  # Add horizontal line at zero for reference
for i, v in enumerate(npvs_values):
    plt.text(i, v, f'{v:.2f}', ha='center', va='bottom' if v >= 0 else 'top')

plt.show()

# Histogram for Monte Carlo simulation
plt.figure(figsize=(10, 6))
sns.histplot(npvs, bins=30, stat='density', color='g', alpha=0.6)
plt.axvline(mean_npv, color='k', linestyle='dashed', linewidth=1, label=f'Mean NPV: {mean_npv:.2f}')
plt.axvline(mean_npv + std_npv, color='r', linestyle='dashed', linewidth=1, label=f'+1 SD: {mean_npv + std_npv:.2f}')
plt.axvline(mean_npv - std_npv, color='r', linestyle='dashed', linewidth=1, label=f'-1 SD: {mean_npv - std_npv:.2f}')
plt.title('Distribution of NPVs from Monte Carlo Simulation')
plt.ylabel('Density')
plt.xlabel('NPV (Million Dollars)')
plt.legend()

# Calculate and display probability of positive NPV
probability_positive = np.mean(np.array(npvs) > 0)
plt.text(0.02, 0.98, f'Probability of Positive NPV: {probability_positive*100:.2f}%',
         transform=plt.gca().transAxes, verticalalignment='top')

plt.show()
