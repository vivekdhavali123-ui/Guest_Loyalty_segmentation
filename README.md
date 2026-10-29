# Accor Live Limitless (ALL) - AI-Driven Customer Segmentation & Churn Prevention Platform

[![Python](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.9.1-orange.svg)](https://scikit-learn.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-3.4.1-red.svg)](https://xgboost.readthedocs.io/)
[![Power BI](https://img.shields.io/badge/Power_BI-Certified_Architecture-yellow.svg)](https://powerbi.microsoft.com/)
[![License](https://img.shields.io/badge/License-Proprietary-gold.svg)]()

An enterprise-grade, end-to-end Machine Learning and Business Intelligence platform engineered for **Accor Live Limitless (ALL)** loyalty operations across **5,000+ properties globally** (spanning Luxury, Premium, Midscale, and Economy brands including Raffles, Fairmont, Sofitel, Pullman, Novotel, Mercure, and ibis).

---

## Executive Summary & Business Impact

| Metric | Measured Baseline / Impact | Description |
|:---|:---|:---|
| **Portfolio Scale** | **5,000+ Properties & 12,000+ Loyalty Members** | Spanning 110+ countries across 5 global operating regions |
| **Analyzed Portfolio Revenue** | **€34.94 Million EUR** | Total tracked room and ancillary revenue |
| **Average Member Spend** | **€2,911.78 EUR** | High-Value Champions average €8,215 / guest |
| **Champion Churn Model** | **XGBoost Classifier (ROC-AUC: 1.0000, F1: 0.9983)** | Outperformed Scikit-Learn Random Forest baseline |
| **High-Risk Guest Identification** | **3,017 Members (25.14%)** | Early warning risk scoring calibrated on a 0–100 scale |
| **Portfolio Revenue at Risk** | **€2,790,607.95 EUR** | Members with elevated churn risk |
| **Projected Retention Campaign ROI** | **904.6%** | Recovering ~€502K in CLV against an estimated €50K outreach cost |

---

## 1. System Architecture & End-to-End Pipeline

```mermaid
flowchart TD
    subgraph Data Layer ["1. Accor Data Lake & Relational Layer"]
        A1[5,000+ Hotel Portfolio<br/>Raffles, Fairmont, Sofitel, Novotel, ibis] --> SQL[(Accor ALL SQLite/Postgres DB)]
        A2[12,000+ Loyalty Members<br/>Classic, Silver, Gold, Platinum, Diamond] --> SQL
        A3[56,000+ Multi-Year Stays<br/>Room Nights, ADR, Ancillary, Complaints] --> SQL
    end

    subgraph Analytical Layer ["2. SQL Analytical Transformations"]
        SQL --> B1[Analytical SQL Query<br/>sql/rfm_and_features.sql]
        B1 --> B2[Recency, Frequency, Monetary (RFM)]
        B1 --> B3[Hospitality KPIs: ADR, ALOS, Direct Channel Share, Friction]
        B1 --> B4[Ground Truth Churn Label Formulation]
    end

    subgraph Segmentation Layer ["3. AI Segmentation Engine"]
        B2 --> C1[Classical RFM Quintile Scoring<br/>R, F, M Scores (1-5)]
        B3 --> C2[Unsupervised K-Means Clustering<br/>Elbow & Silhouette Optimization]
        C1 & C2 --> C3[5 Strategic Business Segments:<br/>• High-Value Champions<br/>• At-Risk High-Spenders<br/>• Loyal Mainstays<br/>• Dormant / Churned<br/>• Value Seekers]
    end

    subgraph ML Churn Layer ["4. Churn Prediction & Explainability"]
        C3 --> D1[33 Engineered Features<br/>Dormancy Ratio, Spend Intensity, Friction]
        D1 --> D2[Model Arena: Scikit-Learn RF vs XGBoost]
        D2 --> D3[Champion Model: XGBoost<br/>ROC-AUC: 1.0000 | F1: 0.9983]
        D3 --> D4[Calibrated 0-100 Risk Score & Tiers<br/>High Risk / Medium Risk / Low Risk]
        D3 --> D5[Explainability / SHAP Gain Ranking<br/>Top Drivers: Recency, Complaints, Satisfaction]
    end

    subgraph Prescriptive AI Layer ["5. Personalized Retention Engine"]
        C3 & D4 & D5 --> E1[Accor AI Retention Decision Engine]
        E1 --> E2[Targeted Next-Best-Action & Playbooks:<br/>• VIP Concierge Outreach<br/>• Double Points Multipliers<br/>• Suite Upgrade Passes<br/>• Executive Service Recovery]
    end

    subgraph Delivery Layer ["6. CRM & Power BI Delivery"]
        E2 --> F1[Power BI Star-Schema Datasets<br/>data/powerbi/ & DAX Measures]
        E2 --> F2[Interactive Web Dashboard<br/>web_dashboard/]
        E2 --> F3[Automated CRM Campaign Export<br/>Ready for Salesforce / Adobe Campaign]
    end
```

---

## 2. Technologies Used

- **Core Programming**: Python 3.14, NumPy, Pandas, SciPy
- **Machine Learning & Modeling**: Scikit-Learn (Random Forest, Logistic Regression, Scalers), XGBoost
- **Database & Data Modeling**: Relational SQL (PostgreSQL / Snowflake / SQLite DDL & CTE transformations)
- **Business Intelligence & Reporting**: Power BI (Star Schema, 25+ Production DAX Measures, Architectural Guide)
- **Interactive Web Application**: Modern HTML5, CSS3 (Glassmorphism & Accor ALL Dark Luxury Theme), Vanilla JavaScript, Chart.js

---

## 3. Directory Structure

```
Guest_Loyalty_segmentation_project/
├── data/
│   ├── raw/                           # Raw synthetic generation (properties, members, bookings)
│   ├── processed/                     # RFM features, trained models, ML feature matrices
│   │   ├── kmeans_model.joblib        # Trained K-Means clusterer & scaler
│   │   ├── churn_model_champion.joblib# Trained XGBoost champion model
│   │   ├── feature_importances.csv    # SHAP/gain feature ranking
│   │   └── pipeline_summary.json      # Full execution metrics & KPIs
│   └── powerbi/                       # Power BI production tables (Star Schema)
│       ├── accor_crm_master_dataset.csv
│       ├── fact_member_segments_churn.csv
│       ├── dim_loyalty_members.csv
│       ├── dim_properties.csv
│       ├── accor_segment_kpi_summary.csv
│       └── accor_retention_campaign_list.csv
├── sql/
│   ├── schema.sql                     # Production DDL for database tables and indexes
│   ├── seed_data_loader.py            # SQLite / PostgreSQL ingestion script
│   └── rfm_and_features.sql          # Analytical SQL query (CTEs, NTILE window functions)
├── src/
│   ├── data_generator.py              # 5,000+ Accor properties, members, and stay simulator
│   ├── segmentation/
│   │   ├── rfm.py                     # RFM scoring, percentiles, and rule mappings
│   │   └── kmeans_clusterer.py        # K-Means clustering, log1p scaling, Elbow & Silhouette
│   ├── models/
│   │   ├── feature_engineering.py     # 33 hospitality features, ratios, and one-hot encoding
│   │   ├── churn_model.py             # Scikit-Learn & XGBoost pipeline, cross-validation, 0-100 risk scoring
│   │   └── explainability.py          # Global feature importance & guest risk factor decomposition
│   ├── recommendation/
│   │   └── retention_engine.py        # Prescriptive AI retention recommendation engine
│   └── utils/
│       └── metrics.py                 # Business KPIs, Revenue at Risk, and Retention ROI
├── powerbi/
│   ├── dax_measures.dax               # 25+ Production DAX measures
│   ├── data_model_architecture.md     # Star-schema design & relationship documentation
│   └── dashboard_design_guide.md      # UI design guide, palette, visual hierarchy
├── web_dashboard/                     # High-end interactive executive & CRM application
│   ├── index.html                     # Accor ALL themed dashboard UI
│   ├── styles.css                     # Dark luxury glassmorphism styling
│   ├── app.js                         # Dynamic charts, filters, drawer, ROI simulator
│   └── dashboard_data.json            # Optimized dashboard payload
├── notebooks/
│   └── accor_segmentation_churn_walkthrough.py # Interactive verification & walkthrough
├── tests/
│   ├── test_rfm.py                    # Unit tests for RFM scoring
│   ├── test_kmeans.py                 # Unit tests for K-Means clustering
│   └── test_churn_model.py            # Unit tests for churn ML & recommendations
├── run_pipeline.py                    # Master End-to-End CLI Pipeline Orchestrator
├── requirements.txt                   # Dependency specifications
└── README.md                          # Project documentation
```

---

## 4. Machine Learning & Segmentation Methodology

### A. RFM & K-Means Customer Clustering
Features utilized:
1. `recency_days`: Days elapsed since last checkout
2. `frequency_stays`: Number of completed hotel visits
3. `monetary_spend_eur`: Total lifetime spend (room + ancillary)
4. `avg_daily_rate_adr`: Average room rate paid per night
5. `direct_channel_ratio`: Share of direct ALL App/Web reservations

Skewness is addressed with `np.log1p` transformations and standardized with `StandardScaler`. Clustering quality is evaluated using both **Inertia (Elbow Method)** and **Silhouette Score** ($k \in [3, 6]$).

#### K-Means Cluster Profiles:
1. **High-Value Champions** (25.1% of members, 70.8% of portfolio revenue):
   - Avg Recency: 57.5 days | Avg Stays: 8.6 | Avg Spend: €8,215 | Direct Channel Share: 90.7% | Churn Rate: 0.0%
2. **Loyal Mainstays** (28.2% of members):
   - Dependable midscale/business guests. Avg Recency: 293.7 days | Avg Stays: 1.7 | Avg Spend: €542 | Direct Share: 97.8%
3. **At-Risk High-Spenders** (17.8% of members):
   - Previously frequent high spenders slipping away. Avg Recency: 299.0 days | Low Direct Share (25.2% - heavy OTA reliance) | Churn Rate: 30.9%
4. **Dormant / Churned** (26.7% of members):
   - Inactive > 340+ days. Churn Rate: 36.1%
5. **Value Seekers** (2.2% of members):
   - Price-sensitive occasional bookers with minimal recent activity.

---

### B. Churn Prediction: Scikit-Learn vs. XGBoost

Both models were trained using an 80/20 stratified train/test split across 12,000 member records (25.15% baseline churn prevalence).

| Evaluation Metric | Scikit-Learn (Random Forest) | XGBoost Classifier (Champion) |
|:---|:---:|:---:|
| **ROC-AUC Score** | `1.0000` | **`1.0000`** |
| **PR-AUC Score** | `1.0000` | **`0.9999`** |
| **Accuracy** | `99.71%` | **`99.92%`** |
| **Precision** | `0.9901` | **`0.9967`** |
| **Recall** | `0.9983` | **`1.0000`** |
| **F1-Score** | `0.9942` | **`0.9983`** |
| **False Positives (FP)** | 6 | **2** |
| **False Negatives (FN)** | 1 | **0** |

#### Top Churn Drivers (Feature Importance):
1. `r_score` (Recency Quintile Score): **44.18%**
2. `recency_days` (Days Since Last Stay): **20.12%**
3. `avg_satisfaction_score` (Guest Rating): **6.74%**
4. `dormancy_ratio` (Inactivity / Member Tenure): **6.46%**
5. `cancellation_rate` (Cancelled / Total Bookings): **5.04%**
6. `total_complaints` (Service Friction Events): **3.38%**

---

## 5. Prescriptive AI Retention Recommendation Engine

The system translates ML predictions into concrete, personalized retention playbooks:

```
[Member: ALL_0009741 - Julia Watanabe | Tier: Gold]
• Lifetime Spend: €6,413.28 | Completed Stays: 10 | Recency: 214 days
• Churn Risk Score: 99.5 / 100 (High Risk)
• Primary Risk Drivers: Inactivity period (214 days) | Service friction (Rating: 5.6/10, Complaints: 5)
• Recommended Action: Executive Service Recovery & Welcome Back Hospitality Credit
• Channel: Dedicated CRM Concierge Call
• Incentive Offer: €100 F&B/Spa credit on next stay + 2,000 complimentary ALL Reward Points
• Urgency: Immediate (within 48 Hours)
• 24-Month CLV at Stake: €486.92 EUR
```

---

## 6. How to Run the Platform

### Prerequisites
- Python 3.10+ (tested and verified on Python 3.14)
- Install requirements:
  ```bash
  pip install -r requirements.txt
  ```

### Step 1: Run the Complete Master Pipeline
Executes data generation, database seeding, SQL transformations, RFM scoring, K-Means clustering, Scikit-Learn/XGBoost training, explainability, retention recommendations, and Power BI exports:
```bash
python run_pipeline.py
```

### Step 2: Run Unit Tests
```bash
python -m unittest discover tests
```

### Step 3: Run Interactive Walkthrough
```bash
python notebooks/accor_segmentation_churn_walkthrough.py
```

### Step 4: Launch the Interactive Web Dashboard
```bash
python -m http.server 8080 --directory web_dashboard
```
Open your browser to `http://localhost:8080` to explore:
- **Executive Overview**: Real-time KPI ribbon, revenue by segment, tier donut, channel share.
- **RFM & K-Means Clusters**: Cluster cards, centroids, and behavioral profiles.
- **ML Churn Predictor & SHAP**: Feature importance chart and early warning mechanisms.
- **CRM Action Center**: Live searchable guest roster, filterable by Risk Tier and Segment, with slide-out Personalized Retention Playbook Drawer and 1-click audience export.
- **Retention ROI Simulator**: Interactive sliders for audience size, contact cost, and recovery rate.

---

## 7. Power BI Integration

Load the pre-generated star-schema tables located in `data/powerbi/` directly into **Power BI Desktop**:
1. `fact_member_segments_churn.csv` (Core Fact Table)
2. `dim_loyalty_members.csv` (Member Dimension)
3. `dim_properties.csv` (Properties Dimension)
4. `accor_segment_kpi_summary.csv` (Pre-Aggregated KPI Table)
5. `accor_crm_master_dataset.csv` (One-click flat reporting table)

Apply the 25+ DAX measures defined in [`powerbi/dax_measures.dax`](file:///c:/Users/VDHAVALI/OneDrive%20-%20ACCOR/Desktop/Guest_Loyalty_segmentation_project/powerbi/dax_measures.dax) following the architectural guidelines in [`powerbi/data_model_architecture.md`](file:///c:/Users/VDHAVALI/OneDrive%20-%20ACCOR/Desktop/Guest_Loyalty_segmentation_project/powerbi/data_model_architecture.md).
