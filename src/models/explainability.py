"""
Accor Loyalty Platform - Explainability & Risk Factor Decomposition
Extracts global model feature importances and decomposes member-level churn drivers.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any


def get_global_feature_importance(model: Any, feature_names: List[str], top_n: int = 12) -> pd.DataFrame:
    """
    Extracts sorted feature importance dataframe from Random Forest or XGBoost model.
    """
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    else:
        importances = np.zeros(len(feature_names))
        
    df_imp = pd.DataFrame({
        "feature": feature_names,
        "importance": importances
    }).sort_values(by="importance", ascending=False).reset_index(drop=True)
    
    df_imp["importance_pct"] = (df_imp["importance"] / df_imp["importance"].sum()) * 100
    return df_imp.head(top_n)


def extract_churn_risk_factors(row: pd.Series) -> str:
    """
    Decomposes the primary behavioral drivers triggering high churn risk for a member.
    """
    drivers = []
    
    # Recency check
    recency = row.get("recency_days", 0)
    if recency >= 300:
        drivers.append(f"Extended absence ({int(recency)} days since last checkout)")
    elif recency >= 180:
        drivers.append(f"Inactivity period ({int(recency)} days without stay)")
        
    # Cancellation rate
    cancel_rate = row.get("cancellation_rate", 0)
    if cancel_rate >= 0.30:
        drivers.append(f"High cancellation rate ({cancel_rate*100:.0f}%)")
        
    # Complaints & satisfaction
    complaints = row.get("total_complaints", 0)
    sat_score = row.get("avg_satisfaction_score", 8.0)
    if complaints > 0 or sat_score < 6.5:
        drivers.append(f"Service friction (Rating: {sat_score:.1f}/10, Complaints: {int(complaints)})")
        
    # Channel shift
    direct_ratio = row.get("direct_channel_ratio", 0.5)
    if direct_ratio < 0.25:
        drivers.append("Channel disintermediation (High OTA reliance)")
        
    # Unredeemed points
    pts = row.get("reward_points_balance", 0)
    if pts > 8000 and recency > 150:
        drivers.append(f"Unredeemed point balance ({int(pts):,} pts at risk)")
        
    # Frequency
    freq = row.get("frequency_stays", 1)
    if freq <= 1 and recency > 120:
        drivers.append("Single-stay non-repeat guest")
        
    if not drivers:
        return "Stable booking pattern, minimal behavioral friction"
        
    return " | ".join(drivers[:2])
