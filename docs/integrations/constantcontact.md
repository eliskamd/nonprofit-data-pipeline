# Constant Contact API Integration

## Overview
RESTful JSON API for email engagement data

## Authentication
- Method: OAuth 2.0
- Developer Portal: developer.constantcontact.com
- Storage: .env file (CONSTANT_CONTACT_CLIENT_ID, CLIENT_SECRET)

## Base URL
https://api.constantcontact.com/v3/

## Key Endpoints
- /contacts - Get contact list
- /contacts/{id} - Individual contact
- /reports/summary_reports/email_campaign_summaries - Campaign stats
- /activities - Email opens, clicks

## Rate Limits
Yes (check docs for specifics)

## Data Schema
**Note:** This documentation is based on Constant Contact V3 API as of February 2025. Always consult the [official API reference](https://v3.developer.constantcontact.com/api_reference/index.html) for the most current field names and schemas.

### Overview
Constant Contact V3 API returns all data as JSON with UUID identifiers. Key resources include contacts, email campaigns, lists, and engagement metrics.

### UUID Format
All resource IDs use UUID v4 format: `91569d46-00e4-4a4d-9a4c-d3369409e9a7` (36 characters: 32 hex digits + 4 hyphens)

### Date Format
ISO-8601 UTC timestamps: `2023-12-01T09:00:00.000Z`

---

### 1. Contact Resource

**Endpoint:** `GET /v3/contacts/{contact_id}`

**Core Fields:**

| Field | Type | Required | Description | Mapping to DonorPerfect |
|-------|------|----------|-------------|-------------------------|
| `contact_id` | UUID | Read-only | Unique identifier | Store as `cc_contact_id` |
| `email_address.address` | String | Yes | Email address | Match to `email` field |
| `email_address.permission_to_send` | Enum | Read-only | Consent status | Filter for `explicit` or `implicit` |
| `email_address.opt_in_date` | DateTime | Read-only | Consent date | Track engagement start |
| `first_name` | String | No | First name | Match to `first_name` |
| `last_name` | String | No | Last name | Match to `last_name` |
| `company_name` | String | No | Organization | Match to `company` |
| `job_title` | String | No | Job title | Store as custom field |
| `created_at` | DateTime | Read-only | Record creation | Track acquisition date |
| `updated_at` | DateTime | Read-only | Last modification | Use for incremental sync |

**Subresources (use `?include=` parameter):**

**List Memberships:**
```json
"list_memberships": [
  {
    "list_id": "d13d60d0-f256-11e8-b47d-fa163e56c9b0",
    "status": "active",
    "created_at": "2022-01-15T10:30:00.000Z"
  }
]
```
*Use case:* Segment donors by list (e.g., "Monthly Donors", "Event Attendees")

**Custom Fields:**
```json
"custom_fields": [
  {
    "custom_field_id": "1618ae62-4752-11e9-9c8a-fa163e6b01c1",
    "name": "LastDonationDate",
    "value": "2023-11-15"
  }
]
```
*Use case:* Store donor-specific data (donation amounts, interests, donor type)
*Limit:* Max 50 characters per field value

**Tags:**
```json
"taggings": [
  {
    "tag_id": "5c2ec1e0-b456-11ea-8d77-fa163e67890a",
    "tag_name": "VIP Donor",
    "created_at": "2023-05-01T08:00:00.000Z"
  }
]
```
*Use case:* Categorize donors (VIP, Major Donor, Lapsed, etc.)

**Contact Permission to Send (not a separate "status" field):**
- `explicit` - Active, can email
- `implicit` - Active, can email
- `pending_confirmation` - Awaiting opt-in
- `temp_hold` - Temporary suspension
- `unsubscribed` - Do not email

**Query parameter `status` filters by:**
- `active` - Contacts with explicit or implicit permission
- `unsubscribed` - Contacts who opted out
- `all` - All contacts regardless of permission

---

### 2. Contact List Resource

**Endpoint:** `GET /v3/contact_lists/{list_id}`

**Fields:**

| Field | Type | Description | Use Case |
|-------|------|-------------|----------|
| `list_id` | UUID | Unique identifier | Track list membership |
| `name` | String | List name | E.g., "Monthly Newsletter", "Major Donors" |
| `description` | String | List description | Document list purpose |
| `membership_count` | Integer | Number of contacts | Monitor list growth |
| `created_at` | DateTime | Creation date | Track list age |
| `updated_at` | DateTime | Last modified | Sync timestamp |

**Example Lists for Nonprofits:**
- "General Newsletter Subscribers"
- "Event Attendees"
- "Monthly Donors"
- "Major Donors ($1000+)"
- "Board Members"

---

### 3. Email Campaign Resource

**Endpoint:** `GET /v3/emails/campaigns/{campaign_id}`

**Campaign Activity Fields:**

| Field | Type | Description | Use Case |
|-------|------|-------------|----------|
| `campaign_activity_id` | UUID | Unique send identifier | Track specific email sends |
| `campaign_id` | UUID | Parent campaign | Group related sends |
| `name` | String | Campaign name | E.g., "2023 Year-End Appeal" |
| `subject` | String | Email subject | Display in reports |
| `from_name` | String | Sender name | Always "Action Center" |
| `from_email` | String | Sender email | Track from address |
| `sent_date` | DateTime | Send timestamp | Campaign timeline |
| `contact_list_ids` | Array | Target lists | Which segments received |

**Example Campaign Names:**
- "2023-12 Year-End Appeal"
- "2024-01 Monthly Newsletter"
- "Colorado Gives Day 2024"
- "Spring Gala Invitation"

---

### 4. Email Engagement Reports

**Endpoint:** `GET /v3/reports/email_reports/{campaign_activity_id}/tracking/summary`

**Aggregate Stats:**
**NOTE:** Actual API field names may be prefixed For example:
- API returns: `em_sends`, `em_opens`, `em_clicks`
- Documentation uses: `sends`, `opens`, `clicks` for readability

Always check the actual API response for exact field names.


| Metric | Type | Description | Analytics Use |
|--------|------|-------------|---------------|
| `sends` | Integer | Total emails sent | Campaign reach |
| `opens` | Integer | Total opens (incl. duplicates) | Initial interest |
| `unique_opens` | Integer | Unique contacts who opened | True open count |
| `open_rate` | Float | % who opened | Campaign effectiveness |
| `clicks` | Integer | Total clicks | Engagement depth |
| `unique_clicks` | Integer | Unique contacts who clicked | Call-to-action success |
| `click_rate` | Float | % who clicked | CTA effectiveness |
| `bounce_count` | Integer | Undeliverable emails | Data quality metric |
| `unsubscribes` | Integer | Opt-outs from this send | List health |
| `spam_complaints` | Integer | Spam reports | Content quality flag |

**Contact-Level Engagement:**

**Endpoint:** `GET /v3/reports/email_reports/{campaign_activity_id}/tracking/sends`
```json
{
  "contact_id": "aa9ff7b0-478d-11e6-8059-d4ae528eb9b6",
  "email_address": "donor@example.com",
  "first_name": "Jane",
  "last_name": "Donor",
  "send_date": "2023-12-05T09:00:15.000Z",
  "open_date": "2023-12-05T10:30:22.000Z",
  "click_date": "2023-12-05T10:32:18.000Z",
  "bounce_type": null,
  "unsubscribe_date": null
}
```

**Engagement Timeline:**
1. `send_date` - Email delivered
2. `open_date` - Contact opened email (NULL if never opened)
3. `click_date` - Contact clicked link (NULL if never clicked)
4. `bounce_type` - Hard/soft bounce (NULL if delivered)
5. `unsubscribe_date` - Opted out (NULL if still subscribed)

**Use Cases:**
- **Donor Engagement Score:** Calculate based on open/click frequency
- **Campaign Attribution:** Did email drive donation within 24-48 hours?
- **Re-engagement Campaigns:** Target contacts who haven't opened in 6 months
- **VIP Identification:** Contacts with high engagement rates

---

### 5. Custom Fields Schema

**Endpoint:** `GET /v3/contact_custom_fields`

**Field Definition:**

| Field | Type | Description |
|-------|------|-------------|
| `custom_field_id` | UUID | Unique identifier |
| `label` | String | Display name |
| `type` | Enum | Data type |
| `position` | Integer | Display order |

**Supported Types:**

| Type | Description | Max Length | Example |
|------|-------------|------------|---------|
| `string` | Text value | 50 chars | "Monthly Donor" |
| `date` | ISO date | N/A | "2023-11-15" |
| `number` | Numeric | N/A | 250.00 |
| `currency` | Money amount | N/A | 1000.00 |
| `single_select` | Dropdown | N/A | "Gold\|Silver\|Bronze" |
| `multi_select` | Checkboxes | N/A | "Events,Newsletter,Volunteer" |

**Recommended Custom Fields for Nonprofits:**

| Field Name | Type | Purpose |
|------------|------|---------|
| `DonorType` | single_select | "Individual\|Corporate\|Foundation" |
| `LastDonationDate` | date | Track most recent gift |
| `LastDonationAmount` | currency | Track most recent gift size |
| `TotalLifetimeGiving` | currency | Cumulative giving |
| `DonorSince` | date | First gift date |
| `PreferredContact` | single_select | "Email\|Phone\|Mail" |
| `Interests` | multi_select | "Education,Housing,Food" |
| `VolunteerStatus` | single_select | "Active\|Inactive\|Interested" |

**Character Limit Workaround:**
For data >50 chars, use multiple fields:
- `Notes_Part1` (50 chars)
- `Notes_Part2` (50 chars)
- `Notes_Part3` (50 chars)

---

### 6. Tags Schema

**Endpoint:** `GET /v3/contact_tags`

**Tag Object:**

| Field | Type | Description |
|-------|------|-------------|
| `tag_id` | UUID | Unique identifier |
| `name` | String | Tag name |
| `contacts_count` | Integer | # contacts with tag |
| `created_at` | DateTime | Creation date |

**Example Tag Structure:**

**Donor Tiers:**
- `Major Donor ($10K+)`
- `Mid-Level Donor ($1K-$10K)`
- `Annual Donor ($100-$1K)`
- `Monthly Donor`

**Engagement Level:**
- `Highly Engaged`
- `Moderately Engaged`
- `Low Engagement`
- `Lapsed Donor`

**Campaign Source:**
- `Colorado Gives Day 2024`
- `Spring Gala 2024`
- `Direct Mail Response`

**Program Interest:**
- `Food Security`
- `Housing Assistance`
- `Youth Programs`

---

### 7. Pagination Schema

All collection endpoints return paginated results with cursor-based navigation.

**Response Structure:**
```json
{
  "contacts": [...],
  "_links": {
    "next": {
      "href": "/v3/contacts?limit=50&cursor=bGltaXQ9NSZuZXh0PTI..."
    }
  },
  "contacts_count": 5000
}
```

**Query Parameters:**

| Parameter | Type | Default | Max | Description |
|-----------|------|---------|-----|-------------|
| `limit` | Integer | 50 | 500 | Results per page |
| `cursor` | String | - | - | Opaque pagination token |
| `include_count` | Boolean | false | - | Return total count (slower) |

**Pagination Logic:**
```python
all_contacts = []
url = "https://api.cc.email/v3/contacts?limit=500"

while url:
    response = requests.get(url, headers=headers)
    data = response.json()
    all_contacts.extend(data['contacts'])
    
    # Get next page URL
    url = data.get('_links', {}).get('next', {}).get('href')
    if url:
        url = f"https://api.cc.email{url}"
```

---

### 8. Query Filters

**GET /v3/contacts** supports filtering:

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `email` | String | Exact email match | `?email=donor@example.com` |
| `status` | Enum | Contact status | `?status=active` |
| `lists` | UUID | Filter by list | `?lists=d13d60d0-f256-11e8` |
| `segment_id` | UUID | Filter by segment | `?segment_id=5f6a7b8c-9d0e` |
| `updated_after` | DateTime | Modified since | `?updated_after=2024-02-01T00:00:00Z` |
| `updated_before` | DateTime | Modified before | `?updated_before=2024-02-05T23:59:59Z` |
| `include` | CSV | Include subresources | `?include=custom_fields,list_memberships` |

### Contact Filtering

**Filter by `permission_to_send` (actual field on contact):**
- `explicit` - Active, can email ✅
- `implicit` - Active, can email ✅  
- `pending_confirmation` - Awaiting opt-in ⏳
- `temp_hold` - Temporary suspension ⚠️
- `unsubscribed` - Do not email ❌

**Filter by `status` query parameter:**
- `status=active` - Returns contacts with `explicit` or `implicit` permission
- `status=unsubscribed` - Returns contacts who opted out
- `status=all` - Returns all contacts regardless of permission

**Incremental Sync Query:**
```
GET /v3/contacts?updated_after=2024-02-04T00:00:00Z
                 &status=active
                 &include=custom_fields,list_memberships
                 &limit=500
```

---

### Database Schema Recommendations

**PostgreSQL Tables:**
```sql
-- Main contacts table
CREATE TABLE cc_contacts (
    contact_id UUID PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    permission_to_send VARCHAR(50),
    opt_in_date TIMESTAMP,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    company_name VARCHAR(100),
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    last_synced_at TIMESTAMP DEFAULT NOW()
);

-- List memberships (many-to-many)
CREATE TABLE cc_list_memberships (
    id SERIAL PRIMARY KEY,
    contact_id UUID REFERENCES cc_contacts(contact_id),
    list_id UUID NOT NULL,
    list_name VARCHAR(255),
    status VARCHAR(50),
    joined_at TIMESTAMP,
    UNIQUE(contact_id, list_id)
);

-- Custom fields (EAV pattern)
CREATE TABLE cc_custom_fields (
    id SERIAL PRIMARY KEY,
    contact_id UUID REFERENCES cc_contacts(contact_id),
    custom_field_id UUID NOT NULL,
    field_name VARCHAR(100),
    field_value TEXT,
    UNIQUE(contact_id, custom_field_id)
);

-- Tags (many-to-many)
CREATE TABLE cc_contact_tags (
    id SERIAL PRIMARY KEY,
    contact_id UUID REFERENCES cc_contacts(contact_id),
    tag_id UUID NOT NULL,
    tag_name VARCHAR(100),
    tagged_at TIMESTAMP,
    UNIQUE(contact_id, tag_id)
);

-- Email campaigns
CREATE TABLE cc_campaigns (
    campaign_activity_id UUID PRIMARY KEY,
    campaign_id UUID,
    name VARCHAR(255),
    subject VARCHAR(500),
    sent_date TIMESTAMP,
    sends INTEGER,
    unique_opens INTEGER,
    open_rate DECIMAL(5,2),
    unique_clicks INTEGER,
    click_rate DECIMAL(5,2),
    unsubscribes INTEGER,
    last_synced_at TIMESTAMP DEFAULT NOW()
);

-- Contact-level engagement
CREATE TABLE cc_contact_engagement (
    id SERIAL PRIMARY KEY,
    contact_id UUID REFERENCES cc_contacts(contact_id),
    campaign_activity_id UUID,
    send_date TIMESTAMP,
    open_date TIMESTAMP,
    click_date TIMESTAMP,
    bounce_type VARCHAR(50),
    unsubscribe_date TIMESTAMP,
    UNIQUE(contact_id, campaign_activity_id)
);
```

---

### Data Quality Notes

**Email Address Normalization:**
- Constant Contact stores emails as provided (case-sensitive)
- Normalize to lowercase for matching: `email.lower()`
- Trim whitespace: `email.strip()`

**UUID Handling:**
- Always store as UUID type or CHAR(36)
- Never parse or manipulate UUIDs
- Use exact string matching

**Date Parsing:**
```python
from datetime import datetime

# Parse ISO-8601 UTC
dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
```

**Null Handling:**
- Missing subresources return empty arrays `[]`
- Missing values return `null`
- Check for existence before accessing nested fields

**Character Encoding:**
- API uses UTF-8
- Handle special characters in names (e.g., José, Zoë, François)
- Escape SQL properly to prevent injection

---

### Rate Limits & Quotas

**Standard Account:**
- 10,000 API calls per day
- 10 calls per second (burst)

**Technology Partner:**
- 100,000 API calls per day, higher limits available
- 100 calls per second (burst)
- Burst protection under heavy load

**Bulk Operations:**
Use bulk endpoints when available:
- `POST /v3/activities/contacts_file_import` (import up to 40,000 contacts)
- Better than looping individual `POST /v3/contacts` calls

**Rate Limit Error Handling:**
```python
if response.status_code == 429:
    retry_after = int(response.headers.get('Retry-After', 60))
    time.sleep(retry_after)
    # Retry request
```

**Best Practices:**
- Use bulk endpoints when importing >100 contacts
- Implement exponential backoff for retries
- Cache frequently accessed data
- Use `updated_after` filters to minimize API calls