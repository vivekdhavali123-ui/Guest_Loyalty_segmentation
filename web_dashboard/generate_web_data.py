"""
Generates optimized JSON payload for the interactive Accor ALL Web Dashboard.
"""
import os
import json
import pandas as pd

def export_web_data():
    master_path = "data/processed/accor_crm_master_dataset.csv"
    summary_path = "data/processed/pipeline_summary.json"
    feat_imp_path = "data/processed/feature_importances.csv"
    web_dir = "web_dashboard"
    os.makedirs(web_dir, exist_ok=True)
    
    df = pd.read_csv(master_path)
    with open(summary_path, "r", encoding="utf-8") as f:
        summary_info = json.load(f)
        
    df_feat = pd.read_csv(feat_imp_path)
    
    # Segment breakdown
    segments = []
    for seg, grp in df.groupby("kmeans_segment"):
        segments.append({
            "segment_name": seg,
            "member_count": int(len(grp)),
            "pct_members": round(float(len(grp) / len(df) * 100), 1),
            "total_spend_eur": round(float(grp["monetary_spend_eur"].sum()), 2),
            "avg_spend_eur": round(float(grp["monetary_spend_eur"].mean()), 2),
            "avg_recency_days": round(float(grp["recency_days"].mean()), 1),
            "avg_stays": round(float(grp["frequency_stays"].mean()), 1),
            "avg_churn_score": round(float(grp["churn_risk_score"].mean()), 1),
            "churn_rate_pct": round(float(grp["is_churned"].mean() * 100), 1),
            "high_risk_count": int((grp["churn_risk_tier"] == "High Risk").sum())
        })
    # Sort by total spend descending
    segments.sort(key=lambda x: x["total_spend_eur"], reverse=True)
    
    # Tier breakdown
    tiers = []
    for t_name, grp in df.groupby("current_tier"):
        tiers.append({
            "tier_name": t_name,
            "count": int(len(grp)),
            "total_spend": round(float(grp["monetary_spend_eur"].sum()), 2),
            "avg_spend": round(float(grp["monetary_spend_eur"].mean()), 2),
            "churn_rate": round(float(grp["is_churned"].mean() * 100), 1)
        })
    tier_order = {"Diamond": 5, "Platinum": 4, "Gold": 3, "Silver": 2, "Classic": 1}
    tiers.sort(key=lambda x: tier_order.get(x["tier_name"], 0), reverse=True)
    
    # Churn risk distribution
    risk_distribution = {
        "High Risk": int((df["churn_risk_tier"] == "High Risk").sum()),
        "Medium Risk": int((df["churn_risk_tier"] == "Medium Risk").sum()),
        "Low Risk": int((df["churn_risk_tier"] == "Low Risk").sum())
    }
    
    # Channel distribution
    channel_distribution = {
        "Direct App": round(float(df["direct_channel_ratio"].mean() * 100), 1),
        "OTA & Third-Party": round(float((1 - df["direct_channel_ratio"].mean()) * 100), 1)
    }
    
    # Feature importances
    feature_importances = df_feat.head(8).to_dict("records")
    
    # Top 150 Prioritized Members for CRM Action Drawer
    sample_members = df[
        (df["churn_risk_tier"].isin(["High Risk", "Medium Risk"])) |
        (df["kmeans_segment"] == "High-Value Champions")
    ].sort_values(by=["churn_risk_score", "monetary_spend_eur"], ascending=[False, False]).head(150)
    
    member_records = []
    for _, row in sample_members.iterrows():
        member_records.append({
            "member_id": row["member_id"],
            "name": row["member_full_name"],
            "email": row["email"],
            "tier": row["current_tier"],
            "country": row["country_of_residence"],
            "segment": row["kmeans_segment"],
            "recency_days": int(row["recency_days"]),
            "frequency_stays": int(row["frequency_stays"]),
            "spend_eur": round(float(row["monetary_spend_eur"]), 2),
            "churn_score": round(float(row["churn_risk_score"]), 1),
            "risk_tier": row["churn_risk_tier"],
            "is_churned": int(row["is_churned"]),
            "action_title": row["retention_action_title"],
            "category": row["action_category"],
            "channel": row["recommended_channel"],
            "incentive": row["incentive_offer"],
            "urgency": row["urgency_level"],
            "clv_eur": round(float(row["estimated_clv_eur"]), 2),
            "risk_factors": row["primary_risk_factors"]
        })
        
    dashboard_payload = {
        "kpis": summary_info["business_kpis"],
        "model_metrics": summary_info["champion_model_metrics"],
        "champion_model": summary_info["champion_churn_model"],
        "segments": segments,
        "tiers": tiers,
        "risk_distribution": risk_distribution,
        "channel_distribution": channel_distribution,
        "feature_importances": feature_importances,
        "members": member_records
    }
    
    out_file = os.path.join(web_dir, "dashboard_data.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(dashboard_payload, f, indent=2)
        
    print(f"[OK] Generated {out_file} ({len(member_records)} prioritized guest records)")

if __name__ == "__main__":
    export_web_data()
