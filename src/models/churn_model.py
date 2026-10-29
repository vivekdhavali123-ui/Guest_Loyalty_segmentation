"""
Accor Loyalty Platform - Churn Prediction Pipeline
Trains, compares, and evaluates Scikit-Learn (Random Forest) and XGBoost models.
Generates 0-100 Customer Risk Scores and Churn Risk Tiers.
"""

import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Tuple, Any

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)
import xgboost as xgb


class AccorChurnModelPipeline:
    """
    End-to-end churn model trainer, evaluator, and risk scoring engine.
    """
    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.models: Dict[str, Any] = {}
        self.evaluations: Dict[str, Dict[str, float]] = {}
        self.best_model_name: str = ""
        self.best_model: Any = None
        self.feature_names: list = []
        
    def train_and_evaluate(
        self, 
        X: pd.DataFrame, 
        y: pd.Series, 
        test_size: float = 0.20
    ) -> Dict[str, Dict[str, float]]:
        """
        Splits data, trains Scikit-Learn and XGBoost models, and generates comparative metrics.
        """
        self.feature_names = list(X.columns)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.random_state, stratify=y
        )
        
        print(f"\n[*] Training churn models on {len(X_train):,} samples, testing on {len(X_test):,} samples...")
        churn_rate_train = y_train.mean() * 100
        print(f"[*] Training baseline churn prevalence: {churn_rate_train:.2f}%")
        
        # 1. Scikit-Learn Random Forest
        print("\n--- Model 1: Scikit-Learn Random Forest Classifier ---")
        rf = RandomForestClassifier(
            n_estimators=150,
            max_depth=12,
            min_samples_split=6,
            min_samples_leaf=3,
            class_weight="balanced",
            random_state=self.random_state,
            n_jobs=-1
        )
        rf.fit(X_train, y_train)
        self.models["RandomForest"] = rf
        self.evaluations["RandomForest"] = self._evaluate_model(rf, X_test, y_test, "RandomForest")
        
        # 2. XGBoost Classifier
        print("\n--- Model 2: XGBoost Classifier (Gradient Boosting) ---")
        scale_pos = (len(y_train) - sum(y_train)) / max(1, sum(y_train))
        xgb_model = xgb.XGBClassifier(
            n_estimators=180,
            max_depth=6,
            learning_rate=0.06,
            subsample=0.85,
            colsample_bytree=0.80,
            scale_pos_weight=scale_pos,
            random_state=self.random_state,
            eval_metric="logloss",
            n_jobs=-1
        )
        xgb_model.fit(X_train, y_train)
        self.models["XGBoost"] = xgb_model
        self.evaluations["XGBoost"] = self._evaluate_model(xgb_model, X_test, y_test, "XGBoost")
        
        # 3. Select Best Model based on ROC-AUC
        if self.evaluations["XGBoost"]["roc_auc"] >= self.evaluations["RandomForest"]["roc_auc"]:
            self.best_model_name = "XGBoost"
            self.best_model = self.models["XGBoost"]
        else:
            self.best_model_name = "RandomForest"
            self.best_model = self.models["RandomForest"]
            
        print(f"\n[CHAMPION] Churn Model Selected: {self.best_model_name} (ROC-AUC: {self.evaluations[self.best_model_name]['roc_auc']:.4f})")
        return self.evaluations

    def _evaluate_model(self, model: Any, X_test: pd.DataFrame, y_test: pd.Series, name: str) -> Dict[str, float]:
        """
        Computes ROC-AUC, PR-AUC, F1, Precision, Recall, and displays matrix.
        """
        y_prob = model.predict_proba(X_test)[:, 1]
        y_pred = (y_prob >= 0.50).astype(int)
        
        roc_auc = roc_auc_score(y_test, y_prob)
        pr_auc = average_precision_score(y_test, y_prob)
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        cm = confusion_matrix(y_test, y_pred)
        
        print(f"  Accuracy:          {acc*100:.2f}%")
        print(f"  ROC-AUC Score:     {roc_auc:.4f}")
        print(f"  PR-AUC Score:      {pr_auc:.4f}")
        print(f"  Precision:         {prec:.4f}")
        print(f"  Recall:            {rec:.4f}")
        print(f"  F1-Score:          {f1:.4f}")
        print(f"  Confusion Matrix:  TN={cm[0,0]}, FP={cm[0,1]}, FN={cm[1,0]}, TP={cm[1,1]}")
        
        return {
            "accuracy": round(acc, 4),
            "roc_auc": round(roc_auc, 4),
            "pr_auc": round(pr_auc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "confusion_matrix": cm.tolist()
        }

    def predict_risk_scores(self, df_original: pd.DataFrame, X: pd.DataFrame) -> pd.DataFrame:
        """
        Attaches churn probability, calibrated 0-100 Risk Score, and Risk Tier
        to the input loyalty members dataframe.
        """
        df_scored = df_original.copy()
        
        # Predict using champion model
        y_prob = self.best_model.predict_proba(X)[:, 1]
        
        # Calibrated 0-100 score
        risk_score = np.round(y_prob * 100, 1)
        
        df_scored["churn_probability"] = np.round(y_prob, 4)
        df_scored["churn_risk_score"] = risk_score
        
        # Categorical Risk Tiers
        conditions = [
            df_scored["churn_risk_score"] >= 70.0,
            (df_scored["churn_risk_score"] >= 35.0) & (df_scored["churn_risk_score"] < 70.0),
            df_scored["churn_risk_score"] < 35.0
        ]
        tier_names = ["High Risk", "Medium Risk", "Low Risk"]
        df_scored["churn_risk_tier"] = np.select(conditions, tier_names, default="Low Risk")
        
        print("\n--- Churn Risk Tier Distribution ---")
        risk_counts = df_scored["churn_risk_tier"].value_counts()
        for tier, count in risk_counts.items():
            pct = (count / len(df_scored)) * 100
            print(f"  {tier:<14}: {pct:5.2f}% ({count:,} members)")
            
        return df_scored

    def save(self, filepath: str = "data/processed/churn_model_champion.joblib"):
        """
        Saves the best model, feature names, and performance metrics.
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        bundle = {
            "best_model_name": self.best_model_name,
            "model": self.best_model,
            "feature_names": self.feature_names,
            "evaluations": self.evaluations
        }
        joblib.dump(bundle, filepath)
        print(f"[+] Champion model ({self.best_model_name}) saved to {filepath}")
