"""
Generate synthetic nonprofit donor data for testing
Author: Eliška Merchant-Dest
"""
import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta
import os

# Initialize
fake = Faker()
Faker.seed(42)  # Reproducible data
random.seed(42)

print("🎉 Starting DataBridge data generation...")
print("=" * 50)

# Create data directory if it doesn't exist
os.makedirs('data/synthetic', exist_ok=True)

# Generate 1,000 donors
print("\n📊 Generating 1,000 donor profiles...")
donors = []
for i in range(1000):
    donor = {
        'donor_id': i + 1,
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'email': fake.email(),
        'phone': fake.phone_number(),
        'address': fake.street_address(),
        'city': fake.city(),
        'state': fake.state_abbr(),
        'zip_code': fake.zipcode(),
        'created_date': fake.date_between(start_date='-5y', end_date='today'),
        'donor_type': random.choice(['Individual', 'Foundation', 'Business', 'Other'])
    }
    donors.append(donor)

df_donors = pd.DataFrame(donors)

# Generate 5,000 donations
print("💰 Generating 5,000 donation records...")
donations = []
for i in range(5000):
    donor_id = random.randint(1, 1000)
    donation = {
        'donation_id': i + 1,
        'donor_id': donor_id,
        'amount': round(random.uniform(10, 5000), 2),
        'donation_date': fake.date_between(start_date='-3y', end_date='today'),
        'campaign_id': random.randint(1, 10),
        'payment_method': random.choice(['Credit Card', 'Check', 'Bank Transfer', 'Cash']),
        'is_recurring': random.choice([True, False])
    }
    donations.append(donation)

df_donations = pd.DataFrame(donations)

# Generate 10 campaigns
print("📢 Generating 10 fundraising campaigns...")
campaigns = []
campaign_names = [
    'Annual Fund Drive', 'Fiscal Year End Appeal', 'Spring Gala',
    'School Supplies', 'Capital Campaign', 'Scholarship Drive',
    'Summer Campaign', 'Year-End Appeal', 'Monthly Giving',
    'Legacy Society'
]

for i, name in enumerate(campaign_names, 1):
    campaign = {
        'campaign_id': i,
        'campaign_name': name,
        'start_date': fake.date_between(start_date='-2y', end_date='-1y'),
        'end_date': fake.date_between(start_date='-1y', end_date='today'),
        'goal_amount': random.randint(10000, 100000),
        'campaign_type': random.choice(['Direct Mail', 'Email', 'Event', 'Social Media'])
    }
    campaigns.append(campaign)

df_campaigns = pd.DataFrame(campaigns)

# Save all datasets
print("\n💾 Saving datasets to CSV files...")
df_donors.to_csv('data/synthetic/donors.csv', index=False)
df_donations.to_csv('data/synthetic/donations.csv', index=False)
df_campaigns.to_csv('data/synthetic/campaigns.csv', index=False)

# Summary statistics
print("\n" + "=" * 50)
print("✅ DATA GENERATION COMPLETE!")
print("=" * 50)
print(f"\n📊 Summary:")
print(f"   • Donors: {len(df_donors):,}")
print(f"   • Donations: {len(df_donations):,}")
print(f"   • Campaigns: {len(df_campaigns)}")
print(f"   • Total donation amount: ${df_donations['amount'].sum():,.2f}")
print(f"   • Average donation: ${df_donations['amount'].mean():.2f}")
print(f"   • Date range: {df_donations['donation_date'].min()} to {df_donations['donation_date'].max()}")

print("\n📁 Files saved:")
print("   • data/synthetic/donors.csv")
print("   • data/synthetic/donations.csv")
print("   • data/synthetic/campaigns.csv")

print("\n🎯 Next steps:")
print("   1. Review the generated data")
print("   2. Set up PostgreSQL database")
print("   3. Build ETL pipeline to load data")

print("\n" + "=" * 50)