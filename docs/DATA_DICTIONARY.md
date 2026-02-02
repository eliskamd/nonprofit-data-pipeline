# Data Dictionary - DataBridge Nonprofit Analytics

## Overview
This document defines all data elements in the DataBridge system.

---

## Table: donors

**Purpose:** Master table of all donor profiles

| Column | Data Type | Constraints | Description | Example |
|--------|-----------|-------------|-------------|---------|
| donor_id | INTEGER | PRIMARY KEY, NOT NULL | Unique identifier for each donor | 1, 2, 3... |
| first_name | VARCHAR(100) | | Donor's first name | "John" |
| last_name | VARCHAR(100) | | Donor's last name | "Smith" |
| email | VARCHAR(255) | INDEXED | Primary email address | "john.smith@example.com" |
| phone | VARCHAR(50) | | Phone number (formatted) | "(555) 123-4567" |
| address | VARCHAR(255) | | Street address | "123 Main St" |
| city | VARCHAR(100) | | City name | "Denver" |
| state | VARCHAR(2) | | Two-letter state code | "CO" |
| zip_code | VARCHAR(10) | | ZIP or ZIP+4 code | "80202" or "80202-1234" |
| created_date | DATE | | Date donor first entered system | "2020-03-15" |
| donor_type | VARCHAR(50) | | Classification of donor | "Individual", "Foundation", "Corporation", "Other" |

**Business Rules:**
- email should be unique (not enforced at DB level currently)
- created_date should be <= current date
- donor_type must be one of the predefined categories

---

## Table: campaigns

**Purpose:** Fundraising campaign master data

| Column | Data Type | Constraints | Description | Example |
|--------|-----------|-------------|-------------|---------|
| campaign_id | INTEGER | PRIMARY KEY, NOT NULL | Unique identifier for each campaign | 1, 2, 3... |
| campaign_name | VARCHAR(255) | | Human-readable campaign name | "Annual Fund Drive" |
| start_date | DATE | | Campaign launch date | "2025-01-01" |
| end_date | DATE | | Campaign end date | "2025-03-31" |
| goal_amount | INTEGER | | Fundraising goal in whole dollars | 50000 |
| campaign_type | VARCHAR(50) | | Channel/method of fundraising | "Direct Mail", "Email", "Event", "Social Media" |

**Business Rules:**
- start_date < end_date
- goal_amount > 0
- campaign_type from predefined list

---

## Table: donations

**Purpose:** Individual donation transactions

| Column | Data Type | Constraints | Description | Example |
|--------|-----------|-------------|-------------|---------|
| donation_id | INTEGER | PRIMARY KEY, NOT NULL | Unique identifier for each gift | 1, 2, 3... |
| donor_id | INTEGER | FOREIGN KEY (donors), INDEXED | Links to donor who made gift | 157 |
| campaign_id | INTEGER | FOREIGN KEY (campaigns), INDEXED | Links to campaign that solicited gift | 3 |
| amount | DECIMAL(10,2) | | Gift amount in dollars and cents | 250.00 |
| donation_date | DATE | INDEXED | Date gift was received | "2025-06-15" |
| payment_method | VARCHAR(50) | | How payment was made | "Credit Card", "Check", "Bank Transfer", "Cash" |
| is_recurring | BOOLEAN | | Whether this is a recurring gift | true, false |

**Business Rules:**
- amount > 0
- donor_id must exist in donors table
- campaign_id must exist in campaigns table
- donation_date should be between campaign start_date and end_date (not enforced)

---

## Calculated Fields / Metrics

### Donor Lifetime Value (LTV)
```sql
SUM(donations.amount) 
WHERE donations.donor_id = {specific_donor}
```

### Donor Retention Rate
```sql
(COUNT(DISTINCT donors who gave this year AND last year) / 
 COUNT(DISTINCT donors who gave last year)) * 100
```

### Campaign ROI
```sql
((SUM(donations.amount) - campaign_cost) / campaign_cost) * 100
```

### Monthly Donor Status
**Definition:** A donor is considered "monthly" if they meet ANY of:
- Has is_recurring = true
- Has made gifts in 3+ consecutive months
- Flagged manually as monthly donor

*(Note: Unified logic will be implemented in dbt)*

---

## Data Quality Rules

### Donors Table
- No NULL values in: donor_id, email
- Email format validation (contains @)
- State codes must be valid US states
- created_date cannot be in the future

### Campaigns Table
- No NULL values in: campaign_id, campaign_name
- start_date < end_date
- goal_amount > 0

### Donations Table
- No NULL values in: donation_id, donor_id, campaign_id, amount
- amount > 0
- donor_id must exist in donors
- campaign_id must exist in campaigns

---

## Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-01-21 | 1.0 | Initial data dictionary | Eliška Merchant-Dest |