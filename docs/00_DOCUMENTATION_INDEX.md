# Documentation Index

**Project**: Agentic Stock Trading System  
**Version**: 1.0  
**Last Updated**: January 2025

---

## 📚 Complete Documentation Set

This documentation set provides comprehensive guidance for **creating, maintaining, debugging, and upgrading** the Agentic Stock Trading System.

---

## 📖 Core Documentation

### 1. [Architecture & Design](01_ARCHITECTURE_AND_DESIGN.md)
**Purpose**: System architecture, design principles, and component details

**Contents**:
- System overview and architecture diagrams
- 5-agent architecture details
- Data flow diagrams
- Technology stack
- Integration points
- Scalability considerations

**Use When**: 
- Understanding system design
- Planning new features
- Onboarding new developers
- Architecture decisions

---

### 2. [Database Schema & Migration](02_DATABASE_SCHEMA_AND_MIGRATION.md)
**Purpose**: Complete database schema, migrations, and optimization

**Contents**:
- Complete DDL for all tables
- Table descriptions and relationships
- Indexes and performance optimization
- Data retention policies
- Migration procedures
- Common queries

**Use When**:
- Setting up database
- Adding new tables/columns
- Optimizing queries
- Understanding data structure
- Database maintenance

---

### 3. [Agent Implementation Guide](03_AGENT_IMPLEMENTATION_GUIDE.md)
**Purpose**: Detailed implementation guide for all 5 agents

**Contents**:
- Base agent architecture
- Complete implementation for each agent
- Code examples and patterns
- Error handling
- Testing strategies

**Use When**:
- Implementing agents
- Debugging agent issues
- Adding new agent features
- Understanding agent behavior

---

### 4. [Configuration Reference](04_CONFIGURATION_REFERENCE.md)
**Purpose**: Complete configuration guide and reference

**Contents**:
- All environment variables
- Configuration files
- Model configuration
- Risk parameters
- API credentials setup
- Best practices

**Use When**:
- Setting up environment
- Configuring system
- Troubleshooting config issues
- Understanding settings

---

### 5. [Deployment & Operations](05_DEPLOYMENT_AND_OPERATIONS.md)
**Purpose**: Deployment procedures and operational guidelines

**Contents**:
- Installation steps
- Initial setup
- Running the system
- Monitoring
- Backup & recovery
- Production checklist

**Use When**:
- Deploying system
- Setting up production
- Daily operations
- Monitoring system health

---

### 6. [Troubleshooting & Debugging](06_TROUBLESHOOTING_AND_DEBUGGING.md)
**Purpose**: Common issues, errors, and debugging techniques

**Contents**:
- Common issues and solutions
- Error messages reference
- Debugging techniques
- Log analysis
- Performance issues
- API and database issues

**Use When**:
- Encountering errors
- System not working
- Performance problems
- Debugging issues

---

### 7. [Testing & Quality Assurance](07_TESTING_AND_QUALITY_ASSURANCE.md)
**Purpose**: Testing strategies and quality metrics

**Contents**:
- Testing strategy
- Unit, integration, E2E tests
- Performance testing
- Test data and fixtures
- CI/CD setup
- Quality metrics

**Use When**:
- Writing tests
- Ensuring quality
- Setting up CI/CD
- Performance validation

---

### 8. [Maintenance & Upgrade](08_MAINTENANCE_AND_UPGRADE.md)
**Purpose**: Maintenance procedures and upgrade guides

**Contents**:
- Regular maintenance tasks
- Upgrade procedures
- Version management
- Dependency updates
- Database migrations
- Rollback procedures

**Use When**:
- Performing maintenance
- Upgrading system
- Managing versions
- Planning updates

---

### 9. [Sentiment Analysis System](09_SENTIMENT_ANALYSIS_SYSTEM.md)
**Purpose**: Complete guide to news sentiment analysis integration

**Contents**:
- System architecture and design
- News Sentiment Analyst agent details
- Data sources and integration
- Sentiment analysis methods (DeepSeek R1 7B, FinBERT)
- Macro news propagation to individual stocks
- Database schema for news and sentiment
- Integration with Strategy Specialist
- Implementation guide
- Performance optimization

**Use When**:
- Implementing sentiment analysis
- Understanding macro news propagation
- Configuring news sources
- Integrating sentiment with trading strategy
- Troubleshooting sentiment analysis issues

---

### 10. [Free Sentiment Sources](10_FREE_SENTIMENT_SOURCES.md)
**Purpose**: Comprehensive guide to free news sources and sentiment analysis tools

**Contents**:
- Free RSS news sources (Indian and international)
- Free sentiment analysis models (FinBERT, VADER, TextBlob)
- Free APIs with sentiment analysis (Alpha Vantage, NewsAPI)
- Open source tools and libraries
- Recommended free setup for the system
- Cost comparison and implementation priority

**Use When**:
- Looking for free news sources
- Choosing sentiment analysis tools
- Setting up a cost-effective sentiment system
- Comparing different free options
- Planning implementation with zero cost

---

### 11. [Status and Changelog](11_STATUS_AND_CHANGELOG.md)

### 12. [News Fetching and Storage](12_NEWS_FETCHING_AND_STORAGE.md)
**Purpose**: Complete guide to news fetching, storage, and per-source tracking

**Contents**:
- Per-source tracking system
- Repository methods and usage
- RSS feed status and validation
- Performance optimization
- Monitoring and troubleshooting
- Command reference

**Use When**:
- Setting up news fetching
- Understanding per-source tracking
- Troubleshooting fetch issues
- Monitoring source status
**Purpose**: Current project status, recent changes, and changelog

**Contents**:
- Current development status
- Completed phases summary
- Recent changes and updates
- Next steps and roadmap
- Migration guide for updates
- Testing status
- Known issues and limitations
- Performance metrics

**Use When**:
- Checking current project status
- Understanding what's been completed
- Planning next development steps
- Reviewing recent changes
- Migrating from older versions

---

## 🔧 Setup & Integration Guides

### [Ollama Local Setup](OLLAMA_LOCAL_SETUP.md)
**Purpose**: Complete guide for setting up local Ollama

**Contents**:
- Installation instructions
- Model pulling guide
- Configuration
- Troubleshooting
- Performance tips

**Use When**:
- Setting up Ollama for the first time
- Pulling required models
- Troubleshooting Ollama issues

---

### [API Integration Summary](API_INTEGRATION_SUMMARY.md)
**Purpose**: Overview of all API integrations

**Contents**:
- All API integrations (Shoonya, Upstox, Ollama, Telegram, yfinance)
- Priority and fallback strategies
- Health checks
- Configuration reference

**Use When**:
- Understanding all API integrations
- Setting up multiple APIs
- Troubleshooting API issues

---

### [Telegram Bot Guide](TELEGRAM_BOT_GUIDE.md)
**Purpose**: Complete Telegram bot setup and usage

**Contents**:
- Bot creation and setup
- All commands and usage
- Inline keyboards
- Alerts and notifications
- Security best practices

**Use When**:
- Setting up Telegram bot
- Understanding bot commands
- Implementing bot features
- Troubleshooting bot issues

---

### [Shoonya API Guide](SHOONYA_API_GUIDE.md)
**Purpose**: Complete Shoonya API integration guide

**Contents**:
- Authentication and setup
- API functions
- WebSocket implementation
- Rate limits
- Python examples

**Use When**:
- Integrating Shoonya API
- Understanding API functions
- Troubleshooting API issues

---

### [Upstox API Guide](UPSTOX_API_GUIDE.md)
**Purpose**: Complete Upstox API integration guide

**Contents**:
- OAuth 2.0 authentication
- API functions
- Token management
- Rate limits
- Python examples

**Use When**:
- Integrating Upstox API
- Setting up backup data source
- Understanding API functions

---

## 📋 Project Specifications

### [Project Specification](Project%20specification%20doc.md)
**Purpose**: Original project specification and requirements

**Contents**:
- Complete system architecture
- Agent specifications
- Database schema
- Implementation checklist
- Success criteria

**Use When**:
- Understanding project requirements
- Reference for implementation
- Planning development

---

## 🚀 Quick Start Guides

### [Development Todo List](../DEVELOPMENT_TODO.md)
**Purpose**: Complete development roadmap and task list

**Contents**:
- All development tasks in priority order
- 10 phases of development
- Progress tracking
- Dependencies and order

**Use When**:
- Starting development
- Planning implementation
- Tracking progress
- Understanding dependencies

---

### [Quick Start Guide](../QUICK_START.md)
**Purpose**: Get started quickly

**Use When**: First-time setup

### [Quick Reference](QUICK_REFERENCE.md)
**Purpose**: Cheat sheet for common tasks and commands

**Contents**:
- Quick start commands
- Common commands
- Telegram bot commands
- Configuration quick reference
- Troubleshooting quick fixes
- Common SQL queries

**Use When**:
- Need quick command reference
- Looking up common tasks
- Daily operations

### [Python Installation Guide](../PYTHON_INSTALLATION_GUIDE.md)
**Purpose**: Python setup instructions

**Use When**: Setting up Python environment

---

## 📊 Documentation by Use Case

### Setting Up the Project
1. Read: [Quick Start Guide](../QUICK_START.md)
2. Read: [Configuration Reference](04_CONFIGURATION_REFERENCE.md)
3. Read: [Deployment & Operations](05_DEPLOYMENT_AND_OPERATIONS.md)

### Understanding the System
1. Read: [Architecture & Design](01_ARCHITECTURE_AND_DESIGN.md)
2. Read: [Database Schema](02_DATABASE_SCHEMA_AND_MIGRATION.md)
3. Read: [Agent Implementation](03_AGENT_IMPLEMENTATION_GUIDE.md)

### Implementing Features
1. Read: [Agent Implementation](03_AGENT_IMPLEMENTATION_GUIDE.md)
2. Read: [Database Schema](02_DATABASE_SCHEMA_AND_MIGRATION.md)
3. Read: [Testing Guide](07_TESTING_AND_QUALITY_ASSURANCE.md)

### Debugging Issues
1. Read: [Troubleshooting Guide](06_TROUBLESHOOTING_AND_DEBUGGING.md)
2. Check: [Configuration Reference](04_CONFIGURATION_REFERENCE.md)
3. Review: [Agent Implementation](03_AGENT_IMPLEMENTATION_GUIDE.md)

### Maintaining System
1. Read: [Maintenance & Upgrade](08_MAINTENANCE_AND_UPGRADE.md)
2. Read: [Deployment & Operations](05_DEPLOYMENT_AND_OPERATIONS.md)
3. Review: [Troubleshooting Guide](06_TROUBLESHOOTING_AND_DEBUGGING.md)

### Upgrading System
1. Read: [Maintenance & Upgrade](08_MAINTENANCE_AND_UPGRADE.md)
2. Review: [Database Schema](02_DATABASE_SCHEMA_AND_MIGRATION.md)
3. Check: [Configuration Reference](04_CONFIGURATION_REFERENCE.md)

---

## 🔍 Finding Information

### By Topic

**Architecture**: [01_ARCHITECTURE_AND_DESIGN.md](01_ARCHITECTURE_AND_DESIGN.md)  
**Database**: [02_DATABASE_SCHEMA_AND_MIGRATION.md](02_DATABASE_SCHEMA_AND_MIGRATION.md)  
**Agents**: [03_AGENT_IMPLEMENTATION_GUIDE.md](03_AGENT_IMPLEMENTATION_GUIDE.md)  
**Configuration**: [04_CONFIGURATION_REFERENCE.md](04_CONFIGURATION_REFERENCE.md)  
**Deployment**: [05_DEPLOYMENT_AND_OPERATIONS.md](05_DEPLOYMENT_AND_OPERATIONS.md)  
**Troubleshooting**: [06_TROUBLESHOOTING_AND_DEBUGGING.md](06_TROUBLESHOOTING_AND_DEBUGGING.md)  
**Testing**: [07_TESTING_AND_QUALITY_ASSURANCE.md](07_TESTING_AND_QUALITY_ASSURANCE.md)  
**Maintenance**: [08_MAINTENANCE_AND_UPGRADE.md](08_MAINTENANCE_AND_UPGRADE.md)  
**Sentiment Analysis**: [09_SENTIMENT_ANALYSIS_SYSTEM.md](09_SENTIMENT_ANALYSIS_SYSTEM.md)  
**Free Sources**: [10_FREE_SENTIMENT_SOURCES.md](10_FREE_SENTIMENT_SOURCES.md)  
**Status & Changelog**: [11_STATUS_AND_CHANGELOG.md](11_STATUS_AND_CHANGELOG.md)  
**News Fetching**: [12_NEWS_FETCHING_AND_STORAGE.md](12_NEWS_FETCHING_AND_STORAGE.md)  
**News Fetching**: [12_NEWS_FETCHING_AND_STORAGE.md](12_NEWS_FETCHING_AND_STORAGE.md)

### By Component

**Shoonya API**: [SHOONYA_API_GUIDE.md](SHOONYA_API_GUIDE.md)  
**Upstox API**: [UPSTOX_API_GUIDE.md](UPSTOX_API_GUIDE.md)  
**All APIs**: [API_INTEGRATION_SUMMARY.md](API_INTEGRATION_SUMMARY.md)  
**Telegram Bot**: [TELEGRAM_BOT_GUIDE.md](TELEGRAM_BOT_GUIDE.md)  
**Ollama Models**: [OLLAMA_LOCAL_SETUP.md](OLLAMA_LOCAL_SETUP.md)  
**Quick Reference**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

---

## 📝 Documentation Standards

### Keeping Documentation Updated

1. **Update on Changes**: Update relevant docs when making changes
2. **Version Control**: Track documentation changes in git
3. **Review Regularly**: Review and update quarterly
4. **Link Documents**: Cross-reference related documents

### Contributing to Documentation

1. **Follow Format**: Use existing document structure
2. **Add Examples**: Include code examples where helpful
3. **Update Index**: Update this index when adding new docs
4. **Test Examples**: Ensure all code examples work

---

## 🎯 Documentation Roadmap

### Current Status
✅ All core documentation complete
✅ API integration guides complete
✅ Project specification documented
✅ Sentiment analysis system documented
✅ Phase 1 & 2 completion documented

### Future Additions
- Video tutorials
- Interactive examples
- API reference (auto-generated)
- Performance benchmarks

---

## 📞 Getting Help

### Documentation Issues
- Check if information exists in docs
- Search across all documents
- Review troubleshooting guide

### Implementation Questions
- Review agent implementation guide
- Check code examples
- Review architecture document

### System Issues
- Check troubleshooting guide
- Review logs
- Check configuration

---

**Last Updated**: January 2025  
**Current Status**: Phase 1 & Phase 2 Complete (Including Sentiment Analysis)  
**Maintained By**: Development Team  
**Feedback**: Update documentation as needed

---

## 📊 Current Development Status

### ✅ Completed Phases

**Phase 1: Foundation & Infrastructure** (100% Complete)
- Database models and repositories (including sentiment models)
- Configuration system
- Ollama service integration
- Technical indicators (29 indicators)
- Core service layer
- **Sentiment Repository** - Complete CRUD operations for news and sentiment

**Phase 2.3: yfinance Integration** (100% Complete)
- yfinance data fetcher with Nifty 500 support
- Historical data backfill script
- Advanced backfill options (force refresh, custom dates, update recent)
- Batch processing with rate limiting
- Comprehensive unit and integration tests

**Phase 2.4: Data Source Orchestrator** (Simplified - Complete)
- Data source manager (yfinance only)
- Data freshness validation
- Batch fetching support

**Phase 2.5: News Sources Integration** (100% Complete)
- News fetcher module with RSS parsing (`data_sources/news_fetcher.py`)
- 12 active news sources configured (Economic Times, Moneycontrol, Business Standard, BSE, etc.)
- BSE corporate announcements RSS feed (replaces NSE API)
- Article content extraction and deduplication
- Per-source tracking for efficient incremental fetching
- News source configuration (`config/news_sources.py`)
- Database migration script for sentiment tables
- News fetch and store script (`scripts/fetch_and_store_news.py`)
- Comprehensive test suite (`tests/test_news_fetcher.py`)

### 🚧 In Progress

- None currently

### ⏳ Pending

- Phase 2.1: Shoonya API Integration
- Phase 2.2: Upstox API Integration
- Phase 3: Agent Implementation (including News Sentiment Analyst)
- Phase 4-10: Remaining phases

### 📝 Recent Changes (January 2025)

- ✅ **Phase 1 & 2 Complete**: All foundation and data source components implemented
- ✅ **Sentiment Analysis Infrastructure**: Complete database models, repository, and news fetching
- ✅ **News Fetcher Module**: RSS parsing for 12 active Indian financial news sources
- ✅ **Sentiment Repository**: Full CRUD operations for articles, sentiment scores, and macro mappings
- ✅ **Database Migration**: Script to create sentiment analysis tables
- ✅ **News Source Configuration**: 12 sources configured (including BSE RSS feed)
- ✅ **Per-Source Tracking**: Efficient incremental fetching with timestamp tracking
- ✅ **News Fetch Script**: `fetch_and_store_news.py` with multiple operation modes
- ✅ **Comprehensive Tests**: Test suite for news fetcher module
- ✅ **Documentation**: Complete sentiment analysis and news fetching documentation
- ✅ **Free Sources Guide**: Comprehensive guide to free news sources and sentiment tools
- ✅ Added Sentiment Analysis System documentation
- ✅ Designed News Sentiment Analyst agent (Agent #5)
- ✅ Documented macro news propagation methodology
- ✅ Added sentiment analysis database schema
- ✅ Integrated sentiment analysis with Strategy Specialist
- ✅ Replaced NSE API with BSE RSS feed for easier access
- ✅ Added yfinance integration for historical data
- ✅ Implemented Nifty 500 backfill script with advanced options
- ✅ Added force refresh, custom date range, and update recent days features
- ✅ Created comprehensive unit tests for data sources
- ✅ Database migration script for sector/market_cap columns
- ✅ Improved CSV parsing for Nifty 500 symbol list
