"""
Accor Live Limitless (ALL) Loyalty Platform - Synthetic Data Generator
Generates realistic enterprise-scale data simulating 5,000+ properties,
loyalty members, multi-year booking transactions, and campaign interactions.
"""

import os
import random
import datetime
from typing import Tuple, List, Dict
import numpy as np
import pandas as pd

# Set fixed random seed for reproducibility
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

# Accor Brands Configuration
ACCOR_PORTFOLIO = [
    # Luxury
    {"brand_code": "RAF", "brand_name": "Raffles", "segment": "Luxury", "base_adr_range": (450, 1100), "weight": 2},
    {"brand_code": "FMT", "brand_name": "Fairmont", "segment": "Luxury", "base_adr_range": (350, 850), "weight": 5},
    {"brand_code": "SOF", "brand_name": "Sofitel", "segment": "Luxury", "base_adr_range": (280, 650), "weight": 7},
    {"brand_code": "BYT", "brand_name": "Banyan Tree", "segment": "Luxury", "base_adr_range": (400, 950), "weight": 2},
    {"brand_code": "SLS", "brand_name": "SLS Hotels", "segment": "Luxury", "base_adr_range": (320, 750), "weight": 2},
    
    # Premium
    {"brand_code": "PUL", "brand_name": "Pullman", "segment": "Premium", "base_adr_range": (160, 320), "weight": 12},
    {"brand_code": "SWI", "brand_name": "Swissôtel", "segment": "Premium", "base_adr_range": (150, 300), "weight": 7},
    {"brand_code": "MGA", "brand_name": "MGallery", "segment": "Premium", "base_adr_range": (170, 350), "weight": 8},
    {"brand_code": "MOV", "brand_name": "Mövenpick", "segment": "Premium", "base_adr_range": (140, 290), "weight": 9},
    {"brand_code": "GMC", "brand_name": "Grand Mercure", "segment": "Premium", "base_adr_range": (130, 260), "weight": 6},
    
    # Midscale
    {"brand_code": "NOV", "brand_name": "Novotel", "segment": "Midscale", "base_adr_range": (95, 210), "weight": 24},
    {"brand_code": "MER", "brand_name": "Mercure", "segment": "Midscale", "base_adr_range": (85, 195), "weight": 25},
    {"brand_code": "TRI", "brand_name": "Tribe", "segment": "Midscale", "base_adr_range": (90, 180), "weight": 4},
    {"brand_code": "ADG", "brand_name": "Adagio Aparthotels", "segment": "Midscale", "base_adr_range": (90, 190), "weight": 6},
    
    # Economy
    {"brand_code": "IBI", "brand_name": "ibis", "segment": "Economy", "base_adr_range": (55, 115), "weight": 35},
    {"brand_code": "IBS", "brand_name": "ibis Styles", "segment": "Economy", "base_adr_range": (65, 125), "weight": 20},
    {"brand_code": "IBB", "brand_name": "ibis budget", "segment": "Economy", "base_adr_range": (42, 85), "weight": 22},
    {"brand_code": "GRT", "brand_name": "greet", "segment": "Economy", "base_adr_range": (48, 90), "weight": 4},
]

REGIONS = {
    "Europe": [
        ("FRA", "Paris"), ("FRA", "Nice"), ("FRA", "Lyon"), ("FRA", "Marseille"),
        ("GBR", "London"), ("GBR", "Edinburgh"), ("GBR", "Manchester"),
        ("DEU", "Berlin"), ("DEU", "Munich"), ("DEU", "Frankfurt"),
        ("ITA", "Rome"), ("ITA", "Milan"), ("ITA", "Florence"),
        ("ESP", "Madrid"), ("ESP", "Barcelona"), ("ESP", "Seville"),
        ("NLD", "Amsterdam"), ("CHE", "Geneva"), ("CHE", "Zurich")
    ],
    "Asia Pacific": [
        ("SGP", "Singapore"), ("THA", "Bangkok"), ("THA", "Phuket"),
        ("JPN", "Tokyo"), ("JPN", "Kyoto"), ("JPN", "Osaka"),
        ("AUS", "Sydney"), ("AUS", "Melbourne"), ("AUS", "Brisbane"),
        ("IDN", "Bali"), ("IDN", "Jakarta"), ("VNM", "Hanoi"), ("VNM", "Da Nang"),
        ("IND", "Mumbai"), ("IND", "Delhi"), ("IND", "Bengaluru")
    ],
    "North America": [
        ("USA", "New York"), ("USA", "San Francisco"), ("USA", "Chicago"), ("USA", "Miami"),
        ("CAN", "Montreal"), ("CAN", "Toronto"), ("CAN", "Vancouver"), ("MEX", "Cancun")
    ],
    "Middle East & Africa": [
        ("ARE", "Dubai"), ("ARE", "Abu Dhabi"), ("SAU", "Riyadh"), ("SAU", "Jeddah"),
        ("EGY", "Cairo"), ("MAR", "Marrakech"), ("ZAF", "Cape Town")
    ],
    "Latin America": [
        ("BRA", "Sao Paulo"), ("BRA", "Rio de Janeiro"), ("ARG", "Buenos Aires"),
        ("CHL", "Santiago"), ("COL", "Bogota")
    ]
}

TIER_CONFIG = {
    "Classic": {"weight": 0.52, "min_nights": 0, "points_mult": 1.0},
    "Silver": {"weight": 0.23, "min_nights": 10, "points_mult": 1.25},
    "Gold": {"weight": 0.15, "min_nights": 30, "points_mult": 1.5},
    "Platinum": {"weight": 0.08, "min_nights": 60, "points_mult": 1.75},
    "Diamond": {"weight": 0.02, "min_nights": 100, "points_mult": 2.0}
}

FIRST_NAMES = [
    "Alexandre", "Camille", "Jean", "Sophie", "Antoine", "Marie", "Julien", "Chloe", "Nicolas", "Emma",
    "Oliver", "Charlotte", "Liam", "Amelia", "Lucas", "Isabella", "James", "Sophia", "Benjamin", "Mia",
    "Max", "Hannah", "Lukas", "Laura", "Felix", "Anna", "Leon", "Julia", "Paul", "Elena",
    "Kenji", "Yuki", "Hiroshi", "Sakura", "Wei", "Mei", "Arjun", "Priya", "Rohan", "Ananya",
    "Mateo", "Valentina", "Santiago", "Camila", "Tariq", "Fatima", "Omar", "Layla", "Arthur", "Zoe"
]

LAST_NAMES = [
    "Dubois", "Laurent", "Moreau", "Bernard", "Petit", "Roux", "Fournier", "Girard", "Mercier", "Dupont",
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner", "Becker", "Schulz", "Hoffmann",
    "Tanaka", "Sato", "Suzuki", "Watanabe", "Chen", "Wang", "Zhang", "Sharma", "Patel", "Verma",
    "Silva", "Santos", "Al-Mansoor", "Al-Sayed", "Haddad", "Rossi", "Ferrari", "Esposito", "Bianchi", "Ricci"
]


def generate_properties_portfolio(n_properties: int = 5000) -> pd.DataFrame:
    """
    Generate the 5,000+ Accor hotel properties network across global regions.
    """
    brand_weights = [b["weight"] for b in ACCOR_PORTFOLIO]
    selected_brands = random.choices(ACCOR_PORTFOLIO, weights=brand_weights, k=n_properties)
    
    properties = []
    region_names = list(REGIONS.keys())
    region_weights = [0.45, 0.25, 0.12, 0.10, 0.08] # Accor has historic European dominance

    for i in range(1, n_properties + 1):
        prop_id = f"PROP_{i:05d}"
        brand = selected_brands[i - 1]
        region = random.choices(region_names, weights=region_weights)[0]
        country, city = random.choice(REGIONS[region])
        
        # Room counts based on segment
        if brand["segment"] == "Luxury":
            room_count = random.randint(120, 380)
            has_spa = random.random() < 0.92
            has_dining = random.random() < 0.98
        elif brand["segment"] == "Premium":
            room_count = random.randint(160, 450)
            has_spa = random.random() < 0.70
            has_dining = random.random() < 0.85
        elif brand["segment"] == "Midscale":
            room_count = random.randint(100, 320)
            has_spa = random.random() < 0.25
            has_dining = random.random() < 0.65
        else: # Economy
            room_count = random.randint(70, 250)
            has_spa = False
            has_dining = random.random() < 0.20
            
        base_adr = round(random.uniform(*brand["base_adr_range"]), 2)
        prop_name = f"{brand['brand_name']} {city} {random.choice(['Centre', 'Grand', 'Palace', 'Resort', 'Airport', 'Tower', 'Boutique', 'Park'])}"
        
        properties.append({
            "property_id": prop_id,
            "property_name": prop_name,
            "brand_code": brand["brand_code"],
            "brand_name": brand["brand_name"],
            "brand_segment": brand["segment"],
            "country_code": country,
            "city": city,
            "region": region,
            "room_count": room_count,
            "average_base_adr_eur": base_adr,
            "has_spa_facility": has_spa,
            "has_fine_dining": has_dining
        })
        
    return pd.DataFrame(properties)


def generate_loyalty_members(n_members: int = 15000) -> pd.DataFrame:
    """
    Generate Accor Live Limitless (ALL) loyalty member profiles with demographic
    and program attributes.
    """
    tiers = list(TIER_CONFIG.keys())
    tier_weights = [TIER_CONFIG[t]["weight"] for t in tiers]
    
    countries = ["FRA", "GBR", "DEU", "AUS", "USA", "SGP", "ITA", "ESP", "ARE", "BRA", "IND", "JPN", "CHE"]
    country_weights = [0.30, 0.14, 0.12, 0.08, 0.08, 0.06, 0.05, 0.05, 0.04, 0.03, 0.02, 0.02, 0.01]
    
    travel_purposes = ["Leisure", "Business", "Bleisure"]
    purpose_weights = [0.48, 0.38, 0.14]
    
    start_date = datetime.date(2021, 1, 1)
    end_date = datetime.date(2025, 12, 31)
    date_range_days = (end_date - start_date).days
    
    members = []
    used_emails = set()
    
    for i in range(1, n_members + 1):
        member_id = f"ALL_{i:07d}"
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        
        email_cand = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 9999)}@example.com"
        while email_cand in used_emails:
            email_cand = f"{first_name.lower()}.{last_name.lower()}{random.randint(10000, 999999)}@example.com"
        used_emails.add(email_cand)
        
        tier = random.choices(tiers, weights=tier_weights)[0]
        enroll_offset = random.randint(0, date_range_days)
        enroll_date = start_date + datetime.timedelta(days=enroll_offset)
        
        # Points based on tier
        if tier == "Diamond":
            reward_pts = random.randint(45000, 220000)
            status_pts = random.randint(26000, 75000)
        elif tier == "Platinum":
            reward_pts = random.randint(20000, 90000)
            status_pts = random.randint(14000, 28000)
        elif tier == "Gold":
            reward_pts = random.randint(7000, 35000)
            status_pts = random.randint(7000, 15000)
        elif tier == "Silver":
            reward_pts = random.randint(2000, 12000)
            status_pts = random.randint(2000, 7500)
        else: # Classic
            reward_pts = random.randint(100, 4500)
            status_pts = random.randint(0, 2500)
            
        country = random.choices(countries, weights=country_weights)[0]
        purpose = random.choices(travel_purposes, weights=purpose_weights)[0]
        app_installed = random.random() < (0.95 if tier in ["Platinum", "Diamond"] else 0.65)
        email_sub = random.random() < 0.82
        
        members.append({
            "member_id": member_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": email_cand,
            "enrollment_date": enroll_date.strftime("%Y-%m-%d"),
            "current_tier": tier,
            "status_points": status_pts,
            "reward_points_balance": reward_pts,
            "country_of_residence": country,
            "primary_travel_purpose": purpose,
            "app_installed": app_installed,
            "email_subscribed": email_sub
        })
        
    return pd.DataFrame(members)


def generate_bookings_and_stays(
    df_members: pd.DataFrame, 
    df_properties: pd.DataFrame,
    analysis_date: datetime.date = datetime.date(2026, 10, 25)
) -> pd.DataFrame:
    """
    Generate multi-year booking and stay records reflecting genuine customer lifecycle,
    including active champions, slipping guests, and dormant members.
    """
    channels = ["ALL_Direct_App", "ALL_Direct_Web", "Corporate_GDS", "OTA_Booking", "OTA_Expedia"]
    channel_weights = [0.38, 0.32, 0.14, 0.10, 0.06]
    
    prop_by_segment = {
        seg: df_properties[df_properties["brand_segment"] == seg].to_dict("records")
        for seg in ["Luxury", "Premium", "Midscale", "Economy"]
    }
    
    bookings = []
    booking_counter = 1
    
    # Define behavioral personas across member population to reflect realistic churn & segmentation
    for _, member in df_members.iterrows():
        m_id = member["member_id"]
        tier = member["current_tier"]
        enroll_date = datetime.datetime.strptime(member["enrollment_date"], "%Y-%m-%d").date()
        
        # Decide member behavioral persona:
        # Persona 1: "High-Value Champion" (frequent, recent, high spend)
        # Persona 2: "Loyal Mainstay" (steady, consistent business/leisure)
        # Persona 3: "At-Risk Churner" (was frequent, but stopped 7-14 months ago or had bad experience)
        # Persona 4: "Dormant Member" (inactive > 12-24 months)
        # Persona 5: "Occasional / Budget" (1-2 stays, low spend)
        
        rand_val = random.random()
        if tier in ["Diamond", "Platinum"]:
            persona = "Champion" if rand_val < 0.65 else ("At-Risk" if rand_val < 0.88 else "Dormant")
        elif tier == "Gold":
            persona = "Mainstay" if rand_val < 0.50 else ("At-Risk" if rand_val < 0.75 else ("Champion" if rand_val < 0.85 else "Dormant"))
        elif tier == "Silver":
            persona = "Mainstay" if rand_val < 0.35 else ("At-Risk" if rand_val < 0.65 else ("Dormant" if rand_val < 0.85 else "Occasional"))
        else: # Classic
            persona = "Occasional" if rand_val < 0.55 else ("Dormant" if rand_val < 0.82 else ("At-Risk" if rand_val < 0.94 else "Mainstay"))
            
        # Determine stay counts and recency window based on persona
        if persona == "Champion":
            num_stays = random.randint(8, 26)
            recency_days = random.randint(5, 65)
            preferred_segs = ["Luxury", "Premium"]
            seg_weights = [0.65, 0.35]
            complaint_prob = 0.03
            direct_channel_boost = True
        elif persona == "Mainstay":
            num_stays = random.randint(4, 14)
            recency_days = random.randint(20, 120)
            preferred_segs = ["Premium", "Midscale"]
            seg_weights = [0.45, 0.55]
            complaint_prob = 0.06
            direct_channel_boost = True
        elif persona == "At-Risk":
            num_stays = random.randint(3, 10)
            recency_days = random.randint(185, 360) # slipping!
            preferred_segs = ["Midscale", "Premium", "Economy"]
            seg_weights = [0.50, 0.30, 0.20]
            complaint_prob = 0.25 # often triggered by bad stay
            direct_channel_boost = False
        elif persona == "Dormant":
            num_stays = random.randint(1, 5)
            recency_days = random.randint(380, 780) # inactive > 1 year
            preferred_segs = ["Midscale", "Economy"]
            seg_weights = [0.40, 0.60]
            complaint_prob = 0.15
            direct_channel_boost = False
        else: # Occasional
            num_stays = random.randint(1, 3)
            recency_days = random.randint(40, 320)
            preferred_segs = ["Economy", "Midscale"]
            seg_weights = [0.70, 0.30]
            complaint_prob = 0.08
            direct_channel_boost = False

        # Generate the stays chronologically backwards from (analysis_date - recency_days)
        last_stay_checkout = analysis_date - datetime.timedelta(days=recency_days)
        current_ref_date = last_stay_checkout
        
        for s_idx in range(num_stays):
            # Check stay doesn't precede enrollment
            nights = random.choices([1, 2, 3, 4, 5, 7, 10], weights=[0.25, 0.35, 0.20, 0.10, 0.05, 0.03, 0.02])[0]
            checkin = current_ref_date - datetime.timedelta(days=nights)
            if checkin < enroll_date:
                checkin = enroll_date + datetime.timedelta(days=random.randint(1, 10))
                current_ref_date = checkin + datetime.timedelta(days=nights)
                
            lead_time = random.randint(3, 90)
            booking_date = checkin - datetime.timedelta(days=lead_time)
            
            # Select property segment
            seg = random.choices(preferred_segs, weights=seg_weights)[0]
            prop = random.choice(prop_by_segment[seg])
            
            # Booking status: Completed or Cancelled
            if persona == "At-Risk" and s_idx == 0 and random.random() < 0.40:
                status = "Cancelled"
            else:
                status = "Completed" if random.random() > 0.09 else "Cancelled"
                
            # Channel
            if direct_channel_boost:
                channel = random.choices(["ALL_Direct_App", "ALL_Direct_Web", "Corporate_GDS"], weights=[0.55, 0.35, 0.10])[0]
            else:
                channel = random.choices(channels, weights=channel_weights)[0]
                
            # Pricing
            base_adr = prop["average_base_adr_eur"] * random.uniform(0.85, 1.25)
            room_revenue = round(base_adr * nights, 2) if status == "Completed" else 0.0
            
            # Ancillary spend (dining, spa, minibar)
            if status == "Completed":
                if seg == "Luxury":
                    ancillary = round(random.uniform(50, 220) * nights, 2)
                elif seg == "Premium":
                    ancillary = round(random.uniform(25, 90) * nights, 2)
                elif seg == "Midscale":
                    ancillary = round(random.uniform(10, 45) * nights, 2)
                else:
                    ancillary = round(random.uniform(0, 20) * nights, 2)
            else:
                ancillary = 0.0
                
            total_spend = round(room_revenue + ancillary, 2)
            
            # Loyalty points
            pts_mult = TIER_CONFIG[tier]["points_mult"]
            pts_earned = int(total_spend * 10 * pts_mult) if status == "Completed" else 0
            pts_redeemed = random.randint(2000, 10000) if (status == "Completed" and random.random() < 0.18) else 0
            
            # Satisfaction & Complaints
            has_complaint = (random.random() < complaint_prob) if status == "Completed" else False
            if has_complaint:
                satisfaction = random.randint(1, 5)
            elif status == "Completed":
                satisfaction = random.choices([7, 8, 9, 10], weights=[0.15, 0.35, 0.35, 0.15])[0]
            else:
                satisfaction = None
                
            bookings.append({
                "booking_id": f"BK_{booking_counter:08d}",
                "member_id": m_id,
                "property_id": prop["property_id"],
                "booking_date": booking_date.strftime("%Y-%m-%d"),
                "checkin_date": checkin.strftime("%Y-%m-%d"),
                "checkout_date": current_ref_date.strftime("%Y-%m-%d"),
                "nights": nights,
                "rooms": 1,
                "booking_channel": channel,
                "booking_status": status,
                "lead_time_days": lead_time,
                "room_revenue_eur": room_revenue,
                "ancillary_revenue_eur": ancillary,
                "total_spend_eur": total_spend,
                "points_earned": pts_earned,
                "points_redeemed": pts_redeemed,
                "guest_satisfaction_score": satisfaction,
                "has_service_complaint": 1 if has_complaint else 0
            })
            booking_counter += 1
            
            # Move earlier in time for the next previous stay
            stay_gap = random.randint(25, 140)
            current_ref_date = checkin - datetime.timedelta(days=stay_gap)
            if current_ref_date <= enroll_date:
                break
                
    return pd.DataFrame(bookings)


def generate_crm_campaigns(df_members: pd.DataFrame) -> pd.DataFrame:
    """
    Generate CRM marketing campaign interactions (Email, App Push, Concierge).
    """
    campaign_names = [
        "Summer Riviera Getaway Double Points",
        "Winter Alps & Dolomites Escape",
        "ALL Platinum & Diamond Exclusive Suite Night",
        "We Miss You - 20% Off Your Next City Weekend",
        "Novotel Family Holidays Perks",
        "Sofitel Art de Vivre Dining Experience"
    ]
    
    interactions = []
    counter = 1
    
    for _, member in df_members.sample(frac=0.6, random_state=42).iterrows():
        m_id = member["member_id"]
        camp = random.choice(campaign_names)
        channel = "App_Push" if member["app_installed"] and random.random() < 0.55 else "Email"
        if member["current_tier"] in ["Platinum", "Diamond"] and "We Miss You" in camp:
            channel = "Concierge_Call"
            
        sent_offset = random.randint(5, 180)
        sent_date = datetime.date(2026, 10, 25) - datetime.timedelta(days=sent_offset)
        
        opened = random.random() < 0.45
        clicked = opened and (random.random() < 0.35)
        converted = clicked and (random.random() < 0.22)
        
        interactions.append({
            "interaction_id": f"INT_{counter:08d}",
            "member_id": m_id,
            "campaign_name": camp,
            "campaign_channel": channel,
            "sent_date": sent_date.strftime("%Y-%m-%d"),
            "opened": opened,
            "clicked": clicked,
            "converted_booking": converted
        })
        counter += 1
        
    return pd.DataFrame(interactions)


def run_data_generation(output_dir: str = "data/raw", n_properties: int = 5000, n_members: int = 12000):
    """
    Execute full data generation pipeline and save to raw directory.
    """
    os.makedirs(output_dir, exist_ok=True)
    print(f"[*] Generating {n_properties} Accor properties across global portfolio...")
    df_props = generate_properties_portfolio(n_properties=n_properties)
    df_props.to_csv(os.path.join(output_dir, "properties.csv"), index=False)
    print(f"[+] Saved properties.csv ({len(df_props)} rows)")
    
    print(f"[*] Generating {n_members} Accor loyalty members...")
    df_members = generate_loyalty_members(n_members=n_members)
    df_members.to_csv(os.path.join(output_dir, "loyalty_members.csv"), index=False)
    print(f"[+] Saved loyalty_members.csv ({len(df_members)} rows)")
    
    print("[*] Generating multi-year bookings and stay records...")
    df_bookings = generate_bookings_and_stays(df_members, df_props)
    df_bookings.to_csv(os.path.join(output_dir, "bookings.csv"), index=False)
    print(f"[+] Saved bookings.csv ({len(df_bookings)} rows)")
    
    print("[*] Generating CRM campaign interactions...")
    df_camps = generate_crm_campaigns(df_members)
    df_camps.to_csv(os.path.join(output_dir, "campaign_interactions.csv"), index=False)
    print(f"[+] Saved campaign_interactions.csv ({len(df_camps)} rows)")
    
    print("[OK] Raw data generation complete!")
    return df_props, df_members, df_bookings, df_camps


if __name__ == "__main__":
    run_data_generation()
