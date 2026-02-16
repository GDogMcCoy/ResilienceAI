# ResilienceAI Setup Guide

Welcome to ResilienceAI! This guide will walk you through setting up the complete development environment for the ResilienceAI medical and geospatial data analysis platform.

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Installation](#2-installation)
3. [Environment Variables](#3-environment-variables)
4. [Data Pipeline](#4-data-pipeline)
5. [Dashboard Launch](#5-dashboard-launch)
6. [Troubleshooting](#6-troubleshooting)
7. [Development Workflow](#7-development-workflow)

---

## 1. Prerequisites

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **Python** | 3.10+ | 3.11 or 3.12 |
| **RAM** | 8 GB | 16 GB+ |
| **Disk Space** | 10 GB | 50 GB+ (for datasets) |
| **OS** | Linux/macOS/Windows WSL2 | Linux (Ubuntu 22.04+) |
| **Git** | 2.30+ | Latest |

### Required Software

- **Python 3.10+** with pip
- **Git** for version control
- **PostgreSQL 14+** (optional, for full database features)
- **PostGIS 3.0+** (optional, for geospatial database features)

### Verify Python Version

```bash
python --version  # Should be 3.10 or higher
# or
python3 --version
```

---

## 2. Installation

### Option A: Using pip (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/resilienceai.git
   cd resilienceai
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   
   # On Linux/macOS
   source venv/bin/activate
   
   # On Windows
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

### Option B: Using Conda

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/resilienceai.git
   cd resilienceai
   ```

2. **Create conda environment:**
   ```bash
   conda env create -f environment.yml
   conda activate resilienceai
   ```

3. **Verify installation:**
   ```bash
   python -c "import resilienceai; print('Installation successful!')"
   ```

### Core Dependencies

The following packages are automatically installed:

```
pandas >= 2.0.0
geopandas >= 0.14.0
numpy >= 1.24.0
rasterio >= 1.3.0
xarray >= 2023.0.0
fhir.resources >= 7.0.0
pydicom >= 2.4.0
sqlalchemy >= 2.0.0
psycopg2-binary >= 2.9.0
requests >= 2.31.0
python-dotenv >= 1.0.0
streamlit >= 1.28.0
plotly >= 5.18.0
matplotlib >= 3.8.0
seaborn >= 0.13.0
scikit-learn >= 1.3.0
shapely >= 2.0.0
pyproj >= 3.6.0
```

---

## 3. Environment Variables

ResilienceAI requires several environment variables for proper operation. Create a `.env` file in the project root:

```bash
cp .env.example .env
```

### Required Variables

| Variable | Description | How to Obtain |
|----------|-------------|---------------|
| `CENSUS_API_KEY` | US Census Bureau API key | [Get API Key](https://api.census.gov/data/key_signup.html) |
| `DATABASE_URL` | PostgreSQL connection string | Format: `postgresql://user:pass@host:port/db` |
| `SECRET_KEY` | Application secret key | Generate: `openssl rand -hex 32` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging level | `INFO` |
| `DATA_DIR` | Data storage directory | `./data` |
| `CACHE_DIR` | Cache directory | `./cache` |
| `DASHBOARD_PORT` | Dashboard port | `8501` |
| `DASHBOARD_HOST` | Dashboard host | `0.0.0.0` |

### Example `.env` File

```bash
# API Keys
CENSUS_API_KEY=your_census_api_key_here

# Database (optional - SQLite used by default)
DATABASE_URL=postgresql://user:password@localhost:5432/resilienceai

# Security
SECRET_KEY=your_generated_secret_key_here

# Paths
DATA_DIR=./data
CACHE_DIR=./cache

# Dashboard
DASHBOARD_PORT=8501
DASHBOARD_HOST=0.0.0.0

# Logging
LOG_LEVEL=INFO
```

### Getting a Census API Key

1. Visit [https://api.census.gov/data/key_signup.html](https://api.census.gov/data/key_signup.html)
2. Fill out the form with your organization details
3. Check your email for the API key (usually arrives within minutes)
4. Add the key to your `.env` file

---

## 4. Data Pipeline

The data pipeline (`run_pipeline.py`) processes medical and geospatial data from various sources.

### Quick Start

```bash
# Run the complete pipeline
python run_pipeline.py

# Run with specific options
python run_pipeline.py --source census --year 2022

# Dry run (validate without downloading)
python run_pipeline.py --dry-run

# Verbose output
python run_pipeline.py --verbose
```

### Pipeline Stages

The pipeline executes the following stages:

1. **Data Collection**
   - Fetches Census demographic data
   - Retrieves health facility locations
   - Downloads environmental datasets

2. **Data Processing**
   - Cleans and validates data
   - Performs geospatial joins
   - Calculates resilience metrics

3. **Data Storage**
   - Saves to database or local files
   - Creates indices for fast queries
   - Generates metadata

### Pipeline Options

```bash
python run_pipeline.py --help

# Output:
#   --source {census,health,environmental,all}
#   --year YEAR
#   --geography {county,tract,block}
#   --output-format {parquet,csv,db}
#   --dry-run
#   --verbose
#   --workers N
```

### Scheduled Pipeline Runs

To run the pipeline on a schedule, use cron:

```bash
# Edit crontab
crontab -e

# Run daily at 2 AM
0 2 * * * cd /path/to/resilienceai && /path/to/venv/bin/python run_pipeline.py >> logs/pipeline.log 2>&1

# Run weekly on Sundays at 3 AM
0 3 * * 0 cd /path/to/resilienceai && /path/to/venv/bin/python run_pipeline.py --source census >> logs/weekly.log 2>&1
```

---

## 5. Dashboard Launch

ResilienceAI includes an interactive Streamlit dashboard for data visualization and analysis.

### Launch the Dashboard

```bash
# Default launch
streamlit run dashboard.py

# Or using the provided script
python -m resilienceai.dashboard

# With custom port
streamlit run dashboard.py --server.port 8080

# With custom host
streamlit run dashboard.py --server.address 127.0.0.1
```

### Dashboard Features

- **Interactive Maps**: Visualize geospatial health data
- **Time Series Analysis**: Track trends over time
- **Resilience Scoring**: View community resilience metrics
- **Data Export**: Download processed datasets
- **Custom Queries**: Filter and explore data

### Access the Dashboard

Once running, access the dashboard at:
- Local: http://localhost:8501
- Network: http://your-ip:8501

### Dashboard Configuration

Create `~/.streamlit/config.toml` for persistent settings:

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
```

---

## 6. Troubleshooting

### Common Issues

#### Issue: `ModuleNotFoundError` on import

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### Issue: Census API key not recognized

**Solution:**
```bash
# Verify .env file exists and is loaded
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('CENSUS_API_KEY'))"

# Check file permissions
ls -la .env

# Ensure no trailing spaces in .env
```

#### Issue: PostgreSQL connection failed

**Solution:**
```bash
# Test connection
psql $DATABASE_URL -c "SELECT 1;"

# Check PostgreSQL service status
sudo systemctl status postgresql  # Linux
brew services list | grep postgresql  # macOS

# Verify PostGIS extension
psql -d resilienceai -c "CREATE EXTENSION IF NOT EXISTS postgis;"
```

#### Issue: Geospatial data processing errors

**Solution:**
```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get install -y libgdal-dev gdal-bin

# Install system dependencies (macOS)
brew install gdal

# Reinstall geopandas
pip install --force-reinstall geopandas pyproj shapely
```

#### Issue: Dashboard fails to start

**Solution:**
```bash
# Check if port is in use
lsof -i :8501  # macOS/Linux
netstat -ano | findstr :8501  # Windows

# Kill existing process or use different port
streamlit run dashboard.py --server.port 8502

# Clear Streamlit cache
rm -rf ~/.streamlit/cache
```

#### Issue: Out of memory during pipeline execution

**Solution:**
```bash
# Reduce worker count
python run_pipeline.py --workers 2

# Process smaller geographic areas
python run_pipeline.py --geography county

# Increase swap space (Linux)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Getting Help

- **Documentation**: https://docs.resilienceai.io
- **GitHub Issues**: https://github.com/your-org/resilienceai/issues
- **Community Discord**: [Join here](https://discord.gg/resilienceai)
- **Email Support**: support@resilienceai.io

### Debug Mode

Enable detailed logging for troubleshooting:

```bash
# Set log level to DEBUG
export LOG_LEVEL=DEBUG

# Run with verbose output
python run_pipeline.py --verbose

# Enable Python tracebacks
export PYTHONUNBUFFERED=1
```

---

## 7. Development Workflow

### For Contributors

#### Setting Up Development Environment

1. **Fork and clone:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/resilienceai.git
   cd resilienceai
   ```

2. **Install development dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   ```

3. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

4. **Run tests:**
   ```bash
   pytest tests/ -v
   ```

#### Development Tools

| Tool | Purpose | Command |
|------|---------|---------|
| **pytest** | Testing | `pytest` |
| **black** | Code formatting | `black .` |
| **isort** | Import sorting | `isort .` |
| **flake8** | Linting | `flake8 .` |
| **mypy** | Type checking | `mypy .` |
| **pre-commit** | Git hooks | `pre-commit run --all-files` |

#### Branch Naming Convention

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

#### Commit Message Format

```
type(scope): subject

body (optional)

footer (optional)
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Example:
```
feat(pipeline): add support for 2023 census data

- Updated API endpoints for 2023 data
- Added new demographic variables
- Updated tests
```

#### Pull Request Process

1. Create a feature branch from `main`
2. Make your changes with tests
3. Run the full test suite: `pytest`
4. Update documentation if needed
5. Submit PR with clear description
6. Address review comments
7. Merge after approval

#### Code Style

- Follow PEP 8 guidelines
- Use type hints for function signatures
- Document public APIs with docstrings
- Keep functions focused and small
- Write tests for new functionality

#### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=resilienceai --cov-report=html

# Run specific test file
pytest tests/test_pipeline.py -v

# Run with debugger
pytest --pdb
```

#### Database Migrations

If using PostgreSQL:

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Quick Reference

### Essential Commands

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Daily use
python run_pipeline.py
streamlit run dashboard.py

# Development
pytest
black .
pre-commit run --all-files
```

### File Structure

```
resilienceai/
├── data/               # Data storage
├── docs/               # Documentation
├── notebooks/          # Jupyter notebooks
├── resilienceai/       # Main package
│   ├── __init__.py
│   ├── pipeline.py
│   ├── dashboard.py
│   └── config.py
├── tests/              # Test suite
├── .env                # Environment variables
├── .env.example        # Example environment file
├── requirements.txt    # Dependencies
├── requirements-dev.txt # Dev dependencies
├── run_pipeline.py     # Pipeline entry point
└── dashboard.py        # Dashboard entry point
```

---

## License

ResilienceAI is licensed under the MIT License. See [LICENSE](../LICENSE) for details.

---

*Last updated: 2024-02-16*
