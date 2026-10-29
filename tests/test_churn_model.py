"""
Unit Tests for Accor Churn Prediction & Recommendation Engine
"""
import unittest
import pandas as pd
import numpy as np

from src.models.feature_engineering import prepare_churn_feature_matrix
from src.models.churn_model import AccorChurnModelPipeline
from src.recommendation.retention_engine import AccorRetentionEngine


class TestAccorChurnModel(unittest.TestCase):
    
    def setUp(self):
        np.random.seed(42)
        n = 200
        self.df_test = pd.DataFrame({
            "member_id": [f"ALL_{i}" for i in range(1, n + 1)],
            "member_full_name": [f"Guest {i}" for i in range(1, n + 1)],
            "email": [f"guest{i}@example.com" for i in range(1, n + 1)],
            "current_tier": np.random.choice(["Classic", "Silver", "Gold", "Platinum", "Diamond"], size=n),
            "primary_travel_purpose": np.random.choice(["Leisure", "Business", "Bleisure"], size=n),
            "country_of_residence": np.random.choice(["FRA", "GBR", "DEU", "USA"], size=n),
            "recency_days": np.random.randint(5, 500, size=n),
            "frequency_stays": np.random.randint(1, 20, size=n),
            "monetary_spend_eur": np.random.uniform(100, 15000, size=n),
            "total_room_nights": np.random.randint(1, 50, size=n),
            "avg_length_of_stay": np.random.uniform(1.0, 5.0, size=n),
            "avg_daily_rate_adr": np.random.uniform(50, 500, size=n),
            "total_ancillary_spend_eur": np.random.uniform(0, 2000, size=n),
            "avg_booking_lead_time": np.random.uniform(5, 60, size=n),
            "direct_channel_ratio": np.random.uniform(0.1, 1.0, size=n),
            "distinct_brands_stayed": np.random.randint(1, 6, size=n),
            "luxury_premium_ratio": np.random.uniform(0.0, 1.0, size=n),
            "cancellation_rate": np.random.uniform(0.0, 0.5, size=n),
            "avg_satisfaction_score": np.random.uniform(4.0, 10.0, size=n),
            "total_complaints": np.random.choice([0, 1, 2], size=n, p=[0.8, 0.15, 0.05]),
            "points_redemption_rate": np.random.uniform(0.0, 0.5, size=n),
            "tenure_days": np.random.randint(60, 1200, size=n),
            "reward_points_balance": np.random.randint(500, 50000, size=n),
            "status_points": np.random.randint(100, 25000, size=n),
            "app_installed": np.random.choice([True, False], size=n),
            "email_subscribed": np.random.choice([True, False], size=n),
            "r_score": np.random.randint(1, 6, size=n),
            "f_score": np.random.randint(1, 6, size=n),
            "m_score": np.random.randint(1, 6, size=n),
            "rfm_composite_score": np.random.uniform(1.0, 5.0, size=n),
            "kmeans_segment": np.random.choice(["High-Value Champions", "Loyal Mainstays", "At-Risk High-Spenders"], size=n)
        })
        # Synthetic ground truth churn label
        self.df_test["is_churned"] = (
            (self.df_test["recency_days"] > 300) | 
            (self.df_test["cancellation_rate"] > 0.35)
        ).astype(int)

    def test_feature_matrix_and_training(self):
        X, y, feats = prepare_churn_feature_matrix(self.df_test)
        self.assertEqual(len(X), len(self.df_test))
        self.assertEqual(len(y), len(self.df_test))
        self.assertGreater(len(feats), 20)

        pipeline = AccorChurnModelPipeline(random_state=42)
        metrics = pipeline.train_and_evaluate(X, y, test_size=0.25)
        self.assertIn("RandomForest", metrics)
        self.assertIn("XGBoost", metrics)
        self.assertGreater(metrics[pipeline.best_model_name]["roc_auc"], 0.70)

        # Risk scoring
        df_scored = pipeline.predict_risk_scores(self.df_test, X)
        self.assertIn("churn_risk_score", df_scored.columns)
        self.assertIn("churn_risk_tier", df_scored.columns)
        self.assertTrue(all(df_scored["churn_risk_score"].between(0, 100)))

    def test_retention_recommendation_engine(self):
        recommender = AccorRetentionEngine()
        row = pd.Series({
            "kmeans_segment": "High-Value Champions",
            "churn_risk_tier": "High Risk",
            "current_tier": "Platinum",
            "monetary_spend_eur": 8500,
            "tenure_days": 720,
            "churn_probability": 0.85,
            "total_complaints": 1,
            "avg_satisfaction_score": 4.5
        })
        rec = recommender.generate_recommendation_for_member(row)
        self.assertIn("retention_action_title", rec)
        self.assertIn("incentive_offer", rec)
        self.assertIn("recommended_channel", rec)
        self.assertEqual(rec["action_category"], "Service Recovery")


if __name__ == "__main__":
    unittest.main()
