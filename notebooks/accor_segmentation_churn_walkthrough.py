"""
Accor Live Limitless (ALL) - Segmentation & Churn Walkthrough
Interactive analysis script demonstrating RFM, K-Means, XGBoost evaluation,
and personalized retention recommendation logic.
"""

import os
import sys
import pandas as pd
import numpy as np

# Add project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def main():
    print("=" * 75)
    print("ACCOR ALL - EXECUTIVE DATA SCIENCE WALKTHROUGH")
    print("=" * 75)
    
    master_path = "data/processed/accor_crm_master_dataset.csv"
    if not os.path.exists(master_path):
        print(f"[!] {master_path} not found. Please run 'python run_pipeline.py' first.")
        return
        
    df = pd.read_csv(master_path)
    print(f"Loaded {len(df):,} Accor loyalty member records.")
    
    print("\n1. PORTFOLIO BREAKDOWN BY K-MEANS SEGMENT:")
    seg_summary = df.groupby("kmeans_segment").agg(
        Members=("member_id", "count"),
        Avg_Spend_EUR=("monetary_spend_eur", "mean"),
        Avg_Stays=("frequency_stays", "mean"),
        Avg_Recency_Days=("recency_days", "mean"),
        Avg_Risk_Score=("churn_risk_score", "mean"),
        Churn_Rate=("is_churned", lambda x: f"{x.mean()*100:.1f}%")
    ).reset_index()
    print(seg_summary.to_string(index=False))
    
    print("\n2. CHURN RISK SCORE SUMMARY BY LOYALTY TIER:")
    tier_summary = df.groupby("current_tier").agg(
        Members=("member_id", "count"),
        Avg_Spend_EUR=("monetary_spend_eur", "mean"),
        High_Risk_Guests=("churn_risk_tier", lambda x: (x == "High Risk").sum()),
        Avg_Risk_Score=("churn_risk_score", "mean")
    ).reset_index()
    print(tier_summary.to_string(index=False))
    
    print("\n3. SAMPLE HIGH-PRIORITY CRM RETENTION PLAYBOOKS:")
    sample_recs = df[
        (df["churn_risk_tier"] == "High Risk") & 
        (df["kmeans_segment"] == "High-Value Champions")
    ].head(3)
    
    for idx, row in sample_recs.iterrows():
        print(f"\n[Member: {row['member_id']} - {row['member_full_name']} | Tier: {row['current_tier']}]")
        print(f"  • Spend: EUR {row['monetary_spend_eur']:,.2f} | Completed Stays: {row['frequency_stays']} | Recency: {row['recency_days']} days")
        print(f"  • Churn Risk Score: {row['churn_risk_score']}/100 ({row['churn_risk_tier']})")
        print(f"  • Primary Risk Drivers: {row['primary_risk_factors']}")
        print(f"  • Recommended Action: {row['retention_action_title']}")
        print(f"  • Channel: {row['recommended_channel']}")
        print(f"  • Incentive Offer: {row['incentive_offer']}")
        print(f"  • Urgency: {row['urgency_level']}")
        print(f"  • 24-Month CLV at Stake: EUR {row['estimated_clv_eur']:,.2f}")
        
    print("\n" + "=" * 75)
    print("Walkthrough completed successfully.")

if __name__ == "__main__":
    main()
