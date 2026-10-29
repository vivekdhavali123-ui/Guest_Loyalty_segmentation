# Accor Live Limitless (ALL) - Power BI Dashboard Design Guide

## 1. Executive Color Palette (Accor ALL Brand Aligned)
- **Primary Navy / Background**: `#0E131F` (Dark Luxury Navy)
- **Accor ALL Gold (Accent)**: `#C5A059` / `#D4AF37`
- **High Risk / Churn Alert**: `#E05D5D` (Crimson Coral)
- **Medium Risk**: `#F39C12` (Amber Gold)
- **Low Risk / Active Champions**: `#2ECC71` (Emerald Jade)
- **Card Background**: `#171E2E` with `#26334D` subtle border.
- **Font Family**: Segoe UI / Aptos / Inter.

---

## 2. Report Structure & Page Blueprint

### Page 1: Executive Loyalty Portfolio Health
- **Target Audience**: Chief Commercial Officer, VP Global Loyalty & CRM.
- **Top KPI Cards**:
  1. `[Total Members]` (12,000)
  2. `[Total Revenue EUR]` (€34.9M)
  3. `[Churn Rate %]` (25.1%)
  4. `[High-Value Revenue At Stake EUR]` (€402k)
  5. `[Projected Retention ROI %]` (904.6%)
- **Visual 1 (Donut Chart)**: Members by Loyalty Tier (`Classic`, `Silver`, `Gold`, `Platinum`, `Diamond`).
- **Visual 2 (Clustered Bar Chart)**: Total Revenue by Hotel Brand & Tier (Fairmont, Sofitel, Pullman, Novotel, ibis).
- **Visual 3 (Scatter Plot)**: Recency Days (X-Axis) vs Monetary Spend (Y-Axis) with Bubble Size = Frequency Stays, colored by `churn_risk_tier`.

---

### Page 2: RFM & K-Means Customer Segmentation
- **Target Audience**: CRM Directors & Guest Analytics Leads.
- **Top KPI Cards**:
  1. `[High Value Champions Count]` (3,013)
  2. `[Loyal Mainstays Count]` (3,384)
  3. `[At-Risk High Spenders Count]` (2,135)
  4. `[Dormant Members Count]` (3,201)
- **Visual 1 (Treemap)**: Segment Share of Total Portfolio Revenue.
- **Visual 2 (Heatmap Matrix)**: R-Score (Rows 1-5) vs F-Score (Columns 1-5), Values = Average Monetary Spend EUR.
- **Visual 3 (Stacked Bar Chart)**: K-Means Segments vs Preferred Channel (% ALL Direct App vs OTA).

---

### Page 3: Churn Risk Radar & Early Warning System
- **Target Audience**: Retention Taskforce & Guest Experience Operations.
- **Visual 1 (Gauge / Bullet Chart)**: Overall Portfolio Churn Risk (Current: 25.14% vs Target: < 20.0%).
- **Visual 2 (Feature Importance Bar Chart)**: Top ML Churn Drivers from XGBoost (Recency, R-Score, Satisfaction Score, Cancellation Rate, Service Complaints).
- **Visual 3 (Decomposition Tree)**: Root = `[High Risk Members Count]`, branches = `current_tier` $\rightarrow$ `kmeans_segment` $\rightarrow$ `primary_risk_factors`.

---

### Page 4: CRM Action Center & Personalized Campaign Generator
- **Target Audience**: Campaign Managers & Property General Managers.
- **Slicers / Filters**:
  - `churn_risk_tier` (Multi-select: High Risk, Medium Risk)
  - `kmeans_segment` (Multi-select: High-Value Champions, At-Risk High-Spenders, Loyal Mainstays)
  - `urgency_level` (Immediate 48h, High Priority 7 Days, Standard 30 Days)
  - `recommended_channel` (Concierge Call, App Push, Email, SMS)
- **Interactive Action Table**:
  - Columns: Member ID, Name, Current Tier, Churn Risk Score (Conditional Formatting: Red > 70), Spend EUR, Primary Risk Drivers, Recommended Action Title, Incentive Offer, CLV (€).
- **Export Button**: One-click export to CSV for direct ingestion into Adobe Campaign, Salesforce Marketing Cloud, or Accor ALL CRM.
