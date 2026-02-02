# DataBridge Architecture Documentation

## System Overview

DataBridge is an open-source analytics framework for nonprofit organizations, designed to unify fragmented donor data across multiple systems into a centralized, queryable database.

**Current Version:** 1.0 (Weeks 1-2 Complete)
**Status:** Development - Foundation Phase Complete

---

## Architecture Layers
```
┌─────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                   │
│                   (Future: Streamlit)                   │
│   Self-service dashboards for portfolio holders         │
└────────────┬────────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────────┐
│                   TRANSFORMATION LAYER                  │
│                    (Future: dbt Core)                   │
│   Business logic, dimensional models, metrics           │
└────────────┬────────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────────┐
│                    STORAGE LAYER                        │
│                   (PostgreSQL 17)                       │
│   Normalized relational database (3NF)                  │
└────────────┬────────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────────┐
│                      ETL LAYER                          │
│                 (Python + psycopg2)                     │
│   Extract from CSV → Load to database                   │
└────────────┬────────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────────┐
│                   DATA GENERATION                       │
│                  (Python + Faker)                       │
│   Synthetic nonprofit data for development              │
└─────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Current Implementation

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Language | Python | 3.13 | ETL scripting, data generation |
| Database | PostgreSQL | 17 | Data warehouse |
| DB Driver | psycopg2 | 2.9.x | Python-PostgreSQL connector |
| Data Processing | pandas | 2.x | DataFrame operations |
| Synthetic Data | Faker | Latest | Realistic test data generation |
| Version Control | Git/GitHub | - | Source code management |

### Future Additions (Weeks 3+)

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Transformations | dbt Core | SQL-based data modeling |
| Dashboard | Streamlit | Self-service analytics UI |
| Orchestration | Airflow (maybe) | Workflow scheduling |

---

## Design Principles

1. **Modularity**
   - Each script has single responsibility
   - Functions are composable and reusable
   - Easy to test and maintain

2. **Idempotency**
   - Scripts can be run multiple times safely
   - DROP IF EXISTS before CREATE
   - Clear state on each run

3. **Error Handling**
   - All database operations wrapped in try/except
   - Transaction rollback on failures
   - Clear error messages for debugging

4. **Data Integrity**
   - Foreign keys enforce relationships
   - Primary keys prevent duplicates
   - Constraints validate business rules

5. **Performance**
   - Batch inserts over individual rows
   - Indexes on frequently queried columns
   - Efficient DataFrame→SQL transformations

6. **Privacy**
   - Synthetic data only (no real PII)
   - .gitignore excludes data files
   - Safe for public GitHub

---

## Data Flow

### Phase 1: Mock Data Generation (Week 1)
```
generate_sample_data.py
  ↓
Faker generates realistic data
  ↓
pandas DataFrames created
  ↓
Export to CSV files
  ├── donors.csv (1,000 rows)
  ├── donations.csv (5,000 rows)
  └── campaigns.csv (10 rows)
```

### Phase 2: Schema Setup (Week 2)
```
database_setup.py
  ↓
Connect to PostgreSQL
  ↓
DROP existing tables (if any)
  ↓
CREATE tables with constraints
  ├── donors (PK, indexes)
  ├── campaigns (PK)
  └── donations (PK, 2x FK, 3x indexes)
  ↓
Verify schema creation
```

### Phase 3: ETL (Week 2)
```
load_data.py
  ↓
Read CSV files (pandas)
  ↓
Transform to tuples
  ↓
Batch INSERT to PostgreSQL
  ├── donors first (no dependencies)
  ├── campaigns (no dependencies)
  └── donations last (depends on both)
  ↓
Verify row counts
  ↓
Run validation queries
```

---

## Security Considerations

### Current State

✅ **Implemented:**
- No hardcoded passwords (environment variables ready)
- .gitignore prevents committing sensitive data
- Synthetic data only (no real PII)
- Database credentials in separate config dict

⚠️ **Not Yet Implemented:**
- Credentials in environment variables (.env file)
- Role-based access control in database
- SSL/TLS for database connections
- Input sanitization (low risk with controlled data)

### Future Security Enhancements

1. **Environment Variables**
```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   
   DB_CONFIG = {
       'password': os.getenv('DB_PASSWORD')
   }
```

2. **Secrets Management**
   - Use .env file (not committed to git)
   - Or use secret management service (AWS Secrets Manager, etc.)

3. **Least Privilege**
   - Create read-only user for dashboards
   - Create write-only user for ETL
   - Separate admin user for schema changes

---

## Scalability & Future Growth

### Current Capacity
- Dataset: 6,010 records
- Database size: ~1 MB
- Query time: <50ms
- Concurrent users: 1

### Projected Growth (5 Years)
- Donors: 1,000 → 25,000 (25x)
- Donations: 5,000 → 250,000 (50x)
- Database size: 1 MB → 100 MB
- **Conclusion:** PostgreSQL easily handles this scale

### Architectural Patterns for Scale

**When to add dbt (Week 3):**
- ✅ Need to transform raw data
- ✅ Business logic becomes complex
- ✅ Want to avoid duplicate query logic
- ✅ Need testing and documentation

**When to add caching:**
- Dataset >100K records
- Queries >500ms
- Dashboard >10 concurrent users

**When to add partitioning:**
- Table >1M rows
- Queries mostly time-range based
- Data has natural time boundaries

**Current assessment:** We're nowhere near these thresholds yet!

---

## Error Recovery & Data Quality

### Current Validation

1. **Generation Phase:**
   - Record counts verified
   - Data types validated
   - Referential integrity checked

2. **Load Phase:**
   - Row counts compared (CSV vs DB)
   - Foreign keys validated by database
   - Aggregate totals verified

3. **Query Phase:**
   - Manual spot-checks via pgAdmin
   - Sample queries run and reviewed

### Future Automated Testing
```python
# tests/test_data_quality.py (Week 9+)

def test_no_orphaned_donations():
    """Ensure all donations have valid donors"""
    result = db.query("""
        SELECT COUNT(*)
        FROM donations d
        LEFT JOIN donors don ON d.donor_id = don.donor_id
        WHERE don.donor_id IS NULL
    """)
    assert result == 0

def test_positive_amounts():
    """Ensure all donations are positive"""
    result = db.query("""
        SELECT COUNT(*)
        FROM donations
        WHERE amount <= 0
    """)
    assert result == 0
```

---

## Deployment Strategy

### Current (Local Development)
- PostgreSQL on local machine
- Manual script execution
- No automation

### Future (Production-Ready)

**Option A: Cloud-Hosted Database**
- AWS RDS PostgreSQL or Supabase
- Scheduled ETL via GitHub Actions or Airflow
- Streamlit Cloud for dashboard

**Option B: Full Cloud Stack**
- Snowflake or BigQuery (data warehouse)
- dbt Cloud (transformations)
- Looker or Mode (dashboards)

**Recommendation:** Start with Option A (cheaper, simpler)

---

## Maintenance & Operations

### Current Manual Tasks
- Run generate_sample_data.py when data changes
- Run database_setup.py when schema changes
- Run load_data.py to refresh data
- Manual queries in pgAdmin

### Future Automation (Week 9+)
- Scheduled daily ETL runs
- Automatic data quality checks
- Alert on failures
- Dashboard auto-refresh

### Monitoring Needs
- ⏭️ Query performance tracking
- ⏭️ Data freshness monitoring
- ⏭️ Error logging and alerting
- ⏭️ Database backup strategy

---

## Extension Points

### Areas for Customization

1. **Additional Data Sources**
   - Email platform APIs (Mailchimp, Constant Contact)
   - Social media (Facebook, LinkedIn)
   - Accounting systems (QuickBooks)
   - Event management (Eventbrite)

2. **Business Logic**
   - Monthly donor definition (in dbt)
   - Donor scoring algorithms
   - Churn prediction models
   - Upgrade potential calculation

3. **Dashboards**
   - Portfolio holder views
   - Campaign comparisons
   - Executive summaries
   - Board reports

---

## Known Limitations

1. **Synthetic Data Only**
   - Not connected to real CRM yet
   - All data is fabricated

2. **Manual Processes**
   - No scheduling/automation
   - Manual script execution required

3. **Single User**
   - No multi-user access controls
   - No authentication system

4. **No Historical Tracking**
   - Overwrites data on each load
   - No slowly changing dimensions (yet)

5. **Limited Testing**
   - Manual validation only
   - No automated test suite

**Note:** These are intentional tradeoffs for a Week 2 development version. All will be addressed in future phases.

---

## Documentation Standards

### Code Documentation
- Docstrings on all functions
- Inline comments for complex logic
- Type hints where helpful (future)

### Data Documentation
- Data dictionary maintained
- Column descriptions
- Business rules documented

### Process Documentation
- This architecture doc
- Performance guide
- Workflow diagrams

---

## Changelog

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-01-21 | 1.0 | Initial architecture, Weeks 1-2 complete | Eliška Merchant-Dest |

---

## References

- [Project README](../README.md)
- [Data Dictionary](DATA_DICTIONARY.md)
- [Performance Guide](PERFORMANCE.md)
- [GitHub Repository](https://github.com/eliskamd/nonprofit-data-pipeline)