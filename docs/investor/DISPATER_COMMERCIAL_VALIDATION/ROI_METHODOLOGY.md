# DISPATER.AI — Commercial ROI & Value Calculation Methodology

**Calculator Module:** `OperationalValueCalculator` in `aurex/dispater_intelligence.py`

---

## Calculation Formula

$$\text{Monthly Evaluated Revenue} = \text{Job Volume} \times \text{Average Ticket Value}$$

$$\text{Revenue At Risk} = \text{Monthly Evaluated Revenue} \times \text{Estimated Leakage } (3.5\%)$$

$$\text{Saved Admin Hours} = (\text{Job Volume} \times \text{Admin Hours/Job}) \times \text{Automation Rate } (65\%)$$

$$\text{Monthly Admin Savings} = \text{Saved Admin Hours} \times \text{Hourly Admin Cost } (\$45.00)$$

$$\text{Total Estimated Monthly Value} = \text{Revenue At Risk} + \text{Monthly Admin Savings}$$

---

## Sensitivity Scenarios

- **Conservative:** 1.5% Revenue Leakage, 40% Admin Automation.
- **Baseline:** 3.5% Revenue Leakage, 65% Admin Automation.
- **Optimistic:** 5.0% Revenue Leakage, 80% Admin Automation.
