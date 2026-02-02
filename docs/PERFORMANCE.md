# Performance Optimization Documentation

## Current Performance Characteristics

### Data Volume
- Donors: 1,000 records (~250 KB)
- Campaigns: 10 records (~1 KB)
- Donations: 5,000 records (~400 KB)
- **Total**: ~6,010 records (~650 KB)

### Query Performance Baseline

**Test Environment:**
- PostgreSQL 17
- Local machine
- No concurrent users

**Sample Query Times:**
```sql
-- Top 10 donors by total giving
SELECT donor_id, SUM(amount)
FROM donations
GROUP BY donor_id
ORDER BY SUM(amount) DESC
LIMIT 10;
-- Execution time: <10ms
```

---

## Indexing Strategy

### Current Indexes

1. **idx_donations_donor** (donations.donor_id)
   - **Purpose:** Speed up donor-specific queries
   - **Use case:** "Show all donations by donor X"
   - **Impact:** O(log n) vs O(n) for 5,000 rows

2. **idx_donations_campaign** (donations.campaign_id)
   - **Purpose:** Speed up campaign analysis
   - **Use case:** "Show all donations to campaign Y"
   - **Impact:** O(log n) lookup

3. **idx_donations_date** (donations.donation_date)
   - **Purpose:** Speed up time-range queries
   - **Use case:** "Show donations in Q4 2025"
   - **Impact:** Fast date filtering

4. **idx_donors_email** (donors.email)
   - **Purpose:** Fast email lookups
   - **Use case:** "Find donor by email"
   - **Impact:** Unique lookups in O(log n)

### When Indexes Help

Indexes improve performance for:
- JOIN operations (FK columns)
- WHERE clauses on indexed columns
- ORDER BY on indexed columns
- GROUP BY on indexed columns

Indexes don't help with:
- Full table scans
- Calculations on every row
- Small tables (<1,000 rows)

---

## Scalability Considerations

### Current Scale (Development)
- Dataset: ~6K records
- Expected query time: <50ms
- Concurrent users: 1 (you!)

### Future Scale (Production Estimate)
- Donors: 10,000 - 50,000
- Donations: 50,000 - 500,000 per year
- Campaigns: 20 - 100 per year

### Performance Projections

**At 50K donors, 500K donations:**
- Index lookups: Still O(log n) ~ <20ms
- Full table scans: Could reach 200-500ms
- Complex JOINs: 100-300ms

**Mitigation strategies:**
1. Use indexes on all FK columns (✅ done)
2. Implement dbt incremental models (⏭️ Week 3)
3. Aggregate tables for common queries (⏭️ Week 5)
4. Partition large tables by year (⏭️ if needed)

---

## ETL Performance

### Current Load Times

**generate_sample_data.py:**
- Execution time: ~2-3 seconds
- Memory usage: <50 MB

**load_data.py:**
- Donors: ~0.5 seconds
- Campaigns: <0.1 seconds
- Donations: ~1-2 seconds
- **Total**: ~3-5 seconds

### Batch Insert Optimization
```python
# Using execute_batch with page_size=100
execute_batch(cursor, insert_sql, records, page_size=100)
```

**Why this matters:**
- Individual INSERTs: 5,000 network round-trips = slow
- Batch of 100: 50 round-trips = 100x faster
- Balance: Smaller batches = more commits (safer), larger = faster

**Current choice:** 100 rows per batch
- Good balance for current scale
- Safe rollback point if errors
- Fast enough (<5 seconds total)

### Future Optimizations

**If data grows to 100K+ donations:**
1. Increase batch size to 1,000
2. Use COPY command instead of INSERT
3. Disable indexes during load, rebuild after
4. Use multi-threading for parallel loads

---

## Query Optimization Patterns

### Good Query Patterns
```sql
-- Uses index on donor_id
SELECT * FROM donations WHERE donor_id = 123;

-- Uses index on donation_date
SELECT * FROM donations 
WHERE donation_date >= '2025-01-01'
  AND donation_date < '2026-01-01';

-- Index helps JOIN
SELECT d.first_name, SUM(don.amount)
FROM donors d
JOIN donations don ON d.donor_id = don.donor_id
GROUP BY d.donor_id, d.first_name;
```

### Anti-Patterns to Avoid
```sql
-- Function on indexed column prevents index use
SELECT * FROM donations 
WHERE YEAR(donation_date) = 2025;  -- BAD

-- Better:
WHERE donation_date >= '2025-01-01' 
  AND donation_date < '2026-01-01';  -- GOOD

-- OR clause can prevent index use
SELECT * FROM donors
WHERE first_name = 'John' OR last_name = 'Smith';  -- SLOW

-- SELECT * on large tables
SELECT * FROM donations;  -- Fetches all columns
-- Better: SELECT only needed columns
SELECT donation_id, amount FROM donations;
```

---

## Monitoring & Metrics

### Key Metrics to Track

1. **Query execution time**
   - Target: <100ms for most queries
   - Alert: >1 second

2. **Table sizes**
```sql
   SELECT 
     pg_size_pretty(pg_total_relation_size('donations'))
   AS size;
```

3. **Index usage**
```sql
   SELECT schemaname, tablename, indexname, idx_scan
   FROM pg_stat_user_indexes
   ORDER BY idx_scan;
```

4. **Slow query log**
   - Enable in PostgreSQL config
   - Log queries > 100ms

### Future: dbt Performance

When you add dbt (Week 3):
- Incremental models reduce re-processing
- Model timing built into dbt
- Test execution times tracked
- Compile time vs run time separation

---

## Caching Strategy (Future)

**Not implemented yet, but planned:**

1. **Application-level caching**
   - Cache frequently accessed aggregates
   - TTL: 1 hour for dashboard queries
   - Invalidate on data updates

2. **Materialized views (PostgreSQL)**
   - Pre-compute expensive aggregations
   - Refresh nightly
   - Example: donor_summary, campaign_totals

3. **dbt incremental models**
   - Only process new/changed data
   - Massive speedup for large datasets

---

## Capacity Planning

### Storage Growth Estimates

**Current:**
- Total database size: ~1 MB

**Projected (1 year):**
- New donors: 2,000/year
- New donations: 20,000/year
- Growth: ~200 KB/year
- **Total after 5 years**: ~2 MB (tiny!)

**Realistic nonprofit (5 years):**
- Donors: 25,000
- Donations: 250,000
- Size: ~50-100 MB
- **Still small!** Most databases handle this easily.

### When to Worry About Performance

Don't optimize prematurely for:
- <100K total records
- <10 concurrent users
- Queries completing <500ms

Start optimizing when:
- Queries regularly >1 second
- 100K+ records in main tables
- 50+ concurrent users
- Dashboard load times >3 seconds

**Current status:** Way below these thresholds!

---

## Lessons Learned

1. **Indexes are cheap at small scale**
   - Added 4 indexes, minimal impact on insert speed
   - Huge benefit for read queries

2. **Batch operations matter**
   - execute_batch 100x faster than individual inserts

3. **Foreign keys enforce integrity**
   - Small performance cost on INSERT
   - Huge benefit: prevents bad data

4. **Premature optimization**
   - Current dataset: Everything is fast
   - Focus on correct logic first
   - Optimize when actual bottlenecks appear

---

## Next Steps (Week 3+)

1. **Add dbt incremental models**
   - Only transform new data
   - Reduce processing time 10-100x

2. **Create aggregate tables**
   - Pre-calculate common metrics
   - "donor_summary" table updated nightly

3. **Monitor query patterns**
   - Log slow queries
   - Add indexes based on actual usage

4. **Load testing**
   - Simulate 10 concurrent dashboard users
   - Identify bottlenecks under load