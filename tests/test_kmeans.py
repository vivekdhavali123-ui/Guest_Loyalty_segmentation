"""
Unit Tests for Accor K-Means Clustering Engine
"""
import unittest
import pandas as pd
import numpy as np

from src.segmentation.kmeans_clusterer import AccorKMeansClusterer


class TestAccorKMeans(unittest.TestCase):
    
    def setUp(self):
        np.random.seed(42)
        n = 100
        self.df_test = pd.DataFrame({
            "member_id": [f"ALL_{i}" for i in range(1, n + 1)],
            "recency_days": np.random.randint(5, 500, size=n),
            "frequency_stays": np.random.randint(1, 20, size=n),
            "monetary_spend_eur": np.random.uniform(100, 15000, size=n),
            "avg_daily_rate_adr": np.random.uniform(50, 600, size=n),
            "direct_channel_ratio": np.random.uniform(0.1, 1.0, size=n),
            "is_churned": np.random.choice([0, 1], size=n, p=[0.75, 0.25])
        })

    def test_kmeans_clustering_execution(self):
        clusterer = AccorKMeansClusterer(n_clusters=3, random_state=42)
        df_result = clusterer.fit_predict(self.df_test)
        
        self.assertIn("kmeans_cluster", df_result.columns)
        self.assertIn("kmeans_segment", df_result.columns)
        self.assertEqual(len(df_result["kmeans_cluster"].unique()), 3)
        self.assertIsNotNone(clusterer.cluster_summary)

    def test_optimal_k_evaluation(self):
        clusterer = AccorKMeansClusterer(random_state=42)
        results = clusterer.evaluate_optimal_k(self.df_test, k_range=range(3, 5))
        self.assertIn("k", results)
        self.assertIn("inertia", results)
        self.assertIn("silhouette", results)
        self.assertEqual(len(results["k"]), 2)


if __name__ == "__main__":
    unittest.main()
