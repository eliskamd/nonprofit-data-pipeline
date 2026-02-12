"""
Generate synthetic nonprofit donor data for testing.
Uses core functions from src.data_generator for maintainability.

Author: Eliška Merchant-Dest
"""
import pandas as pd
from src.data_generator import generate_donor, generate_donation, generate_campaign
import random
import os

# Set seeds for reproducibility
random.seed(42)

print("Starting DataBridge data generation...")
print("=" * 50)

# Create data directory
os.makedirs('data/synthetic', exist_ok=True)

# Generate donors
print("\nGenerating 1,000 donor profiles...")
donors = [generate_donor(i + 1, seed=42 + i) for i in range(1000)]
df_donors = pd.DataFrame(donors)

# Generate donations
print("Generating 5,000 donation records...")
donations = [
    generate_donation(
        donation_id=i + 1,
        donor_id=random.randint(1, 1000),
        seed=42 + i
    )
    for i in range(5000)
]
df_donations = pd.DataFrame(donations)

# Generate campaigns
print("Generating 10 fundraising campaigns...")
campaign_names = [
    'Annual Fund Drive', 'Fiscal Year End Appeal', 'Spring Gala',
    'School Supplies', 'Capital Campaign', 'Scholarship Drive',
    'Summer Campaign', 'Year-End Appeal', 'Monthly Giving',
    'Legacy Society'
]
campaigns = [
    generate_campaign(i + 1, name, seed=42 + i)
    for i, name in enumerate(campaign_names)
]
df_campaigns = pd.DataFrame(campaigns)

# Save datasets
print("\nSaving datasets to CSV files...")
df_donors.to_csv('data/synthetic/donors.csv', index=False)
df_donations.to_csv('data/synthetic/donations.csv', index=False)
df_campaigns.to_csv('data/synthetic/campaigns.csv', index=False)

# Summary
print("\n" + "=" * 50)
print("DATA GENERATION COMPLETE!")
print("=" * 50)
print("\nSummary:")
print(f"   - Donors: {len(df_donors):,}")
print(f"   - Donations: {len(df_donations):,}")
print(f"   - Campaigns: {len(df_campaigns)}")
print(f"   - Total donation amount: ${df_donations['amount'].sum():,.2f}")
print(f"   - Average donation: ${df_donations['amount'].mean():.2f}")
print(f"   - Date range: {df_donations['donation_date'].min()} to {df_donations['donation_date'].max()}")
print("\nFiles saved:")
print("   - data/synthetic/donors.csv")
print("   - data/synthetic/donations.csv")
print("   - data/synthetic/campaigns.csv")
print("\nNext steps:")
print("   1. Review the generated data")
print("   2. Set up PostgreSQL database")
print("   3. Build ETL pipeline to load data")
print("\n" + "=" * 50)