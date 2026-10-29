"""
Accor Live Limitless (ALL) Loyalty & Guest Segmentation Platform
End-to-End Master Pipeline Orchestrator

Executes:
1. Data Generation (5,000+ Accor properties, members, bookings)
2. SQL Schema Ingestion & Analytical RFM Feature Transformation
3. RFM Quantile Scoring & Rule-Based Segmentation
4. Unsupervised K-Means Clustering with Elbow & Silhouette Profiling
5. Machine Learning Churn Modeling (Scikit-Learn vs XGBoost)
6. Calibrated 0-100 Customer Risk Scoring & Churn Driver Explainability
7. Prescriptive AI Retention Recommendation Engine
8. Power BI Star Schema & Clean Master Dataset Exports
"""

import os
import sys
import json
import time
import datetime
import pandas as pd
import numpy as np

# Reconfigure console encoding for Windows cmd/powershell
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.data_generator import run_data_generation
from sql.seed_data_loader import load_database, execute_rfm_sql_analytics
from src.segmentation.rfm import compute_rfm_segments
from src.segmentation.kmeans_clusterer import AccorKMeansClusterer
from src.models.feature_engineering import prepare_churn_feature_matrix
from src.models.churn_model import AccorChurnModelPipeline
from src.models.explainability import get_global_feature_importance, extract_churn_risk_factors
from src.recommendation.retention_engine import AccorRetentionEngine
from src.utils.metrics import compute_business_kpis


def run_accor_loyalty_pipeline():
    start_time = time.time()
    print("=" * 80)
    print("ACCOR LIVE LIMITLESS (ALL) - ENTERPRISE AI CUSTOMER SEGMENTATION & CHURN PLATFORM")
    print("Across 5,000+ Properties Globally | Luxury, Premium, Midscale, Economy")
    print("=" * 80)
    
    # Paths
    raw_dir = "data/raw"
    processed_dir = "data/processed"
    powerbi_dir = "data/powerbi"
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(powerbi_dir, exist_ok=True)
    
    # ---------------------------------------------------------
    # STEP 1: Raw Data Generation / Check
    # ---------------------------------------------------------
    raw_member_file = os.path.join(raw_dir, "loyalty_members.csv")
    raw_prop_file = os.path.join(raw_dir, "properties.csv")
    raw_booking_file = os.path.join(raw_dir, "bookings.csv")
    
    if not (os.path.exists(raw_member_file) and os.path.exists(raw_prop_file) and os.path.exists(raw_booking_file)):
        print("\n[STEP 1] Generating high-fidelity synthetic Accor ecosystem data...")
        df_props, df_members, df_bookings, df_camps = run_data_generation(
            output_dir=raw_dir, 
            n_properties=5000, 
            n_members=12000
        )
    else:
        print("\n[STEP 1] Existing raw data found. Loading from files...")
        df_props = pd.read_csv(raw_prop_file)
        df_members = pd.read_csv(raw_member_file)
        df_bookings = pd.read_csv(raw_booking_file)
        print(f"[+] Loaded {len(df_props):,} properties, {len(df_members):,} members, {len(df_bookings):,} bookings.")
        
    # ---------------------------------------------------------
    # STEP 2: SQL Ingestion & Analytical RFM Query Execution
    # ---------------------------------------------------------
    print("\n[STEP 2] Executing SQL Analytical Pipeline & RFM Extraction...")
    conn = load_database()
    df_rfm_raw = execute_rfm_sql_analytics(conn)
    
    # ---------------------------------------------------------
    # STEP 3: Classical RFM Segmentation
    # ---------------------------------------------------------
    print("\n[STEP 3] Running Classical RFM Scoring & Hospitality Business Rules...")
    df_rfm = compute_rfm_segments(df_rfm_raw)
    
    # ---------------------------------------------------------
    # STEP 4: K-Means Clustering & Profiling
    # ---------------------------------------------------------
    print("\n[STEP 4] Executing Unsupervised K-Means Machine Learning Clustering...")
    clusterer = AccorKMeansClusterer(n_clusters=5, random_state=42)
    # Evaluate Elbow & Silhouette
    cluster_eval = clusterer.evaluate_optimal_k(df_rfm, k_range=range(3, 7))
    df_clustered = clusterer.fit_predict(df_rfm)
    clusterer.save(os.path.join(processed_dir, "kmeans_model.joblib"))
    
    # ---------------------------------------------------------
    # STEP 5: Churn Feature Engineering & Dataset Prep
    # ---------------------------------------------------------
    print("\n[STEP 5] Preparing Feature Matrix for Machine Learning Churn Models...")
    X, y, feature_names = prepare_churn_feature_matrix(df_clustered, is_training=True)
    print(f"[+] Engineered {X.shape[1]} features across {X.shape[0]:,} member records.")
    
    # ---------------------------------------------------------
    # STEP 6: Churn Model Training & Evaluation (Scikit-Learn vs XGBoost)
    # ---------------------------------------------------------
    print("\n[STEP 6] Training & Comparing Churn Prediction Models (Scikit-Learn & XGBoost)...")
    churn_pipeline = AccorChurnModelPipeline(random_state=42)
    eval_metrics = churn_pipeline.train_and_evaluate(X, y, test_size=0.20)
    churn_pipeline.save(os.path.join(processed_dir, "churn_model_champion.joblib"))
    
    # Predict Churn Probabilities & 0-100 Risk Scores
    df_scored = churn_pipeline.predict_risk_scores(df_clustered, X)
    
    # ---------------------------------------------------------
    # STEP 7: Explainability & Primary Risk Factor Decomposition
    # ---------------------------------------------------------
    print("\n[STEP 7] Extracting Global Feature Importances & Guest Risk Factors...")
    df_feat_imp = get_global_feature_importance(churn_pipeline.best_model, feature_names, top_n=12)
    df_feat_imp.to_csv(os.path.join(processed_dir, "feature_importances.csv"), index=False)
    print("Top Churn Drivers:")
    for _, f_row in df_feat_imp.head(6).iterrows():
        print(f"  - {f_row['feature']:<28}: {f_row['importance_pct']:.2f}%")
        
    df_scored["primary_risk_factors"] = df_scored.apply(extract_churn_risk_factors, axis=1)
    
    # ---------------------------------------------------------
    # STEP 8: Personalized Retention Recommendation Engine
    # ---------------------------------------------------------
    print("\n[STEP 8] Executing AI Retention Recommendation Engine...")
    recommender = AccorRetentionEngine()
    df_master = recommender.generate_batch_recommendations(df_scored)
    
    # ---------------------------------------------------------
    # STEP 9: Business Financial KPIs & Executive Metrics
    # ---------------------------------------------------------
    print("\n[STEP 9] Calculating Business KPIs & Revenue-at-Risk Economics...")
    business_kpis = compute_business_kpis(df_master)
    print("\n" + "=" * 50)
    print("EXECUTIVE BUSINESS DASHBOARD METRICS")
    print("=" * 50)
    print(f"Total Portfolio Members:       {business_kpis['total_active_loyalty_members']:,}")
    print(f"Total Portfolio Revenue:       EUR {business_kpis['total_portfolio_revenue_eur']:,.2f}")
    print(f"Average Revenue per Member:    EUR {business_kpis['average_member_spend_eur']:,.2f}")
    print(f"Overall Churn Rate:            {business_kpis['overall_churn_rate_pct']:.2f}%")
    print(f"High-Risk Members:             {business_kpis['high_risk_member_count']:,} ({business_kpis['high_risk_member_pct']:.2f}%)")
    print(f"Total Revenue at Risk:         EUR {business_kpis['total_revenue_at_risk_eur']:,.2f}")
    print(f"High-Value Spend at Risk:      EUR {business_kpis['high_value_revenue_at_stake_eur']:,.2f}")
    print(f"CLV at Risk (24 Months):       EUR {business_kpis['estimated_clv_at_risk_eur']:,.2f}")
    print(f"Projected Campaign Recovery:   EUR {business_kpis['projected_campaign_recovered_revenue_eur']:,.2f}")
    print(f"Projected Retention ROI:       {business_kpis['projected_campaign_roi_pct']:.1f}%")
    print("=" * 50)
    
    # ---------------------------------------------------------
    # STEP 10: Power BI & CRM Analytical Datasets Export
    # ---------------------------------------------------------
    print("\n[STEP 10] Exporting Star-Schema Tables & Master Dataset for Power BI...")
    
    # 1. Master CRM Mega-Table (Everything joined for instant Power BI reporting)
    master_csv_path = os.path.join(powerbi_dir, "accor_crm_master_dataset.csv")
    df_master.to_csv(master_csv_path, index=False)
    print(f"[+] Saved {master_csv_path} ({len(df_master):,} rows)")
    
    # Also save to processed
    df_master.to_csv(os.path.join(processed_dir, "accor_crm_master_dataset.csv"), index=False)
    
    # 2. Dimension Tables
    df_members.to_csv(os.path.join(powerbi_dir, "dim_loyalty_members.csv"), index=False)
    df_props.to_csv(os.path.join(powerbi_dir, "dim_properties.csv"), index=False)
    
    # 3. Fact Table: Member Segments & Churn Risk
    cols_fact_segments = [
        "member_id", "current_tier", "rfm_segment", "kmeans_cluster", "kmeans_segment",
        "recency_days", "frequency_stays", "monetary_spend_eur", "rfm_composite_score",
        "churn_probability", "churn_risk_score", "churn_risk_tier", "is_churned",
        "retention_action_title", "action_category", "recommended_channel",
        "incentive_offer", "urgency_level", "estimated_clv_eur", "projected_retention_uplift_pct",
        "primary_risk_factors"
    ]
    df_master[cols_fact_segments].to_csv(os.path.join(powerbi_dir, "fact_member_segments_churn.csv"), index=False)
    
    # 4. Summary Table for Quick KPI Cards
    summary_by_segment = df_master.groupby("kmeans_segment").agg(
        member_count=("member_id", "count"),
        total_revenue_eur=("monetary_spend_eur", "sum"),
        avg_spend_eur=("monetary_spend_eur", "mean"),
        avg_recency_days=("recency_days", "mean"),
        avg_stays=("frequency_stays", "mean"),
        avg_churn_risk_score=("churn_risk_score", "mean"),
        high_risk_members=("churn_risk_tier", lambda x: (x == "High Risk").sum()),
        clv_eur=("estimated_clv_eur", "sum")
    ).reset_index()
    summary_by_segment["pct_of_portfolio"] = (summary_by_segment["member_count"] / len(df_master)) * 100
    summary_by_segment.to_csv(os.path.join(powerbi_dir, "accor_segment_kpi_summary.csv"), index=False)
    
    # 5. CRM Campaign Actionable Outreach List (High Risk & High Value members)
    crm_action_list = df_master[
        (df_master["churn_risk_tier"].isin(["High Risk", "Medium Risk"])) &
        (df_master["kmeans_segment"].isin(["High-Value Champions", "At-Risk High-Spenders", "Loyal Mainstays"]))
    ].sort_values(by=["churn_risk_score", "monetary_spend_eur"], ascending=[False, False])
    crm_action_list.to_csv(os.path.join(powerbi_dir, "accor_retention_campaign_list.csv"), index=False)
    print(f"[+] Saved high-priority CRM retention campaign list ({len(crm_action_list):,} prioritized guests)")
    
    # Save Pipeline Summary JSON
    summary_data = {
        "execution_timestamp": datetime.datetime.now().isoformat(),
        "runtime_seconds": round(time.time() - start_time, 2),
        "total_properties_simulated": len(df_props),
        "total_members": len(df_members),
        "total_bookings": len(df_bookings),
        "champion_churn_model": churn_pipeline.best_model_name,
        "champion_model_metrics": eval_metrics[churn_pipeline.best_model_name],
        "business_kpis": business_kpis,
        "optimal_k_evaluation": cluster_eval,
        "segment_distribution": df_master["kmeans_segment"].value_counts().to_dict(),
        "risk_tier_distribution": df_master["churn_risk_tier"].value_counts().to_dict()
    }
    with open(os.path.join(processed_dir, "pipeline_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)
        
    conn.close()
    elapsed = time.time() - start_time
    print(f"\n[SUCCESS] Entire Accor Segmentation & Churn Pipeline finished successfully in {elapsed:.2f} seconds!")
    return df_master, summary_data


if __name__ == "__main__":
    run_accor_loyalty_pipeline()
