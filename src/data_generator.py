"""
Core data generation functions for nonprofit donor data.
Reusable across scripts and testable.
"""
from faker import Faker
from datetime import datetime
import random
from typing import Dict, List

fake = Faker()

def generate_donor(donor_id: int, seed: int = None) -> Dict:
    """
    Generate a single donor record.
    
    Args:
        donor_id: Unique identifier for the donor
        seed: Optional random seed for reproducibility
        
    Returns:
        Dictionary containing donor information
    """
    if seed is not None:
        Faker.seed(seed)
        random.seed(seed)
    
    return {
        'donor_id': donor_id,
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

def generate_donation(donation_id: int, donor_id: int, campaign_id: int = None, seed: int = None) -> Dict:
    """
    Generate a single donation record.
    
    Args:
        donation_id: Unique identifier for the donation
        donor_id: ID of the donor making the donation
        campaign_id: Optional campaign ID (random if None)
        seed: Optional random seed for reproducibility
        
    Returns:
        Dictionary containing donation information
    """
    if seed is not None:
        Faker.seed(seed)
        random.seed(seed)
    
    if campaign_id is None:
        campaign_id = random.randint(1, 10)
    
    return {
        'donation_id': donation_id,
        'donor_id': donor_id,
        'amount': round(random.uniform(10, 5000), 2),
        'donation_date': fake.date_between(start_date='-3y', end_date='today'),
        'campaign_id': campaign_id,
        'payment_method': random.choice(['Credit Card', 'Check', 'Bank Transfer', 'Cash']),
        'is_recurring': random.choice([True, False])
    }

def generate_campaign(campaign_id: int, campaign_name: str, seed: int = None) -> Dict:
    """
    Generate a single campaign record.
    
    Args:
        campaign_id: Unique identifier for the campaign
        campaign_name: Name of the campaign
        seed: Optional random seed for reproducibility
        
    Returns:
        Dictionary containing campaign information
    """
    if seed is not None:
        Faker.seed(seed)
        random.seed(seed)
    
    return {
        'campaign_id': campaign_id,
        'campaign_name': campaign_name,
        'start_date': fake.date_between(start_date='-2y', end_date='-1y'),
        'end_date': fake.date_between(start_date='-1y', end_date='today'),
        'goal_amount': random.randint(10000, 100000),
        'campaign_type': random.choice(['Direct Mail', 'Email', 'Event', 'Social Media'])
    }

def validate_donor(donor: Dict) -> bool:
    """
    Validate donor record has required fields and valid data.
    
    Args:
        donor: Dictionary containing donor information
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['donor_id', 'first_name', 'last_name', 'email', 'donor_type']
    
    if not all(field in donor for field in required_fields):
        return False
    
    if '@' not in donor['email']:
        return False
    
    if donor['donor_type'] not in ['Individual', 'Foundation', 'Business', 'Other']:
        return False
    
    return True

def validate_donation(donation: Dict) -> bool:
    """
    Validate donation record has required fields and valid data.
    
    Args:
        donation: Dictionary containing donation information
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['donation_id', 'donor_id', 'amount', 'donation_date']
    
    if not all(field in donation for field in required_fields):
        return False
    
    if donation['amount'] <= 0:
        return False
    
    return True