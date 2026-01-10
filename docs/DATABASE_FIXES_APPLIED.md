# Database Schema Fixes Applied

**Date**: January 2025  
**Status**: ✅ All fixes applied

---

## Summary

This document lists all database schema fixes that were applied to align the codebase with the documented schema in `02_DATABASE_SCHEMA_AND_MIGRATION.md`.

---

## Fixes Applied

### 1. ✅ Added Missing `broker_order_id` Field to Order Model

**File**: `database/models.py` (line 190)

**Change**: Added `broker_order_id` column to track external broker order IDs (Shoonya/Upstox).

```python
broker_order_id = Column(String(100), nullable=True)  # Shoonya/Upstox order ID
```

**Migration**: Use `scripts/migrate_add_missing_fields.py` to add this column to existing databases.

---

### 2. ✅ Added Missing Technical Indicators to MarketDataDaily

**File**: `database/models.py` (lines 70-71, 81)

**Changes**: Added three missing indicators to complete the 29-indicator set:
- `mfi` (Money Flow Index) - line 81
- `ema_20` (20-period EMA) - line 70
- `ema_50` (50-period EMA) - line 71

**Migration**: Use `scripts/migrate_add_missing_fields.py` to add these columns to existing databases.

---

### 3. ✅ Added Nifty500Sector Model

**File**: `database/models.py` (lines 368-375)

**Change**: Added new model class for Nifty 500 sector reference data.

```python
class Nifty500Sector(Base):
    """Nifty 500 sector and industry reference data."""
    __tablename__ = "nifty500_sectors"
    
    symbol = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    sector = Column(String(100), nullable=True, index=True)
    industry = Column(String(100), nullable=True, index=True)
    market_cap_rank = Column(Integer, nullable=True)
```

**Migration**: Use `scripts/migrate_add_missing_fields.py` to create this table in existing databases.

---

### 4. ✅ Fixed verify_database.py Column Checks

**File**: `scripts/verify_database.py` (line 54)

**Change**: Fixed incorrect column names in verification checks:
- Changed `"symbol"` → `"stock_id"` for orders table
- Changed `"status"` → `"order_status"` for orders table

**Also Updated**: Added missing tables to expected_tables list:
- `nifty500_sectors`
- `news_articles`
- `sentiment_scores`
- `macro_stock_sentiment`
- `news_sources`

---

### 5. ✅ Added Unique Constraints

**Files**: `database/models.py`

**Changes**: Added unique constraints to prevent duplicate data:

1. **MarketDataDaily** (line 97):
   ```python
   UniqueConstraint('stock_id', 'date', name='uq_market_data_daily_stock_date')
   ```

2. **MarketDataIntraday** (line 120):
   ```python
   UniqueConstraint('stock_id', 'timestamp', 'interval', name='uq_market_data_intraday_stock_timestamp_interval')
   ```

3. **SentimentScore** (line 328):
   ```python
   UniqueConstraint('stock_id', 'date', name='uq_sentiment_scores_stock_date')
   ```

**Note**: These constraints are enforced at the database level. Existing databases will need to be migrated or cleaned before applying constraints.

---

### 6. ✅ Created FTS5 Virtual Table Migration Script

**File**: `scripts/migrate_add_fts5_table.py` (new file)

**Purpose**: Creates SQLite FTS5 virtual table for full-text search on news articles.

**Features**:
- Creates `news_articles_fts` virtual table
- Populates with existing news articles
- Creates triggers to keep FTS5 table in sync with `news_articles` table

**Usage**:
```bash
python scripts/migrate_add_fts5_table.py
```

---

### 7. ✅ Created Migration Script for Missing Fields

**File**: `scripts/migrate_add_missing_fields.py` (new file)

**Purpose**: Adds missing fields to existing databases:
- `broker_order_id` to `orders` table
- `mfi`, `ema_20`, `ema_50` to `market_data_daily` table
- Creates `nifty500_sectors` table if missing

**Usage**:
```bash
python scripts/migrate_add_missing_fields.py
```

---

## Migration Order

For existing databases, run migrations in this order:

1. **First**: `scripts/migrate_add_missing_fields.py`
   - Adds missing columns and tables

2. **Second**: `scripts/migrate_add_sentiment_tables.py` (if not already run)
   - Adds sentiment analysis tables

3. **Third**: `scripts/migrate_add_fts5_table.py`
   - Adds full-text search capability

4. **Finally**: `scripts/verify_database.py`
   - Verifies all changes were applied correctly

---

## Verification

After applying fixes, verify the database:

```bash
python scripts/verify_database.py
```

This will check:
- ✅ All tables exist
- ✅ All required columns are present
- ✅ Database integrity
- ✅ Foreign key constraints

---

## Breaking Changes

⚠️ **Note**: The unique constraints added may cause issues if your existing database has duplicate data. Before applying constraints:

1. Check for duplicates:
   ```sql
   SELECT stock_id, date, COUNT(*) 
   FROM market_data_daily 
   GROUP BY stock_id, date 
   HAVING COUNT(*) > 1;
   ```

2. Remove duplicates if found

3. Then apply migrations

---

## Files Modified

1. `database/models.py` - Added fields, constraints, and new model
2. `scripts/verify_database.py` - Fixed column checks and added tables
3. `scripts/migrate_add_fts5_table.py` - New migration script
4. `scripts/migrate_add_missing_fields.py` - New migration script

---

## Next Steps

1. ✅ All fixes applied to codebase
2. ⏳ Run migrations on existing databases (if any)
3. ⏳ Update any code that uses Order model to handle `broker_order_id`
4. ⏳ Update indicator calculation code to include `mfi`, `ema_20`, `ema_50`
5. ⏳ Test database operations with new constraints

---

## References

- Schema Documentation: `docs/02_DATABASE_SCHEMA_AND_MIGRATION.md`
- Original Issue Report: Database verification findings
