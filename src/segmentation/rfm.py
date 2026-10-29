"""
Accor Loyalty Segmentation - RFM Analysis Engine
Performs classical and hospitality-specific RFM scoring,
percentile ranking, and rule-based segment classification.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple


def compute_rfm_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes quintile scores (1 to 5) for Recency, Frequency, and Monetary metrics.
    Handles tie-breaking and skewed boundaries with rank-based percentiles.
    """
    df_rfm = df.copy()
    
    # Recency: Lower days = better (higher score).
    # We invert rank so smallest recency gets 5, largest gets 1.
    df_rfm["r_score"] = pd.qcut(
        df_rfm["recency_days"].rank(method="first"), 
        q=5, 
        labels=[5, 4, 3, 2, 1]
    ).astype(int)
    
    # Frequency: Higher stays = better score.
    df_rfm["f_score"] = pd.qcut(
        df_rfm["frequency_stays"].rank(method="first"), 
        q=5, 
        labels=[1, 2, 3, 4, 5]
    ).astype(int)
    
    # Monetary: Higher spend = better score.
    df_rfm["m_score"] = pd.qcut(
        df_rfm["monetary_spend_eur"].rank(method="first"), 
        q=5, 
        labels=[1, 2, 3, 4, 5]
    ).astype(int)
    
    # Composite RFM cell and average score
    df_rfm["rfm_cell"] = (
        df_rfm["r_score"].astype(str) + 
        df_rfm["f_score"].astype(str) + 
        df_rfm["m_score"].astype(str)
    )
    df_rfm["rfm_composite_score"] = (
        (df_rfm["r_score"] + df_rfm["f_score"] + df_rfm["m_score"]) / 3.0
    ).round(2)
    
    return df_rfm


def assign_rfm_business_segment(row: pd.Series) -> str:
    """
    Assign hospitality business segments based on RFM scores:
    - High-Value Champions: Top tier, recently active, highest spenders
    - Loyal Mainstays: Consistent frequent business & leisure travellers
    - Potential Loyalists: Recent guests with rising frequency
    - At-Risk High-Spenders: High previous spend, but slipping recency
    - At-Risk Casuals: Declining engagement, low-moderate spend
    - Dormant Members: No activity in > 1 year
    - Value Seekers: Low spend, promo driven
    """
    r = row["r_score"]
    f = row["f_score"]
    m = row["m_score"]
    recency_days = row.get("recency_days", 100)
    
    # Inactive > 365 days or Recency score 1 with low frequency
    if recency_days > 365 or (r == 1 and f <= 2):
        return "Dormant / Inactive"
        
    # High-Value Champions: High recency, top frequency & monetary
    if r >= 4 and f >= 4 and m >= 4:
        return "High-Value Champions"
        
    # At-Risk High-Spenders: Used to spend heavily, but hasn't stayed recently
    if r <= 2 and m >= 4:
        return "At-Risk High-Spenders"
        
    # Loyal Mainstays: Steady and dependable frequency
    if r >= 3 and f >= 3 and m >= 3:
        return "Loyal Mainstays"
        
    # Potential Loyalists: Recent guests with promising start
    if r >= 4 and f in [2, 3] and m in [2, 3, 4]:
        return "Potential Loyalists"
        
    # At-Risk Casuals: Slipping recency and modest frequency
    if r <= 2 and f >= 2:
        return "At-Risk Casuals"
        
    # Value Seekers / Budget
    if m <= 2:
        return "Value Seekers"
        
    # Default fallthrough
    return "Promising Occasional"


def compute_rfm_segments(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full RFM pipeline: Computes scores, RFM composite, and assigns business segment.
    """
    df_scored = compute_rfm_scores(df)
    df_scored["rfm_segment"] = df_scored.apply(assign_rfm_business_segment, axis=1)
    
    print("\n--- RFM Business Segment Distribution ---")
    dist = df_scored["rfm_segment"].value_counts(normalize=True) * 100
    for seg, pct in dist.items():
        count = (df_scored["rfm_segment"] == seg).sum()
        print(f"  {seg:<26}: {pct:5.2f}% ({count:,} members)")
        
    return df_scored
