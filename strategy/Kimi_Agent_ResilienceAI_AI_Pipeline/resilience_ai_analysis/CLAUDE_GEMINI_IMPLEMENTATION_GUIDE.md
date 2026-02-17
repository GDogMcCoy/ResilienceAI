# Claude Code / Gemini CLI Implementation Guide
## ResilienceAI - AI-Powered Disaster Vulnerability Platform

**Repository:** https://github.com/GDogMcCoy/ResilienceAI  
**Branch:** claw-autonomous  
**Generated:** February 17, 2026

---

## Quick Start for Claude Code / Gemini CLI

This guide provides step-by-step instructions for implementing the ResilienceAI platform using Claude Code or Gemini CLI.

### Step 1: Clone and Setup Repository

```bash
# Clone the repository
git clone https://github.com/GDogMcCoy/ResilienceAI.git
cd ResilienceAI

# Switch to claw-autonomous branch
git checkout claw-autonomous

# Create implementation branch
git checkout -b feature/ai-enhanced-platform
```

### Step 2: Review Analysis Documents

All analysis documents are in `/mnt/okcomputer/output/resilience_ai_analysis/`:

```bash
# List all analysis documents
ls -la /mnt/okcomputer/output/resilience_ai_analysis/*.md

# Key documents to review first:
# 00_MASTER_INTEGRATION_GUIDE.md - Start here
# 01_frontend_dashboard.md - UI enhancements
# 02_backend_agent.md - Agent system
# 03_data_engineering.md - Data pipeline
# 04_ml_models.md - ML models
```

### Step 3: Implementation Order

Follow this priority order for implementation:

#### Phase 1: Foundation (Critical - Start Here)

```bash
# 1. Database Architecture
cat /mnt/okcomputer/output/resilience_ai_analysis/10_database_architecture.md

# 2. Security Framework
cat /mnt/okcomputer/output/resilience_ai_analysis/13_security_compliance.md

# 3. Data Pipeline
cat /mnt/okcomputer/output/resilience_ai_analysis/03_data_engineering.md

# 4. Agent System
cat /mnt/okcomputer/output/resilience_ai_analysis/02_backend_agent.md

# 5. ML Models
cat /mnt/okcomputer/output/resilience_ai_analysis/04_ml_models.md

# 6. Frontend Dashboard
cat /mnt/okcomputer/output/resilience_ai_analysis/01_frontend_dashboard.md
```

#### Phase 2: Intelligence (High Priority)

```bash
# 7. LLM Integration
cat /mnt/okcomputer/output/resilience_ai_analysis/06_ai_llm.md

# 8. Geospatial Analysis
cat /mnt/okcomputer/output/resilience_ai_analysis/05_geospatial.md

# 9. Real-time Systems
cat /mnt/okcomputer/output/resilience_ai_analysis/07_realtime_systems.md

# 10. Predictive Analytics
cat /mnt/okcomputer/output/resilience_ai_analysis/14_predictive_analytics.md
```

#### Phase 3: Scale (Medium Priority)

```bash
# 11. Kubernetes Deployment
cat /mnt/okcomputer/output/resilience_ai_analysis/44_kubernetes_devops.md

# 12. API Gateway
cat /mnt/okcomputer/output/resilience_ai_analysis/87_api_gateway.md

# 13. Monitoring
cat /mnt/okcomputer/output/resilience_ai_analysis/45_monitoring_observability.md

# 14. Performance Optimization
cat /mnt/okcomputer/output/resilience_ai_analysis/34_performance_optimization.md
```

---

## Implementation Commands

### Using Claude Code

```bash
# Start Claude Code in the repository
claude

# Ask Claude to implement specific components
# Example: Implement database architecture
@claude Please implement the database architecture from 
/mnt/okcomputer/output/resilience_ai_analysis/10_database_architecture.md

# Example: Create the security framework
@claude Please implement OAuth2 and JWT authentication from
/mnt/okcomputer/output/resilience_ai_analysis/13_security_compliance.md
```

### Using Gemini CLI

```bash
# Start Gemini CLI
gemini

# Ask Gemini to implement components
# Example: Implement data pipeline
@gemini Please implement the data pipeline from 
/mnt/okcomputer/output/resilience_ai_analysis/03_data_engineering.md
```

---

## Key Implementation Files to Create

### 1. Database Layer

```bash
# Create database directory structure
mkdir -p src/database/{models,migrations,queries}

# Files to create (from 10_database_architecture.md):
# - src/database/models/county.py
# - src/database/models/features.py
# - src/database/models/alerts.py
# - src/database/connection.py
# - src/database/migrations/alembic.ini
```

### 2. Security Layer

```bash
# Create security directory
mkdir -p src/security/{auth,encryption,audit}

# Files to create (from 13_security_compliance.md):
# - src/security/auth/oauth.py
# - src/security/auth/jwt_manager.py
# - src/security/auth/rbac.py
# - src/security/encryption/manager.py
# - src/security/audit/logger.py
```

### 3. Agent System

```bash
# Create agent directory
mkdir -p src/agents/{base,specialized,tools}

# Files to create (from 02_backend_agent.md):
# - src/agents/base.py
# - src/agents/orchestrator.py
# - src/agents/supervisor.py
# - src/agents/tools/registry.py
# - src/agents/specialized/vulnerability.py
# - src/agents/specialized/climate.py
```

### 4. Data Pipeline

```bash
# Create data pipeline directory
mkdir -p src/data/{extract,transform,load,quality}

# Files to create (from 03_data_engineering.md):
# - src/data/pipeline.py
# - src/data/extract/fema.py
# - src/data/extract/census.py
# - src/data/extract/noaa.py
# - src/data/transform/features.py
# - src/data/quality/checks.py
```

### 5. ML Models

```bash
# Create ML directory
mkdir -p src/ml/{models,training,inference,explainability}

# Files to create (from 04_ml_models.md):
# - src/ml/models/ensemble.py
# - src/ml/models/random_forest.py
# - src/ml/models/gradient_boosting.py
# - src/ml/models/neural_network.py
# - src/ml/training/pipeline.py
# - src/ml/explainability/shap.py
```

### 6. Frontend Dashboard

```bash
# Create dashboard directory
mkdir -p app/dashboard/{components,pages,utils}

# Files to create (from 01_frontend_dashboard.md):
# - app/dashboard/main.py
# - app/dashboard/components/chat_interface.py
# - app/dashboard/components/visualizations.py
# - app/dashboard/pages/resilience_map.py
# - app/dashboard/pages/predictive_insights.py
```

---

## Configuration Files

### Environment Variables (.env)

```bash
# Copy from example
cp .env.example .env

# Edit with your values:
# Database
DATABASE_URL=postgresql://user:pass@localhost/resilienceai
REDIS_URL=redis://localhost:6379

# API Keys
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
FEMA_API_KEY=your_key
CENSUS_API_KEY=your_key

# Security
JWT_SECRET=your_secret
OAUTH_CLIENT_ID=your_client_id
OAUTH_CLIENT_SECRET=your_client_secret

# Cloud
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
```

### Docker Compose (docker-compose.yml)

```yaml
version: '3.8'
services:
  postgres:
    image: postgis/postgis:15-3.3
    environment:
      POSTGRES_DB: resilienceai
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    ports:
      - "9092:9092"
    environment:
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181

  app:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
      - kafka
    env_file:
      - .env

volumes:
  postgres_data:
```

---

## Testing Strategy

### Unit Tests

```bash
# Run all unit tests
pytest tests/unit -v --cov=src

# Run specific test file
pytest tests/unit/test_agents.py -v

# Run with coverage report
pytest --cov=src --cov-report=html --cov-report=term
```

### Integration Tests

```bash
# Start test services
docker-compose -f docker-compose.test.yml up -d

# Run integration tests
pytest tests/integration -v

# Stop test services
docker-compose -f docker-compose.test.yml down
```

### Load Tests

```bash
# Install locust
pip install locust

# Run load tests
locust -f tests/performance/locustfile.py \
  --host=http://localhost:8000 \
  --users=100 \
  --spawn-rate=10 \
  --run-time=5m
```

---

## Deployment Commands

### Local Development

```bash
# Start all services
docker-compose up -d

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload

# Start Streamlit dashboard
streamlit run app/dashboard/main.py
```

### Kubernetes Deployment

```bash
# Build and push Docker image
docker build -t resilienceai:latest .
docker push your-registry/resilienceai:latest

# Apply Kubernetes manifests
kubectl apply -f config/kubernetes/

# Check deployment status
kubectl get pods -n resilienceai
kubectl logs -f deployment/resilienceai -n resilienceai
```

### Helm Deployment

```bash
# Install Helm chart
helm install resilienceai ./config/helm/resilience-ai \
  --namespace resilienceai \
  --create-namespace \
  --values config/helm/values-production.yaml

# Upgrade deployment
helm upgrade resilienceai ./config/helm/resilience-ai \
  --namespace resilienceai
```

---

## Monitoring & Debugging

### View Logs

```bash
# Application logs
docker-compose logs -f app

# Kubernetes logs
kubectl logs -f deployment/resilienceai -n resilienceai

# Specific pod logs
kubectl logs -f pod/resilienceai-xxx -n resilienceai
```

### Health Checks

```bash
# Check API health
curl http://localhost:8000/health

# Check metrics
curl http://localhost:8000/metrics

# Check database connection
python -c "from src.database.connection import check_connection; check_connection()"
```

### Performance Profiling

```bash
# Run profiler
python -m cProfile -o profile.stats app/main.py

# View profile stats
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative'); p.print_stats(20)"
```

---

## Common Issues & Solutions

### Issue 1: Database Connection Failed

```bash
# Check if PostgreSQL is running
docker-compose ps

# Restart PostgreSQL
docker-compose restart postgres

# Check logs
docker-compose logs postgres
```

### Issue 2: Redis Connection Failed

```bash
# Check Redis status
docker-compose ps redis

# Test Redis connection
redis-cli ping
```

### Issue 3: ML Model Loading Slow

```bash
# Pre-download models
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Use model caching
export TRANSFORMERS_CACHE=/app/models/cache
```

### Issue 4: Out of Memory

```bash
# Increase Docker memory limit
docker-compose down
docker-compose up -d --memory=8g

# Or update docker-compose.yml:
services:
  app:
    deploy:
      resources:
        limits:
          memory: 8G
```

---

## Code Generation Prompts

### For Claude Code

```
@claude Please implement the database models from 
/mnt/okcomputer/output/resilience_ai_analysis/10_database_architecture.md
Create the following files in src/database/models/:
- county.py (County model with PostGIS geometry)
- features.py (Feature definitions and values)
- alerts.py (Alert subscriptions and events)
```

```
@claude Please implement the OAuth2 authentication system from
/mnt/okcomputer/output/resilience_ai_analysis/13_security_compliance.md
Create:
- src/security/auth/oauth.py (OAuth2 provider integration)
- src/security/auth/jwt_manager.py (JWT token management)
- src/security/middleware.py (FastAPI middleware)
```

```
@claude Please implement the MCP agent orchestrator from
/mnt/okcomputer/output/resilience_ai_analysis/02_backend_agent.md
Create:
- src/agents/orchestrator.py (Main orchestrator)
- src/agents/base.py (Base agent class)
- src/agents/supervisor.py (Agent supervisor)
```

### For Gemini CLI

```
@gemini Please implement the data pipeline from
/mnt/okcomputer/output/resilience_ai_analysis/03_data_engineering.md
Create:
- src/data/pipeline.py (Main pipeline orchestrator)
- src/data/extract/fema.py (FEMA data extraction)
- src/data/extract/census.py (Census data extraction)
```

```
@gemini Please implement the ML model ensemble from
/mnt/okcomputer/output/resilience_ai_analysis/04_ml_models.md
Create:
- src/ml/models/ensemble.py (Ensemble model)
- src/ml/models/random_forest.py (Random Forest)
- src/ml/models/gradient_boosting.py (Gradient Boosting)
```

---

## File Structure Reference

```
resilience-ai/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── cd.yml
│       └── security-scan.yml
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application
│   ├── dashboard/
│   │   ├── __init__.py
│   │   ├── main.py               # Streamlit dashboard
│   │   ├── components/
│   │   │   ├── chat_interface.py
│   │   │   └── visualizations.py
│   │   └── pages/
│   │       ├── resilience_map.py
│   │       └── predictive_insights.py
│   └── api/
│       ├── __init__.py
│       ├── routes/
│       │   ├── counties.py
│       │   ├── predictions.py
│       │   └── alerts.py
│       └── dependencies.py
├── src/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── orchestrator.py
│   │   ├── supervisor.py
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   └── registry.py
│   │   └── specialized/
│   │       ├── vulnerability.py
│   │       ├── climate.py
│   │       └── planning.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── county.py
│   │   │   ├── features.py
│   │   │   └── alerts.py
│   │   └── migrations/
│   ├── data/
│   │   ├── __init__.py
│   │   ├── pipeline.py
│   │   ├── extract/
│   │   │   ├── __init__.py
│   │   │   ├── fema.py
│   │   │   ├── census.py
│   │   │   └── noaa.py
│   │   ├── transform/
│   │   │   ├── __init__.py
│   │   │   └── features.py
│   │   └── quality/
│   │       ├── __init__.py
│   │       └── checks.py
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── ensemble.py
│   │   │   ├── random_forest.py
│   │   │   ├── gradient_boosting.py
│   │   │   └── neural_network.py
│   │   ├── training/
│   │   │   ├── __init__.py
│   │   │   └── pipeline.py
│   │   └── explainability/
│   │       ├── __init__.py
│   │       └── shap.py
│   ├── security/
│   │   ├── __init__.py
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── oauth.py
│   │   │   ├── jwt_manager.py
│   │   │   └── rbac.py
│   │   ├── encryption/
│   │   │   ├── __init__.py
│   │   │   └── manager.py
│   │   └── audit/
│   │       ├── __init__.py
│   │       └── logger.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── config/
│   ├── kubernetes/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── ingress.yaml
│   ├── helm/
│   │   └── resilience-ai/
│   │       ├── Chart.yaml
│   │       ├── values.yaml
│   │       └── templates/
│   └── terraform/
│       └── main.tf
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_agents.py
│   │   ├── test_models.py
│   │   └── test_security.py
│   ├── integration/
│   │   ├── test_api.py
│   │   └── test_pipeline.py
│   └── performance/
│       └── locustfile.py
├── notebooks/
│   └── exploratory_analysis.ipynb
├── docs/
│   ├── architecture.md
│   ├── api.md
│   └── deployment.md
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── requirements/
│   ├── base.txt
│   ├── production.txt
│   └── development.txt
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
└── LICENSE
```

---

## Next Steps

1. **Review Master Integration Guide**
   ```bash
   cat /mnt/okcomputer/output/resilience_ai_analysis/00_MASTER_INTEGRATION_GUIDE.md
   ```

2. **Start with Phase 1 Implementation**
   - Database architecture
   - Security framework
   - Data pipeline

3. **Use Claude/Gemini for Code Generation**
   - Reference specific analysis documents
   - Follow the implementation order
   - Test each component

4. **Iterate and Refine**
   - Run tests after each implementation
   - Review and optimize
   - Document changes

---

## Support

- **Documentation:** See individual analysis documents in `/mnt/okcomputer/output/resilience_ai_analysis/`
- **Issues:** Create GitHub issues for bugs or questions
- **Discussions:** Use GitHub Discussions for general questions

---

**Ready to implement?** Start with the Master Integration Guide and follow the Phase 1 implementation order!
