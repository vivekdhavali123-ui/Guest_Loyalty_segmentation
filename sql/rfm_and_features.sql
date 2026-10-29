-- ============================================================================
-- Accor Live Limitless (ALL) Loyalty Platform
-- Analytical SQL: RFM Extraction, Hospitality Feature Engineering & Churn Flagging
-- ============================================================================

-- 1. Common Table Expression (CTE): Completed Stay Aggregations per Member
WITH member_stay_stats AS (
    SELECT 
        b.member_id,
        -- Recency metrics (using snapshot date '2026-10-25')
        MAX(b.checkout_date) AS last_stay_date,
        MIN(b.checkin_date) AS first_stay_date,
        CAST(ROUND(JULIANDAY('2026-10-25') - JULIANDAY(MAX(b.checkout_date))) AS INTEGER) AS recency_days,
        
        -- Frequency metrics
        COUNT(CASE WHEN b.booking_status = 'Completed' THEN 1 END) AS total_completed_stays,
        SUM(CASE WHEN b.booking_status = 'Completed' THEN b.nights ELSE 0 END) AS total_room_nights,
        COUNT(b.booking_id) AS total_bookings_made,
        COUNT(CASE WHEN b.booking_status = 'Cancelled' THEN 1 END) AS total_cancellations,
        
        -- Monetary metrics (EUR)
        SUM(CASE WHEN b.booking_status = 'Completed' THEN b.total_spend_eur ELSE 0 END) AS total_spend_eur,
        SUM(CASE WHEN b.booking_status = 'Completed' THEN b.room_revenue_eur ELSE 0 END) AS total_room_revenue_eur,
        SUM(CASE WHEN b.booking_status = 'Completed' THEN b.ancillary_revenue_eur ELSE 0 END) AS total_ancillary_spend_eur,
        
        -- Hospitality Behavioral KPIs
        AVG(CASE WHEN b.booking_status = 'Completed' THEN b.nights ELSE NULL END) AS avg_length_of_stay,
        AVG(CASE WHEN b.booking_status = 'Completed' THEN (b.room_revenue_eur / NULLIF(b.nights, 0)) ELSE NULL END) AS avg_daily_rate_adr,
        AVG(b.lead_time_days) AS avg_booking_lead_time,
        
        -- Channel & Brand Behavior
        1.0 * SUM(CASE WHEN b.booking_channel IN ('ALL_Direct_App', 'ALL_Direct_Web') THEN 1 ELSE 0 END) / COUNT(b.booking_id) AS direct_channel_ratio,
        COUNT(DISTINCT p.brand_code) AS distinct_brands_stayed,
        COUNT(DISTINCT p.property_id) AS distinct_properties_stayed,
        1.0 * SUM(CASE WHEN p.brand_segment IN ('Luxury', 'Premium') AND b.booking_status = 'Completed' THEN 1 ELSE 0 END) / 
            NULLIF(COUNT(CASE WHEN b.booking_status = 'Completed' THEN 1 END), 0) AS luxury_premium_ratio,
            
        -- Loyalty Engagement & Service Experience
        SUM(b.points_earned) AS total_points_earned,
        SUM(b.points_redeemed) AS total_points_redeemed,
        AVG(b.guest_satisfaction_score) AS avg_satisfaction_score,
        SUM(CASE WHEN b.has_service_complaint = 1 THEN 1 ELSE 0 END) AS total_complaints
    FROM bookings b
    JOIN properties p ON b.property_id = p.property_id
    GROUP BY b.member_id
),

-- 2. Member Profile Merged with Behavioral Metrics
member_enriched AS (
    SELECT 
        m.member_id,
        m.first_name || ' ' || m.last_name AS member_full_name,
        m.email,
        m.current_tier,
        m.reward_points_balance,
        m.status_points,
        m.country_of_residence,
        m.primary_travel_purpose,
        m.app_installed,
        m.email_subscribed,
        CAST(ROUND(JULIANDAY('2026-10-25') - JULIANDAY(m.enrollment_date)) AS INTEGER) AS tenure_days,
        
        -- RFM Core
        COALESCE(s.recency_days, 730) AS recency_days,
        COALESCE(s.total_completed_stays, 0) AS frequency_stays,
        COALESCE(s.total_spend_eur, 0.0) AS monetary_spend_eur,
        
        -- Additional Features
        COALESCE(s.total_room_nights, 0) AS total_room_nights,
        COALESCE(s.avg_length_of_stay, 0.0) AS avg_length_of_stay,
        COALESCE(s.avg_daily_rate_adr, 0.0) AS avg_daily_rate_adr,
        COALESCE(s.total_ancillary_spend_eur, 0.0) AS total_ancillary_spend_eur,
        COALESCE(s.avg_booking_lead_time, 0.0) AS avg_booking_lead_time,
        COALESCE(s.direct_channel_ratio, 0.0) AS direct_channel_ratio,
        COALESCE(s.distinct_brands_stayed, 0) AS distinct_brands_stayed,
        COALESCE(s.distinct_properties_stayed, 0) AS distinct_properties_stayed,
        COALESCE(s.luxury_premium_ratio, 0.0) AS luxury_premium_ratio,
        COALESCE(1.0 * s.total_cancellations / NULLIF(s.total_bookings_made, 0), 0.0) AS cancellation_rate,
        COALESCE(s.avg_satisfaction_score, 7.5) AS avg_satisfaction_score,
        COALESCE(s.total_complaints, 0) AS total_complaints,
        COALESCE(1.0 * s.total_points_redeemed / NULLIF(s.total_points_earned, 0), 0.0) AS points_redemption_rate
    FROM loyalty_members m
    LEFT JOIN member_stay_stats s ON m.member_id = s.member_id
),

-- 3. Quintile Scoring for RFM (1 to 5)
rfm_scored AS (
    SELECT 
        e.*,
        -- R_Score: Lower recency days = higher score (5 = most recent, 1 = least recent)
        6 - NTILE(5) OVER (ORDER BY e.recency_days ASC) AS r_score,
        -- F_Score: Higher stays = higher score (5 = highest frequency)
        NTILE(5) OVER (ORDER BY e.frequency_stays ASC) AS f_score,
        -- M_Score: Higher spend = higher score (5 = highest monetary)
        NTILE(5) OVER (ORDER BY e.monetary_spend_eur ASC) AS m_score
    FROM member_enriched e
)

-- 4. Final Output: RFM Cells & Business Ground Truth Churn Flag
SELECT 
    r.*,
    CAST(r.r_score AS VARCHAR) || CAST(r.f_score AS VARCHAR) || CAST(r.m_score AS VARCHAR) AS rfm_cell,
    (r.r_score + r.f_score + r.m_score) / 3.0 AS rfm_composite_score,
    
    -- Ground Truth Churn Definition in Hospitality:
    -- Inactive for > 365 days OR (recency > 270 days with high cancellation rate > 35%)
    CASE 
        WHEN r.recency_days > 365 THEN 1
        WHEN r.recency_days > 270 AND r.cancellation_rate > 0.35 THEN 1
        WHEN r.recency_days > 210 AND r.total_complaints >= 2 AND r.avg_satisfaction_score < 6.0 THEN 1
        ELSE 0
    END AS is_churned
FROM rfm_scored r;
