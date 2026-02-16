"""
Unit tests for core data generation functions.
Tests individual functions in isolation for reliability.
"""
import pytest
from src.data_generator import (
    generate_donor,
    generate_donation,
    generate_campaign,
    generate_portfolio_holder,
    generate_portfolio_assignment,
    validate_donor,
    validate_donation
)

class TestGenerateDonor:
    """Tests for generate_donor function"""
    
    def test_generates_all_required_fields(self):
        """Test that donor has all required fields"""
        donor = generate_donor(donor_id=1)
        
        required_fields = ['donor_id', 'first_name', 'last_name', 'email',
                          'phone', 'address', 'city', 'state', 'zip_code',
                          'created_date', 'donor_type']
        assert all(field in donor for field in required_fields)
    
    def test_donor_id_matches_input(self):
        """Test that donor_id is set correctly"""
        donor = generate_donor(donor_id=12345)
        assert donor['donor_id'] == 12345
    
    def test_email_is_valid_format(self):
        """Test that email contains @"""
        donor = generate_donor(donor_id=1)
        assert '@' in donor['email']
    
    def test_donor_type_is_valid(self):
        """Test that donor_type is one of expected values"""
        donor = generate_donor(donor_id=1)
        valid_types = ['Individual', 'Foundation', 'Business', 'Other']
        assert donor['donor_type'] in valid_types
    
    def test_reproducibility_with_seed(self):
        """Test that same seed produces same donor"""
        donor1 = generate_donor(donor_id=1, seed=42)
        donor2 = generate_donor(donor_id=1, seed=42)
        assert donor1['first_name'] == donor2['first_name']
        assert donor1['email'] == donor2['email']

class TestGenerateDonation:
    """Tests for generate_donation function"""
    
    def test_generates_all_required_fields(self):
        """Test that donation has all required fields"""
        donation = generate_donation(donation_id=1, donor_id=100)
        
        required_fields = ['donation_id', 'donor_id', 'amount', 'donation_date',
                          'campaign_id', 'payment_method', 'is_recurring']
        assert all(field in donation for field in required_fields)
    
    def test_ids_match_input(self):
        """Test that IDs are set correctly"""
        donation = generate_donation(donation_id=999, donor_id=888, campaign_id=5)
        assert donation['donation_id'] == 999
        assert donation['donor_id'] == 888
        assert donation['campaign_id'] == 5
    
    def test_amount_is_positive(self):
        """Test that donation amount is greater than zero"""
        donation = generate_donation(donation_id=1, donor_id=1)
        assert donation['amount'] > 0
    
    def test_amount_is_in_expected_range(self):
        """Test that donation amount is within expected range"""
        donation = generate_donation(donation_id=1, donor_id=1)
        assert 10 <= donation['amount'] <= 5000
    
    def test_payment_method_is_valid(self):
        """Test that payment method is one of expected values"""
        donation = generate_donation(donation_id=1, donor_id=1)
        valid_methods = ['Credit Card', 'Check', 'Bank Transfer', 'Cash']
        assert donation['payment_method'] in valid_methods
    
    def test_is_recurring_is_boolean(self):
        """Test that is_recurring is a boolean"""
        donation = generate_donation(donation_id=1, donor_id=1)
        assert isinstance(donation['is_recurring'], bool)

    def test_campaign_id_none_when_allow_no_campaign(self):
        """Test that donation can have no campaign when allow_no_campaign=True"""
        donation = generate_donation(
            donation_id=1, donor_id=1, campaign_id=None, allow_no_campaign=True, seed=42
        )
        assert donation['campaign_id'] is None

    def test_campaign_id_random_when_none_and_not_allow_no_campaign(self):
        """Test that campaign_id is assigned when allow_no_campaign=False (default)"""
        donation = generate_donation(donation_id=1, donor_id=1, seed=42)
        assert donation['campaign_id'] is not None
        assert 1 <= donation['campaign_id'] <= 10

class TestGenerateCampaign:
    """Tests for generate_campaign function"""
    
    def test_generates_all_required_fields(self):
        """Test that campaign has all required fields"""
        campaign = generate_campaign(campaign_id=1, campaign_name="Test Campaign")
        
        required_fields = ['campaign_id', 'campaign_name', 'start_date',
                          'end_date', 'goal_amount', 'campaign_type']
        assert all(field in campaign for field in required_fields)
    
    def test_campaign_name_matches_input(self):
        """Test that campaign name is set correctly"""
        campaign = generate_campaign(campaign_id=1, campaign_name="Spring Gala")
        assert campaign['campaign_name'] == "Spring Gala"
    
    def test_goal_amount_is_positive(self):
        """Test that goal amount is greater than zero"""
        campaign = generate_campaign(campaign_id=1, campaign_name="Test")
        assert campaign['goal_amount'] > 0

class TestValidateDonor:
    """Tests for validate_donor function"""
    
    def test_valid_donor_returns_true(self):
        """Test that valid donor passes validation"""
        donor = generate_donor(donor_id=1)
        assert validate_donor(donor) is True
    
    def test_missing_required_field_returns_false(self):
        """Test that donor missing required field fails"""
        invalid_donor = {
            'donor_id': 1,
            'first_name': 'John'
            # Missing other required fields
        }
        assert validate_donor(invalid_donor) is False
    
    def test_invalid_email_returns_false(self):
        """Test that invalid email format fails"""
        invalid_donor = generate_donor(donor_id=1)
        invalid_donor['email'] = 'notanemail'
        assert validate_donor(invalid_donor) is False
    
    def test_invalid_donor_type_returns_false(self):
        """Test that invalid donor type fails"""
        invalid_donor = generate_donor(donor_id=1)
        invalid_donor['donor_type'] = 'InvalidType'
        assert validate_donor(invalid_donor) is False

class TestValidateDonation:
    """Tests for validate_donation function"""
    
    def test_valid_donation_returns_true(self):
        """Test that valid donation passes validation"""
        donation = generate_donation(donation_id=1, donor_id=1)
        assert validate_donation(donation) is True
    
    def test_missing_required_field_returns_false(self):
        """Test that donation missing required field fails"""
        invalid_donation = {
            'donation_id': 1,
            'donor_id': 1
            # Missing other required fields
        }
        assert validate_donation(invalid_donation) is False
    
    def test_negative_amount_returns_false(self):
        """Test that negative donation amount fails"""
        invalid_donation = generate_donation(donation_id=1, donor_id=1)
        invalid_donation['amount'] = -100
        assert validate_donation(invalid_donation) is False
    
    def test_zero_amount_returns_false(self):
        """Test that zero donation amount fails"""
        invalid_donation = generate_donation(donation_id=1, donor_id=1)
        invalid_donation['amount'] = 0
        assert validate_donation(invalid_donation) is False

    def test_donation_without_campaign_is_valid(self):
        """Test that donation with campaign_id None passes validation"""
        donation = generate_donation(
            donation_id=1, donor_id=1, campaign_id=None, allow_no_campaign=True, seed=42
        )
        assert donation['campaign_id'] is None
        assert validate_donation(donation) is True


class TestGeneratePortfolioHolder:
    """Tests for generate_portfolio_holder function"""

    def test_generates_all_required_fields(self):
        """Test that portfolio holder has expected fields"""
        holder = generate_portfolio_holder(holder_id=1, name="Jane Doe")
        assert holder['portfolio_holder_id'] == 1
        assert holder['name'] == "Jane Doe"
        assert 'email' in holder

    def test_name_random_when_none(self):
        """Test that name is generated when not provided"""
        holder = generate_portfolio_holder(holder_id=1, seed=42)
        assert ' ' in holder['name']
        assert len(holder['name']) > 0


class TestGeneratePortfolioAssignment:
    """Tests for generate_portfolio_assignment function"""

    def test_generates_all_required_fields(self):
        """Test that assignment has all expected fields"""
        assignment = generate_portfolio_assignment(
            assignment_id=1, donor_id=100, portfolio_holder_id=2, seed=42
        )
        assert assignment['assignment_id'] == 1
        assert assignment['donor_id'] == 100
        assert assignment['portfolio_holder_id'] == 2
        assert 'assigned_date' in assignment

    def test_assigned_date_matches_input(self):
        """Test that explicit assigned_date is used"""
        from datetime import date
        d = date(2024, 6, 1)
        assignment = generate_portfolio_assignment(
            assignment_id=1, donor_id=1, portfolio_holder_id=1, assigned_date=d
        )
        assert assignment['assigned_date'] == d