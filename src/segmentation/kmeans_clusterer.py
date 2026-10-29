"""
Accor Loyalty Segmentation - K-Means Clustering Engine
Unsupervised machine learning clusterer with log transformation,
feature scaling, elbow curve & silhouette score analysis, and automated segment profiling.
"""

import json
import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score


class AccorKMeansClusterer:
    """
    K-Means clustering pipeline customized for hospitality loyalty data.
    """
    def __init__(self, n_clusters: int = 5, random_state: int = 42):
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=self.random_state, n_init=15)
        self.feature_columns = [
            "recency_days", 
            "frequency_stays", 
            "monetary_spend_eur",
            "avg_daily_rate_adr",
            "direct_channel_ratio"
        ]
        self.cluster_labels_map: Dict[int, str] = {}
        self.cluster_summary: Optional[pd.DataFrame] = None
        
    def _transform_features(self, df: pd.DataFrame, fit_scaler: bool = True) -> np.ndarray:
        """
        Applies log1p transformation to skewed metrics and standardizes features.
        """
        X = df[self.feature_columns].copy()
        
        # Log-transform skewed monetary and frequency features
        X["monetary_spend_eur"] = np.log1p(np.maximum(0, X["monetary_spend_eur"]))
        X["frequency_stays"] = np.log1p(np.maximum(0, X["frequency_stays"]))
        X["avg_daily_rate_adr"] = np.log1p(np.maximum(0, X["avg_daily_rate_adr"]))
        # Recency log transform helps compress large dormancy gaps
        X["recency_days"] = np.log1p(np.maximum(0, X["recency_days"]))
        
        if fit_scaler:
            return self.scaler.fit_transform(X)
        return self.scaler.transform(X)
        
    def evaluate_optimal_k(self, df: pd.DataFrame, k_range: range = range(3, 8)) -> Dict[str, List]:
        """
        Evaluates cluster quality across multiple k values using Inertia and Silhouette Score.
        """
        X_scaled = self._transform_features(df, fit_scaler=True)
        results = {"k": [], "inertia": [], "silhouette": []}
        
        print("\n--- K-Means Optimal K Evaluation (Elbow & Silhouette) ---")
        for k in k_range:
            km = KMeans(n_clusters=k, random_state=self.random_state, n_init=10)
            cluster_preds = km.fit_predict(X_scaled)
            inertia = km.inertia_
            sil = silhouette_score(X_scaled, cluster_preds, sample_size=min(3000, len(X_scaled)), random_state=self.random_state)
            
            results["k"].append(k)
            results["inertia"].append(round(inertia, 2))
            results["silhouette"].append(round(sil, 4))
            print(f"  k={k}: Inertia = {inertia:10.2f} | Silhouette Score = {sil:.4f}")
            
        return results

    def fit_predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fits K-Means, profiles cluster centroids, labels semantic segments,
        and returns the enriched dataframe.
        """
        df_clustered = df.copy()
        X_scaled = self._transform_features(df_clustered, fit_scaler=True)
        
        cluster_ids = self.kmeans.fit_predict(X_scaled)
        df_clustered["kmeans_cluster"] = cluster_ids
        
        # Profile cluster means to understand properties of each cluster
        profile = df_clustered.groupby("kmeans_cluster").agg(
            member_count=("member_id", "count"),
            mean_recency=("recency_days", "mean"),
            mean_frequency=("frequency_stays", "mean"),
            mean_spend=("monetary_spend_eur", "mean"),
            mean_adr=("avg_daily_rate_adr", "mean"),
            mean_direct_ratio=("direct_channel_ratio", "mean"),
            churn_rate=("is_churned", "mean") if "is_churned" in df_clustered.columns else ("recency_days", lambda x: (x > 365).mean())
        ).reset_index()
        
        # Interpret and map semantic business segment names
        # Order clusters by monetary spend and recency
        self._map_semantic_labels(profile)
        
        df_clustered["kmeans_segment"] = df_clustered["kmeans_cluster"].map(self.cluster_labels_map)
        profile["kmeans_segment"] = profile["kmeans_cluster"].map(self.cluster_labels_map)
        self.cluster_summary = profile
        
        print("\n--- K-Means Cluster Centroids & Profiles ---")
        for _, row in profile.iterrows():
            print(
                f"Cluster {int(row['kmeans_cluster'])} [{row['kmeans_segment']}]: "
                f"Count={int(row['member_count']):,}, "
                f"Avg Recency={row['mean_recency']:.1f}d, "
                f"Avg Freq={row['mean_frequency']:.1f} stays, "
                f"Avg Spend=EUR {row['mean_spend']:,.0f}, "
                f"Avg ADR=EUR {row['mean_adr']:.0f}, "
                f"Direct%={row['mean_direct_ratio']*100:.1f}%, "
                f"Churn Rate={row['churn_rate']*100:.1f}%"
            )
            
        return df_clustered

    def _map_semantic_labels(self, profile: pd.DataFrame):
        """
        Heuristic semantic assignment based on centroid characteristics.
        """
        labels = {}
        # Sort indices by spend and recency
        # High spend, low recency -> High-Value Champions
        # High recency (> 300) -> Dormant / Churned
        # High spend, high recency -> At-Risk High-Spenders
        # Moderate spend, moderate recency, high frequency -> Loyal Mainstays
        # Low spend, moderate recency -> Value Seekers
        
        clusters = profile.to_dict("records")
        assigned = set()
        
        # 1. Dormant: Highest recency
        dormant_cand = max(clusters, key=lambda c: c["mean_recency"])
        labels[dormant_cand["kmeans_cluster"]] = "Dormant / Churned"
        assigned.add(dormant_cand["kmeans_cluster"])
        
        # 2. High-Value Champions: Highest spend among remaining with low recency (< 150)
        remaining = [c for c in clusters if c["kmeans_cluster"] not in assigned]
        champs_cand = max(remaining, key=lambda c: c["mean_spend"])
        labels[champs_cand["kmeans_cluster"]] = "High-Value Champions"
        assigned.add(champs_cand["kmeans_cluster"])
        
        # 3. At-Risk High-Spenders: High recency (> 180) or highest churn rate among remaining
        remaining = [c for c in clusters if c["kmeans_cluster"] not in assigned]
        if remaining:
            at_risk_cand = max(remaining, key=lambda c: c["mean_recency"] * (c["mean_spend"] ** 0.5))
            labels[at_risk_cand["kmeans_cluster"]] = "At-Risk High-Spenders"
            assigned.add(at_risk_cand["kmeans_cluster"])
            
        # 4. Loyal Mainstays vs Value Seekers among remaining
        remaining = [c for c in clusters if c["kmeans_cluster"] not in assigned]
        if len(remaining) >= 2:
            mainstay_cand = max(remaining, key=lambda c: c["mean_frequency"])
            labels[mainstay_cand["kmeans_cluster"]] = "Loyal Mainstays"
            assigned.add(mainstay_cand["kmeans_cluster"])
            
            value_cand = [c for c in clusters if c["kmeans_cluster"] not in assigned][0]
            labels[value_cand["kmeans_cluster"]] = "Value Seekers"
            assigned.add(value_cand["kmeans_cluster"])
        elif len(remaining) == 1:
            labels[remaining[0]["kmeans_cluster"]] = "Loyal Mainstays"
            
        self.cluster_labels_map = labels

    def save(self, filepath: str = "data/processed/kmeans_model.joblib"):
        """
        Persist trained K-Means model, scaler, and label mapping.
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        bundle = {
            "kmeans": self.kmeans,
            "scaler": self.scaler,
            "feature_columns": self.feature_columns,
            "cluster_labels_map": self.cluster_labels_map,
            "cluster_summary": self.cluster_summary.to_dict("records") if self.cluster_summary is not None else None
        }
        joblib.dump(bundle, filepath)
        print(f"[+] K-Means model successfully saved to {filepath}")
