"""
Accor Loyalty Platform - Feature Engineering for Churn Prediction
Transforms raw and RFM data into a high-dimensional feature matrix for machine learning.
"""

import numpy as np
import pandas as pd
from typing import Tuple, List, Dict


NUMERIC_FEATURES = [
    "recency_days",
    "frequency_stays",
    "monetary_spend_eur",
    "total_room_nights",
    "avg_length_of_stay",
    "avg_daily_rate_adr",
    "total_ancillary_spend_eur",
    "avg_booking_lead_time",
    "direct_channel_ratio",
    "distinct_brands_stayed",
    "luxury_premium_ratio",
    "cancellation_rate",
    "avg_satisfaction_score",
    "total_complaints",
    "points_redemption_rate",
    "tenure_days",
    "reward_points_balance",
    "status_points",
    "app_installed",
    "email_subscribed",
    "r_score",
    "f_score",
    "m_score",
    "rfm_composite_score"
]

CATEGORICAL_FEATURES = [
    "current_tier",
    "primary_travel_purpose"
]


def prepare_churn_feature_matrix(
    df: pd.DataFrame, 
    is_training: bool = True
) -> Tuple[pd.DataFrame, pd.Series, List[str]]:
    """
    Constructs feature matrix X and target y with one-hot encoding
    and missing value imputation.
    """
    df_clean = df.copy()
    
    # Fill any null values with domain defaults
    df_clean["avg_satisfaction_score"] = df_clean["avg_satisfaction_score"].fillna(7.5)
    df_clean["cancellation_rate"] = df_clean["cancellation_rate"].fillna(0.0)
    df_clean["direct_channel_ratio"] = df_clean["direct_channel_ratio"].fillna(0.5)
    df_clean["points_redemption_rate"] = df_clean["points_redemption_rate"].fillna(0.0)
    df_clean["total_complaints"] = df_clean["total_complaints"].fillna(0)
    
    # Derived interaction features
    # 1. Ancillary spend intensity (ancillary spend per completed stay)
    df_clean["ancillary_intensity"] = (
        df_clean["total_ancillary_spend_eur"] / np.maximum(1, df_clean["frequency_stays"])
    )
    # 2. Spend per night (total monetary / room nights)
    df_clean["spend_per_night"] = (
        df_clean["monetary_spend_eur"] / np.maximum(1, df_clean["total_room_nights"])
    )
    # 3. Inactivity to tenure ratio
    df_clean["dormancy_ratio"] = (
        df_clean["recency_days"] / np.maximum(30, df_clean["tenure_days"])
    )
    
    engineered_numerics = NUMERIC_FEATURES + ["ancillary_intensity", "spend_per_night", "dormancy_ratio"]
    
    # One-hot encode categorical features
    df_encoded = pd.get_dummies(df_clean[CATEGORICAL_FEATURES], drop_first=True, dtype=float)
    
    # Combine numerics and encoded categoricals
    X = pd.concat([df_clean[engineered_numerics], df_encoded], axis=1)
    
    feature_names = list(X.columns)
    
    y = df_clean["is_churned"] if "is_churned" in df_clean.columns else None
    
    return X, y, feature_names
