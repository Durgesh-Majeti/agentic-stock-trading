# Maintenance & Upgrade Guide

**Version**: 1.0  
**Last Updated**: January 2025

---

## Table of Contents

1. [Regular Maintenance](#regular-maintenance)
2. [Upgrade Procedures](#upgrade-procedures)
3. [Version Management](#version-management)
4. [Dependency Updates](#dependency-updates)
5. [Database Migrations](#database-migrations)
6. [Model Updates](#model-updates)
7. [Rollback Procedures](#rollback-procedures)
8. [Best Practices](#best-practices)

---

## Regular Maintenance

### Daily Tasks

1. **Check Logs**
   ```bash
   tail -f logs/trading_app.log
   ```

2. **Verify Backups**
   ```bash
   ls -lh backups/
   ```

3. **Monitor Performance**
   - Check signal generation rate
   - Monitor API response times
   - Review error rates

### Weekly Tasks

1. **Database Maintenance**
   ```bash
   python scripts/maintain_database.py
   ```

2. **Clean Old Logs**
   ```bash
   find logs/ -name "*.log" -mtime +30 -delete
   ```

3. **Review Metrics**
   - Win rate
   - Profit factor
   - Drawdown

### Monthly Tasks

1. **Full System Backup**
2. **Security Audit**
3. **Performance Review**
4. **Documentation Update**

---

## Upgrade Procedures

### Pre-Upgrade Checklist

- [ ] Backup database
- [ ] Backup configuration
- [ ] Review changelog
- [ ] Test in development
- [ ] Notify stakeholders

### Upgrade Steps

1. **Stop System**
   ```bash
   # Stop main process
   pm2 stop trading-bot
   # Or
   pkill -f main.py
   ```

2. **Backup Current State**
   ```bash
   # Backup database
   cp data/trading.db backups/pre_upgrade_$(date +%Y%m%d).db
   
   # Backup config
   cp .env backups/.env.backup
   ```

3. **Update Code**
   ```bash
   git pull origin main
   # Or download new version
   ```

4. **Update Dependencies**
   ```bash
   pip install -r requirements.txt --upgrade
   ```
   
   **Note**: After updating, if sentiment analysis tables are missing:
   ```bash
   python scripts/migrate_add_sentiment_tables.py
   ```

5. **Run Migrations**
   ```bash
   python scripts/migrate_database.py
   python scripts/migrate_add_sentiment_tables.py  # If not already done
   ```

6. **Test System**
   ```bash
   python scripts/test_system.py
   ```

7. **Start System**
   ```bash
   pm2 start trading-bot
   ```

8. **Monitor**
   - Watch logs for errors
   - Verify all agents working
   - Check performance metrics

---

## Version Management

### Versioning Scheme

**Format**: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes

### Current Version

Track in `VERSION` file:
```
1.0.0
```

### Changelog

Maintain `CHANGELOG.md`:
```markdown
# Changelog

## [1.0.0] - 2025-01-15
### Added
- Initial release
- 5-agent architecture
- Telegram integration
```

---

## Dependency Updates

### Check for Updates

```bash
pip list --outdated
```

### Update Strategy

1. **Test Updates**: Update in dev environment first
2. **One at a Time**: Update dependencies incrementally
3. **Test Thoroughly**: Run all tests after updates
4. **Document Changes**: Note any breaking changes

### Critical Dependencies

- **CrewAI**: Agent framework
- **LangChain**: LLM integration
- **SQLAlchemy**: Database ORM
- **python-telegram-bot**: Telegram bot

---

## Database Migrations

### Migration Script Template

```python
# scripts/migrations/v1_0_to_v1_1.py
import sqlite3
from datetime import datetime

def migrate():
    """Migrate database from v1.0 to v1.1."""
    conn = sqlite3.connect('data/trading.db')
    cursor = conn.cursor()
    
    try:
        # Add new column
        cursor.execute("ALTER TABLE trades ADD COLUMN notes TEXT")
        
        # Create index
        cursor.execute("CREATE INDEX idx_trades_notes ON trades(notes)")
        
        # Update version
        cursor.execute("UPDATE schema_version SET version = '1.1'")
        
        conn.commit()
        print("Migration successful")
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
        raise
    finally:
        conn.close()
```

### Migration Checklist

- [ ] Backup database
- [ ] Test migration on copy
- [ ] Document changes
- [ ] Update schema documentation
- [ ] Test rollback procedure

---

## Model Updates

### Updating LLM Models

1. **Check Model Availability**
   ```python
   python scripts/list_ollama_models.py
   ```

2. **Update Configuration**
   ```env
   OLLAMA_STRATEGY_MODEL=new_model:tag
   ```

3. **Test New Model**
   ```python
   python scripts/test_model.py --model new_model:tag
   ```

4. **Gradual Rollout**
   - Test with small subset
   - Monitor performance
   - Compare with old model
   - Full rollout if better

---

## Rollback Procedures

### Database Rollback

```bash
# Restore from backup
cp backups/pre_upgrade_20250115.db data/trading.db
```

### Code Rollback

```bash
# Git rollback
git checkout <previous-commit>

# Or restore from backup
cp -r backups/code_backup/* .
```

### Configuration Rollback

```bash
# Restore config
cp backups/.env.backup .env
```

### Full System Rollback

1. Stop system
2. Restore database
3. Restore code
4. Restore configuration
5. Restart system
6. Verify functionality

---

## Best Practices

### Before Upgrades

1. **Always Backup**: Database and configuration
2. **Test First**: Use development environment
3. **Read Changelog**: Understand changes
4. **Plan Downtime**: Schedule during off-hours
5. **Document**: Record upgrade steps

### During Upgrades

1. **Follow Steps**: Don't skip steps
2. **Monitor Logs**: Watch for errors
3. **Test Immediately**: Verify functionality
4. **Have Rollback Ready**: Know how to revert

### After Upgrades

1. **Monitor Closely**: Watch for 24 hours
2. **Verify Metrics**: Check performance
3. **Update Documentation**: Reflect changes
4. **Communicate**: Notify stakeholders

---

## Troubleshooting Upgrades

### Common Issues

**Issue**: Migration fails
**Solution**: Restore backup, check migration script

**Issue**: Dependencies conflict
**Solution**: Use virtual environment, check versions

**Issue**: Performance degradation
**Solution**: Rollback, investigate changes

---

## Maintenance Schedule

### Recommended Schedule

- **Daily**: Log review, backup verification
- **Weekly**: Database maintenance, log cleanup, news article cleanup (30+ days old)
- **Monthly**: Full backup, security audit, sentiment data review
- **Quarterly**: Major updates, performance review, macro sentiment mapping cleanup (90+ days old)
- **Annually**: Architecture review, major upgrades

---

**Documentation Complete!**

All 8 comprehensive documents created for the project.
