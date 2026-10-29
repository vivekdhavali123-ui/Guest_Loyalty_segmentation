"""
Unit Tests for Accor RFM Segmentation Engine
"""
import unittest
import pandas as pd
import numpy as np

from src.segmentation.rfm import compute_rfm_scores, assign_rfm_business_segment, compute_rfm_segments


class TestAccorRFM(unittest.TestCase):
    
    def setUp(self):
        # Create synthetic test dataset
        self.df_test = pd.DataFrame({
            "member_id": [f"ALL_{i}" for i in range(1, 11)],
            "recency_days": [10, 45, 90, 150, 210, 290, 370, 450, 20, 80],
            "frequency_stays": [15, 10, 6, 4, 3, 2, 1, 1, 12, 5],
            "monetary_spend_eur": [9500, 6200, 3400, 1800, 1100, 800, 400, 250, 7800, 2900]
        })

    def test_rfm_scores_range(self):
        df_scored = compute_rfm_scores(self.df_test)
        self.assertTrue(all(df_scored["r_score"].between(1, 5)))
        self.assertTrue(all(df_scored["f_score"].between(1, 5)))
        self.assertTrue(all(df_scored["m_score"].between(1, 5)))
        self.assertIn("rfm_cell", df_scored.columns)
        self.assertIn("rfm_composite_score", df_scored.columns)

    def test_champion_segment_assignment(self):
        row = pd.Series({"r_score": 5, "f_score": 5, "m_score": 5, "recency_days": 15})
        seg = assign_rfm_business_segment(row)
        self.assertEqual(seg, "High-Value Champions")

    def test_dormant_segment_assignment(self):
        row = pd.Series({"r_score": 1, "f_score": 1, "m_score": 1, "recency_days": 420})
        seg = assign_rfm_business_segment(row)
        self.assertEqual(seg, "Dormant / Inactive")


if __name__ == "__main__":
    unittest.main()
