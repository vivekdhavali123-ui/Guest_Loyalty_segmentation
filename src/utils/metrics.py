"""
Accor Loyalty Platform - Business Metrics & ROI Calculator
"""
import pandas as pd
from typing import Dict, Any


def compute_business_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes executive business metrics, revenue exposure, and potential retention savings.
    """
    total_members = len(df)
    total_revenue = df["monetary_spend_eur"].sum()
    avg_spend = df["monetary_spend_eur"].mean()
    
    # Churn Metrics
    churned_members = (df["is_churned"] == 1).sum() if "is_churned" in df.columns else (df["recency_days"] > 365).sum()
    churn_rate = (churned_members / total_members) * 100
    
    # High Risk Metrics
    high_risk_members = (df["churn_risk_tier"] == "High Risk").sum()
    high_risk_pct = (high_risk_members / total_members) * 100
    
    # Revenue at stake
    revenue_at_risk = df[df["churn_risk_tier"].isin(["High Risk", "Medium Risk"])]["monetary_spend_eur"].sum()
    high_value_at_risk = df[(df["churn_risk_tier"] == "High Risk") & (df["kmeans_segment"].str.contains("High-Value|Spenders", na=False))]["monetary_spend_eur"].sum()
    
    # CLV at stake
    total_clv_at_risk = df[df["churn_risk_tier"] == "High Risk"]["estimated_clv_eur"].sum() if "estimated_clv_eur" in df.columns else 0.0
    
    # Estimated Retention Campaign Economics:
    # Target top 2,000 high-risk/at-risk high spenders
    # Cost per contact: ~€12 (concierge call + promo incentives)
    # Average expected retention uplift: ~25%
    retained_revenue_target = revenue_at_risk * 0.18 # conservative 18% recovery
    est_campaign_cost = min(50000.0, total_members * 4.5)
    net_retention_roi = ((retained_revenue_target - est_campaign_cost) / max(1.0, est_campaign_cost)) * 100
    
    kpis = {
        "total_active_loyalty_members": int(total_members),
        "total_portfolio_revenue_eur": round(float(total_revenue), 2),
        "average_member_spend_eur": round(float(avg_spend), 2),
        "overall_churn_rate_pct": round(float(churn_rate), 2),
        "high_risk_member_count": int(high_risk_members),
        "high_risk_member_pct": round(float(high_risk_pct), 2),
        "total_revenue_at_risk_eur": round(float(revenue_at_risk), 2),
        "high_value_revenue_at_stake_eur": round(float(high_value_at_risk), 2),
        "estimated_clv_at_risk_eur": round(float(total_clv_at_risk), 2),
        "projected_campaign_recovered_revenue_eur": round(float(retained_revenue_target), 2),
        "projected_campaign_roi_pct": round(float(net_retention_roi), 1)
    }
    
    return kpis
