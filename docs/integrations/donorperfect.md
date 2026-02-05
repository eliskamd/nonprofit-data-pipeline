# DonorPerfect Integration

## Overview

This document describes the integration between your organization's PostgreSQL database and DonorPerfect's XML API (Version 7.1).

## API Configuration

### Authentication
- **Base URL**: `https://www.donorperfect.net/prod/xmlrequest.asp`
- **Authentication Method**: API Key (provided by DonorPerfect Support)
- **Request Format**: `https://www.donorperfect.net/prod/xmlrequest.asp?apikey=YOUR_KEY&action=PROCEDURE&params=PARAMS`

### Response Format
All responses are in XML format. Example:
```xml
<r>
  <record>
    <field name="donor_id" id="donor_id" value="147"/>
    <field name="first_name" id="first_name" value="John"/>
  </record>
</r>
```

## Data Schema

### 1. Donor Records (DP Table)

Procedures: `dp_donorsearch`, `dp_savedonor`

| Field | Type | Description | Example | PostgreSQL Mapping |
|-------|------|-------------|---------|-------------------|
| `donor_id` | numeric | Unique ID (0 = new) | `147` | `donors.donorperfect_id` |
| `first_name` | varchar(50) | First name | `John` | `donors.first_name` |
| `last_name` | varchar(75) | Last name | `Smith` | `donors.last_name` |
| `middle_name` | varchar(50) | Middle name | `Robert` | `donors.middle_name` |
| `suffix` | varchar(50) | Name suffix | `Jr.` | `donors.suffix` |
| `title` | varchar(50) | Honorific | `Dr.` | `donors.title` |
| `salutation` | varchar(130) | Greeting | `Dear Dr. Smith` | `donors.salutation` |
| `prof_title` | varchar(100) | Professional title | `CEO` | `donors.professional_title` |
| `opt_line` | varchar(100) | Optional address | `c/o Marketing` | `donors.opt_line` |
| `address` | varchar(100) | Street (line 1) | `123 Main St` | `donors.address_line1` |
| `address2` | varchar(100) | Street (line 2) | `Suite 100` | `donors.address_line2` |
| `city` | varchar(50) | City | `Springfield` | `donors.city` |
| `state` | varchar(30) | State/Province | `IL` | `donors.state` |
| `zip` | varchar(20) | Postal code | `62701` | `donors.zip_code` |
| `country` | varchar(30) | Country | `US` | `donors.country` |
| `address_type` | varchar(30) | Address type | `Home` | `donors.address_type` |
| `home_phone` | varchar(40) | Home phone | `(555) 123-4567` | `donors.home_phone` |
| `business_phone` | varchar(40) | Business phone | `(555) 987-6543` | `donors.business_phone` |
| `fax_phone` | varchar(40) | Fax | `(555) 111-2222` | `donors.fax_phone` |
| `mobile_phone` | varchar(40) | Mobile | `(555) 333-4444` | `donors.mobile_phone` |
| `email` | varchar(75) | Email | `john@example.com` | `donors.email` |
| `org_rec` | varchar(1) | Org flag | `Y`/`N` | `donors.is_organization` (bool) |
| `donor_type` | varchar(30) | Type | `IN`/`CO` | `donors.donor_type` |
| `nomail` | varchar(1) | No mail flag | `Y`/`N` | `donors.no_mail` (bool) |
| `nomail_reason` | varchar(30) | No mail reason | `Deceased` | `donors.no_mail_reason` |
| `narrative` | text | Notes | Free text | `donors.notes` |
| `donor_rcpt_type` | varchar(1) | Receipt type | `I`/`C` | `donors.receipt_type` |

### 2. Gift Records (DPGIFT Table)

Procedures: `dp_savegift`, `dp_gifts`

| Field | Type | Description | Example | PostgreSQL Mapping |
|-------|------|-------------|---------|-------------------|
| `gift_id` | numeric | Unique ID (0 = new) | `10230` | `gifts.donorperfect_gift_id` |
| `donor_id` | numeric | Donor FK | `147` | `gifts.donor_id` |
| `record_type` | varchar(1) | Type | `G`/`P`/`M`/`S` | `gifts.record_type` |
| `gift_date` | datetime | Date (MM/DD/YYYY) | `03/29/2018` | `gifts.gift_date` |
| `amount` | money | Amount | `149.95` | `gifts.amount` |
| `gl_code` | varchar(30) | GL code | `4540-N` | `gifts.gl_code` |
| `solicit_code` | varchar(30) | Solicitation | `BQ10` | `gifts.solicitation_code` |
| `sub_solicit_code` | varchar(30) | Sub-solicit | `TS` | `gifts.sub_solicitation_code` |
| `campaign` | varchar(30) | Campaign | `CAM2018` | `gifts.campaign_code` |
| `gift_type` | varchar(30) | Payment method | `VISAIC` | `gifts.payment_method` |
| `split_gift` | varchar(1) | Split flag | `Y`/`N` | `gifts.is_split` (bool) |
| `pledge_payment` | varchar(1) | Pledge payment | `Y`/`N` | `gifts.is_pledge_payment` (bool) |
| `reference` | varchar(100) | Reference | `Check #1234` | `gifts.reference` |
| `transaction_id` | numeric | Transaction ID | `1234567890123` | `gifts.transaction_id` |
| `memory_honor` | varchar(30) | Tribute type | `In Memory Of` | `gifts.memory_honor` |
| `gfname` | varchar(50) | Tribute first | `Jane` | `gifts.tribute_first_name` |
| `glname` | varchar(75) | Tribute last | `Doe` | `gifts.tribute_last_name` |
| `fmv` | money | Fair market value | `25.00` | `gifts.fair_market_value` |
| `batch_no` | numeric | Batch number | `501` | `gifts.batch_number` |
| `gift_narrative` | nvarchar(4000) | Notes | Free text | `gifts.notes` |
| `ty_letter_no` | varchar(30) | Thank you code | `TY` | `gifts.thank_you_letter_code` |
| `glink` | numeric | Parent gift ID | `10229` | `gifts.parent_gift_id` |
| `plink` | numeric | Pledge ID | `10150` | `gifts.pledge_id` |
| `nocalc` | varchar(1) | Exclude calc | `N`/`Y` | `gifts.exclude_from_reports` (bool) |
| `receipt` | varchar(1) | Generate receipt | `Y`/`N` | `gifts.generate_receipt` (bool) |
| `currency` | nvarchar(3) | Currency | `USD` | `gifts.currency` |
| `receipt_delivery_g` | varchar(1) | Delivery | `N`/`E`/`B`/`L` | `gifts.receipt_delivery` |

**Record Types:**
- `G` = Gift
- `P` = Pledge
- `M` = Main split gift
- `S` = Soft credit

**Payment Types (gift_type):** `CHECK`, `CASH`, `VISAIC`, `MC`, `AMEX`, `DISCOVER`, `EFT`, `STOCK`

**Receipt Delivery:** `N` = None, `E` = Email, `B` = Both, `L` = Letter

### 3. Code Tables (DPCODES)

Stores campaigns, solicitations, GL codes, and other lookup values.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `code` | varchar(30) | Code value | `ANNUAL2024` |
| `field_name` | varchar(30) | Code type | `CAMPAIGN` |
| `description` | varchar(100) | Description | `Annual Appeal 2024` |
| `active` | varchar(1) | Active flag | `Y`/`N` |

### 4. User Defined Fields (UDF)

Custom fields stored in separate tables:
- `DPUDF` - Donor UDFs
- `DPGIFTUDF` - Gift UDFs
- `DPADDRESSUDF` - Address UDFs
- `DPCONTACTUDF` - Contact UDFs

Use `dp_save_udf_xml` procedure or dynamic SELECT queries to access.

## Data Type Conversions

| DonorPerfect | PostgreSQL | Notes |
|-------------|-----------|-------|
| numeric | INTEGER/BIGINT | Use BIGINT for IDs |
| money | NUMERIC(12,2) | Currency values |
| varchar(N) | VARCHAR(N) | Direct mapping |
| nvarchar(N) | VARCHAR(N) | PG handles Unicode |
| text | TEXT | Long content |
| datetime | TIMESTAMP | See date format below |
| char(1) Y/N | BOOLEAN | Y=true, N=false |

### Date Format
- **DonorPerfect**: MM/DD/YYYY only (no time)
- **PostgreSQL**: YYYY-MM-DD HH:MM:SS
- Convert between formats when syncing

### Boolean Fields
Convert Y/N to boolean:
- `Y` → `true`
- `N` → `false`

Fields: `org_rec`, `nomail`, `split_gift`, `pledge_payment`, `receipt`, `nocalc`

### NULL Handling
- Use `NULL` for empty/unset values
- Never use empty string `''` for code fields (gl_code, solicit_code, campaign, etc.)
- In searches, `NULL` = wildcard `%`

## API Procedures

### dp_donorsearch
Search for donors (supports % wildcards).

```
.../xmlrequest.asp?apikey=KEY&action=dp_donorsearch&params=@donor_id=null,@last_name='Smith',@first_name='J%',...
```

### dp_savedonor
Create (donor_id=0) or update donor.

```
.../xmlrequest.asp?apikey=KEY&action=dp_savedonor&params=@donor_id=0,@first_name='John',@last_name='Smith',...
```

### dp_savegift
Create (gift_id=0) or update gift.

```
.../xmlrequest.asp?apikey=KEY&action=dp_savegift&params=@gift_id=0,@donor_id=147,@record_type='G',@gift_date='03/29/2018',@amount=149.95,...
```

### dp_gifts
Get all gifts for donor.

```
.../xmlrequest.asp?apikey=KEY&action=dp_gifts&params=@donor_id=147
```

### Dynamic Queries
Use SQL SELECT for custom queries:

```
.../xmlrequest.asp?apikey=KEY&action=SELECT donor_id, first_name, last_name FROM DP WHERE last_name='Smith'
```

**Available Tables:** `DP`, `DPGIFT`, `DPUDF`, `DPGIFTUDF`, `DPCODES`, `DPADDRESS`, `DPCONTACT`, `DPOTHERINFO`, `DPLINK`, `DPFLAGS`

## Security & Best Practices

### API Keys
- Provided by DonorPerfect Support
- Associated with user account but **bypass user permissions**
- Store in environment variables
- Never URL-encode the key itself

### Best Practices
1. Use predefined procedures over dynamic queries
2. Include `@user_id` in save operations (app name for audit)
3. Handle apostrophes by doubling: `O'Reilly` → `O''Reilly`
4. URL-encode parameters (not the API key)
5. Implement rate limiting
6. Log all API calls
7. Use pagination for large result sets (`SELECT TOP 100...`)

## Error Handling

Common issues:
- Missing parameters (even if NULL)
- Wrong date format (must be MM/DD/YYYY)
- Empty string `''` in code fields (use NULL)
- Wildcard encoding: `%` → `%25` in URLs

Errors returned in XML with descriptive messages.

## Sync Workflow

1. **Donor Sync**: Query PG → `dp_savedonor` → Store `donor_id`
2. **Gift Sync**: Query PG → `dp_savegift` → Store `gift_id`
3. **Code Sync**: Query `DPCODES` → Update PG lookup tables
4. **Retrieval**: Use search/dynamic queries → Parse XML → Update PG

## Testing

1. Test `dp_donorsearch` for connectivity
2. Create test donor (`donor_id=0`)
3. Create test gift with donor from step 2
4. Verify in DonorPerfect UI
5. Test updates with existing IDs
6. Implement error handling

## Resources

- **Documentation**: DonorPerfect XML API v7.1 (May 3, 2024)
- **Support**: support@donorperfect.com
- **API Keys**: Contact DonorPerfect Support/API Desk