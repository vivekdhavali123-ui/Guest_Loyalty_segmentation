-- ============================================================================
-- Accor Live Limitless (ALL) Loyalty & Guest Segmentation Platform
-- Enterprise Relational Schema (PostgreSQL / Snowflake / SQLite Compatible)
-- Across 5,000+ Global Properties
-- ============================================================================

-- Table 1: Properties Portfolio (Accor 5,000+ Hotel Footprint)
CREATE TABLE IF NOT EXISTS properties (
    property_id VARCHAR(32) PRIMARY KEY,
    property_name VARCHAR(150) NOT NULL,
    brand_code VARCHAR(20) NOT NULL,
    brand_name VARCHAR(50) NOT NULL,
    brand_segment VARCHAR(30) NOT NULL, -- 'Luxury', 'Premium', 'Midscale', 'Economy'
    country_code VARCHAR(3) NOT NULL,
    city VARCHAR(80) NOT NULL,
    region VARCHAR(30) NOT NULL,        -- 'Europe', 'North America', 'Asia Pacific', 'Middle East & Africa', 'Latin America'
    room_count INTEGER NOT NULL,
    average_base_adr_eur NUMERIC(10, 2) NOT NULL,
    has_spa_facility BOOLEAN DEFAULT FALSE,
    has_fine_dining BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_properties_brand_segment ON properties(brand_segment);
CREATE INDEX IF NOT EXISTS idx_properties_region ON properties(region);

-- Table 2: Loyalty Members (ALL - Accor Live Limitless)
CREATE TABLE IF NOT EXISTS loyalty_members (
    member_id VARCHAR(32) PRIMARY KEY,
    first_name VARCHAR(60) NOT NULL,
    last_name VARCHAR(60) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    enrollment_date DATE NOT NULL,
    current_tier VARCHAR(20) NOT NULL, -- 'Classic', 'Silver', 'Gold', 'Platinum', 'Diamond'
    status_points INTEGER DEFAULT 0,
    reward_points_balance INTEGER DEFAULT 0,
    country_of_residence VARCHAR(3) NOT NULL,
    primary_travel_purpose VARCHAR(20) DEFAULT 'Leisure', -- 'Leisure', 'Business', 'Bleisure'
    app_installed BOOLEAN DEFAULT TRUE,
    email_subscribed BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_members_tier ON loyalty_members(current_tier);
CREATE INDEX IF NOT EXISTS idx_members_country ON loyalty_members(country_of_residence);

-- Table 3: Bookings & Stays Record
CREATE TABLE IF NOT EXISTS bookings (
    booking_id VARCHAR(36) PRIMARY KEY,
    member_id VARCHAR(32) NOT NULL,
    property_id VARCHAR(32) NOT NULL,
    booking_date DATE NOT NULL,
    checkin_date DATE NOT NULL,
    checkout_date DATE NOT NULL,
    nights INTEGER NOT NULL CHECK (nights > 0),
    rooms INTEGER DEFAULT 1,
    booking_channel VARCHAR(30) NOT NULL, -- 'ALL_Direct_App', 'ALL_Direct_Web', 'Corporate_GDS', 'OTA_Booking', 'OTA_Expedia'
    booking_status VARCHAR(20) NOT NULL,  -- 'Completed', 'Cancelled', 'NoShow'
    lead_time_days INTEGER NOT NULL,
    room_revenue_eur NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    ancillary_revenue_eur NUMERIC(10, 2) NOT NULL DEFAULT 0.00, -- F&B, Spa, Services
    total_spend_eur NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    points_earned INTEGER DEFAULT 0,
    points_redeemed INTEGER DEFAULT 0,
    guest_satisfaction_score INTEGER, -- 1 to 10
    has_service_complaint BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (member_id) REFERENCES loyalty_members(member_id),
    FOREIGN KEY (property_id) REFERENCES properties(property_id)
);

CREATE INDEX IF NOT EXISTS idx_bookings_member ON bookings(member_id);
CREATE INDEX IF NOT EXISTS idx_bookings_property ON bookings(property_id);
CREATE INDEX IF NOT EXISTS idx_bookings_checkout ON bookings(checkout_date);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(booking_status);

-- Table 4: CRM Campaign Interactions & Feedback
CREATE TABLE IF NOT EXISTS campaign_interactions (
    interaction_id VARCHAR(36) PRIMARY KEY,
    member_id VARCHAR(32) NOT NULL,
    campaign_name VARCHAR(100) NOT NULL,
    campaign_channel VARCHAR(30) NOT NULL, -- 'Email', 'App_Push', 'SMS', 'Concierge_Call'
    sent_date DATE NOT NULL,
    opened BOOLEAN DEFAULT FALSE,
    clicked BOOLEAN DEFAULT FALSE,
    converted_booking BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (member_id) REFERENCES loyalty_members(member_id)
);

CREATE INDEX IF NOT EXISTS idx_campaign_member ON campaign_interactions(member_id);
