"""
Generate synthetic nonprofit donor data for testing.
Uses core functions from src.data_generator for maintainability.

Author: Eliška Merchant-Dest
"""
import pandas as pd
from src.data_generator import (
    generate_donor,
    generate_donation,
    generate_campaign,
    generate_portfolio_holder,
    generate_portfolio_assignment,
)
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

# Generate donations (most with a campaign, ~10% without a campaign)
print("Generating 5,000 donation records...")
donations = []
for i in range(5000):
    allow_no_campaign = random.random() < 0.10  # 10% gifts without a campaign
    donations.append(
        generate_donation(
            donation_id=i + 1,
            donor_id=random.randint(1, 1000),
            campaign_id=None,
            allow_no_campaign=allow_no_campaign,
            seed=42 + i,
        )
    )
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

# Generate portfolio holders and assignments
# 3 portfolios: Major Gifts (80), Mid-Level Donors (100), Corporate Partners (60) = 240 assignments
print("Generating portfolio holders and assignments...")
portfolio_specs = [
    ("Major Gifts", 80),
    ("Mid-Level Donors", 100),
    ("Corporate Partners", 60),
]
portfolio_holders = [
    generate_portfolio_holder(i + 1, name=name, seed=42 + i)
    for i, (name, _) in enumerate(portfolio_specs)
]
df_portfolio_holders = pd.DataFrame(portfolio_holders)

donor_ids = list(range(1, 1001))
random.seed(42)
random.shuffle(donor_ids)
assignments = []
assignment_id = 1
for portfolio_holder_id, (portfolio_name, count) in enumerate(portfolio_specs, start=1):
    for _ in range(count):
        donor_id = donor_ids.pop(0)
        assignments.append(
            generate_portfolio_assignment(
                assignment_id=assignment_id,
                donor_id=donor_id,
                portfolio_holder_id=portfolio_holder_id,
                seed=42 + assignment_id,
            )
        )
        assignment_id += 1
df_assignments = pd.DataFrame(assignments)

# Save datasets
print("\nSaving datasets to CSV files...")
df_donors.to_csv('data/synthetic/donors.csv', index=False)
df_donations.to_csv('data/synthetic/donations.csv', index=False)
df_campaigns.to_csv('data/synthetic/campaigns.csv', index=False)
df_portfolio_holders.to_csv('data/synthetic/portfolio_holders.csv', index=False)
df_assignments.to_csv('data/synthetic/portfolio_assignments.csv', index=False)

# Summary
print("\n" + "=" * 50)
print("DATA GENERATION COMPLETE!")
print("=" * 50)
print("\nSummary:")
print(f"   - Donors: {len(df_donors):,}")
print(f"   - Donations: {len(df_donations):,}")
print(f"   - Campaigns: {len(df_campaigns)}")
print(f"   - Portfolio holders: {len(df_portfolio_holders)}")
print(f"   - Portfolio assignments: {len(df_assignments):,}")
print(f"   - Donations without campaign: {df_donations['campaign_id'].isna().sum():,}")
print(f"   - Total donation amount: ${df_donations['amount'].sum():,.2f}")
print(f"   - Average donation: ${df_donations['amount'].mean():.2f}")
print(f"   - Date range: {df_donations['donation_date'].min()} to {df_donations['donation_date'].max()}")
print("\nFiles saved:")
print("   - data/synthetic/donors.csv")
print("   - data/synthetic/donations.csv")
print("   - data/synthetic/campaigns.csv")
print("   - data/synthetic/portfolio_holders.csv")
print("   - data/synthetic/portfolio_assignments.csv")
print("\nNext steps:")
print("   1. Review the generated data")
print("   2. Set up PostgreSQL database")
print("   3. Build ETL pipeline to load data")
print("\n" + "=" * 50)