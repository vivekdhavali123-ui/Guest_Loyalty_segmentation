"""
Accor Loyalty Platform - Personalized Retention Recommendation Engine
Generates tailored Next-Best-Action strategies, targeted incentive offers,
and marketing channel recommendations for CRM teams to prevent customer churn.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any


class AccorRetentionEngine:
    """
    Prescriptive AI engine translating segmentation and churn risk scores
    into actionable retention campaigns across Accor's multi-brand ecosystem.
    """
    
    @staticmethod
    def generate_recommendation_for_member(row: pd.Series) -> Dict[str, Any]:
        """
        Evaluates member dimensions to formulate personalized retention actions.
        """
        segment = row.get("kmeans_segment", row.get("rfm_segment", "Loyal Mainstays"))
        risk_tier = row.get("churn_risk_tier", "Low Risk")
        tier = row.get("current_tier", "Classic")
        complaints = row.get("total_complaints", 0)
        sat_score = row.get("avg_satisfaction_score", 8.0)
        recency = row.get("recency_days", 60)
        pts_bal = row.get("reward_points_balance", 0)
        monetary = row.get("monetary_spend_eur", 500)
        app_installed = row.get("app_installed", True)
        purpose = row.get("primary_travel_purpose", "Leisure")
        
        # Calculate Estimated Customer Lifetime Value (CLV in EUR over next 24 months)
        annual_spend = monetary / max(1.0, (row.get("tenure_days", 365) / 365.0))
        retention_prob = 1.0 - (row.get("churn_probability", 0.3))
        clv_24m = round(annual_spend * 2.0 * max(0.2, retention_prob), 2)
        
        # 1. High Priority Case: High complaints / Service friction
        if complaints > 0 or sat_score < 6.0:
            return {
                "retention_action_title": "Executive Service Recovery & Welcome Back Hospitality Credit",
                "action_category": "Service Recovery",
                "recommended_channel": "Dedicated CRM Concierge Call" if tier in ["Platinum", "Diamond", "Gold"] else "Personalized GM Email",
                "incentive_offer": "€100 F&B/Spa credit on next stay + 2,000 complimentary ALL Reward Points",
                "urgency_level": "Immediate (within 48 Hours)",
                "target_brand_tier": "Previous Hotel Brand",
                "estimated_clv_eur": clv_24m,
                "projected_retention_uplift_pct": 28.5
            }
            
        # 2. Case: High-Value At-Risk (Champions or Spenders slipping away)
        if segment in ["At-Risk High-Spenders", "High-Value Champions"] and risk_tier in ["High Risk", "Medium Risk"]:
            return {
                "retention_action_title": "Exclusive ALL VIP Retention Invitation & Suite Upgrade",
                "action_category": "VIP High-Touch",
                "recommended_channel": "ALL Ambassador Direct Call & App Push" if app_installed else "Curated Direct Mail + Email",
                "incentive_offer": "Guaranteed Suite Upgrade voucher + Double Status Nights + Private airport transfer at Fairmont / Raffles / Sofitel",
                "urgency_level": "High Priority (within 7 Days)",
                "target_brand_tier": "Luxury / Premium",
                "estimated_clv_eur": clv_24m,
                "projected_retention_uplift_pct": 34.0
            }
            
        # 3. Case: High-Value Champions (Low Churn Risk) - VIP Appreciation & Upsell
        if segment == "High-Value Champions":
            return {
                "retention_action_title": "Tier Milestone Recognition & Limitless Experiences Access",
                "action_category": "Loyalty Celebration",
                "recommended_channel": "ALL App VIP Notification & Email",
                "incentive_offer": "Early access to Roland-Garros / Accor Arena VIP tickets + 2,500 bonus points on next stay",
                "urgency_level": "Standard Cycle (30 Days)",
                "target_brand_tier": "Luxury / Lifestyle",
                "estimated_clv_eur": clv_24m,
                "projected_retention_uplift_pct": 12.0
            }
            
        # 4. Case: Loyal Mainstays with Elevated Risk
        if segment == "Loyal Mainstays" and risk_tier in ["High Risk", "Medium Risk"]:
            if purpose == "Business":
                offer = "Mid-week Fast-Track Check-in + Free High-Speed WiFi & Breakfast at Novotel/Pullman"
            else:
                offer = "Weekend Getaway 3-for-2 nights offer + 1,500 ALL Reward points bonus"
            return {
                "retention_action_title": "Frequent Traveller Loyalty Multiplier & Booking Incentive",
                "action_category": "Points Multiplier",
                "recommended_channel": "ALL App Push Notification" if app_installed else "Email Newsletter Exclusive",
                "incentive_offer": offer,
                "urgency_level": "High Priority (within 14 Days)",
                "target_brand_tier": "Premium / Midscale",
                "estimated_clv_eur": clv_24m,
                "projected_retention_uplift_pct": 24.5
            }
            
        # 5. Case: Dormant Members (High recency inactivity > 365 days)
        if segment == "Dormant / Churned" or recency > 365:
            return {
                "retention_action_title": "'We Miss You' Global Reactivation Escape Pass",
                "action_category": "Reactivation Campaign",
                "recommended_channel": "Re-engagement Email & Dynamic Social Ad Audience",
                "incentive_offer": "25% discount on next stay + Flexible cancellation up to 6pm on arrival date",
                "urgency_level": "Standard Cycle (30 Days)",
                "target_brand_tier": "Midscale / Economy",
                "estimated_clv_eur": clv_24m,
                "projected_retention_uplift_pct": 18.0
            }
            
        # 6. Case: Value Seekers / Budget Guests
        if segment == "Value Seekers":
            return {
                "retention_action_title": "ibis Network Flash Deal & Direct Booking Member Rate",
                "action_category": "Price / Value Incentive",
                "recommended_channel": "ALL App Flash Alert & SMS Promo",
                "incentive_offer": "Additional 10% off member-only rate at ibis & ibis Styles + Free morning coffee",
                "urgency_level": "Low Priority (Campaign Cadence)",
                "target_brand_tier": "Economy",
                "estimated_clv_eur": clv_24m,
                "projected_retention_uplift_pct": 15.0
            }
            
        # Default recommendation
        return {
            "retention_action_title": "ALL Points Accelerator & Destination Discovery",
            "action_category": "Nurture Campaign",
            "recommended_channel": "Email Campaign",
            "incentive_offer": "Double points on your next booking across 5,000+ properties globally",
            "urgency_level": "Standard Cycle (30 Days)",
            "target_brand_tier": "All Accor Brands",
            "estimated_clv_eur": clv_24m,
            "projected_retention_uplift_pct": 10.5
        }

    def generate_batch_recommendations(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies recommendation logic across full dataframe of members.
        """
        print("\n[*] Generating personalized retention recommendations for loyalty members...")
        recs = [self.generate_recommendation_for_member(row) for _, row in df.iterrows()]
        df_recs = pd.DataFrame(recs)
        
        df_merged = pd.concat([df.reset_index(drop=True), df_recs.reset_index(drop=True)], axis=1)
        
        print("--- Personalized Retention Actions Summary ---")
        summary = df_merged["action_category"].value_counts()
        for cat, cnt in summary.items():
            pct = (cnt / len(df_merged)) * 100
            print(f"  {cat:<26}: {pct:5.2f}% ({cnt:,} recommendations)")
            
        return df_merged
