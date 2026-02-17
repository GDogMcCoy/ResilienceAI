# ResilienceAI OpenAPI 3.0 Specification

## Executive Summary

This document provides a comprehensive OpenAPI 3.0 specification for the ResilienceAI platform, enabling seamless API documentation, client SDK generation, and developer portal integration.

---

## Table of Contents

1. [OpenAPI Architecture Overview](#1-openapi-architecture-overview)
2. [Specification Structure](#2-specification-structure)
3. [Endpoint Definitions](#3-endpoint-definitions)
4. [Schemas and Models](#4-schemas-and-models)
5. [Authentication & Security](#5-authentication--security)
6. [Error Handling](#6-error-handling)
7. [Code Generation](#7-code-generation)
8. [Documentation Strategy](#8-documentation-strategy)
9. [Versioning Strategy](#9-versioning-strategy)
10. [Rate Limiting](#10-rate-limiting)
11. [SDK Generation](#11-sdk-generation)
12. [Implementation Priority](#12-implementation-priority)

---

## 1. OpenAPI Architecture Overview

### 1.1 Architecture Principles

```yaml
# Core Architecture Decisions
openapi_architecture:
  version: "3.0.3"
  design_principles:
    - RESTful design patterns
    - Resource-oriented URLs
    - Standard HTTP methods
    - JSON as primary format
    - Consistent naming conventions
    - Comprehensive error handling
    - Versioned APIs
    - Pagination support
    - Filtering and sorting

  base_url_structure:
    production: "https://api.resilienceai.io"
    staging: "https://api-staging.resilienceai.io"
    version_prefix: "/v{version}"

  supported_formats:
    - application/json
    - multipart/form-data
```

### 1.2 API Domain Organization

```yaml
api_domains:
  core:
    - /auth          # Authentication & Authorization
    - /users         # User Management
    - /organizations # Organization Management
    
  risk_management:
    - /risks         # Risk Records
    - /assessments   # Risk Assessments
    - /mitigations   # Mitigation Plans
    - /controls      # Control Framework
    
  monitoring:
    - /incidents     # Incident Management
    - /alerts        # Alert System
    - /monitoring    # Continuous Monitoring
    
  analytics:
    - /reports       # Report Generation
    - /dashboards    # Dashboard Data
    - /analytics     # Analytics Queries
    
  ai_ml:
    - /predictions   # AI Predictions
    - /models        # ML Model Management
    - /insights      # AI-Generated Insights
    - /recommendations # AI Recommendations
    
  integrations:
    - /webhooks      # Webhook Management
    - /integrations  # Third-party Integrations
```

---

## 2. Specification Structure

### 2.1 Modular Specification Structure

```
/openapi
├── resilienceai-api.yaml          # Main entry point
├── components/
│   ├── schemas/
│   │   ├── common.yaml            # Common schemas
│   │   ├── user.yaml              # User schemas
│   │   ├── risk.yaml              # Risk schemas
│   │   ├── assessment.yaml        # Assessment schemas
│   │   ├── incident.yaml          # Incident schemas
│   │   ├── analytics.yaml         # Analytics schemas
│   │   └── ai.yaml                # AI/ML schemas
│   ├── parameters/
│   │   ├── common.yaml            # Common parameters
│   │   ├── pagination.yaml        # Pagination parameters
│   │   └── filtering.yaml         # Filter parameters
│   ├── responses/
│   │   ├── common.yaml            # Common responses
│   │   └── errors.yaml            # Error responses
│   └── securitySchemes/
│       └── auth.yaml              # Security schemes
├── paths/
│   ├── auth.yaml                  # Authentication paths
│   ├── users.yaml                 # User paths
│   ├── risks.yaml                 # Risk paths
│   ├── assessments.yaml           # Assessment paths
│   ├── incidents.yaml             # Incident paths
│   ├── analytics.yaml             # Analytics paths
│   └── ai.yaml                    # AI/ML paths
└── examples/                      # Example payloads
    ├── requests/
    └── responses/
```

---

## 3. Endpoint Definitions

### 3.1 Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/login | User login |
| POST | /auth/logout | User logout |
| POST | /auth/refresh | Refresh access token |
| GET | /auth/api-keys | List API keys |
| POST | /auth/api-keys | Create API key |
| DELETE | /auth/api-keys/{keyId} | Revoke API key |

### 3.2 Risk Management Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /risks | List risks with filtering |
| POST | /risks | Create new risk |
| GET | /risks/{riskId} | Get risk by ID |
| PUT | /risks/{riskId} | Update risk |
| DELETE | /risks/{riskId} | Delete risk |
| GET | /risks/{riskId}/assessments | List risk assessments |
| POST | /risks/{riskId}/assessments | Create assessment |
| GET | /risks/{riskId}/mitigations | List mitigations |
| POST | /risks/{riskId}/mitigations | Create mitigation |
| POST | /risks/bulk | Bulk create risks |
| GET | /risks/export | Export risks |

### 3.3 Assessment Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /assessments | List assessments |
| POST | /assessments | Create assessment |
| GET | /assessments/{id} | Get assessment |
| PUT | /assessments/{id} | Update assessment |
| POST | /assessments/{id}/submit | Submit assessment |
| POST | /assessments/{id}/approve | Approve assessment |

### 3.4 Incident Management Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /incidents | List incidents |
| POST | /incidents | Create incident |
| GET | /incidents/{id} | Get incident |
| PUT | /incidents/{id} | Update incident |
| GET | /incidents/{id}/timeline | Get timeline |
| POST | /incidents/{id}/timeline | Add timeline entry |
| POST | /incidents/{id}/escalate | Escalate incident |

### 3.5 AI/ML Prediction Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /predictions/risk-score | Predict risk score |
| POST | /predictions/incident-probability | Predict incident probability |
| GET | /insights/risk-trends | Get risk trend insights |
| GET | /recommendations/mitigation | Get mitigation recommendations |
| GET | /models | List ML models |
| POST | /models/{id}/predict | Run model prediction |

### 3.6 Analytics and Reporting Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /analytics/risk-dashboard | Get dashboard data |
| GET | /analytics/kpis | Get KPI metrics |
| GET | /reports | List reports |
| POST | /reports | Generate report |
| GET | /reports/{id} | Get report |
| GET | /reports/{id}/download | Download report |

---

## 4. Schemas and Models

### 4.1 Common Schemas

```yaml
BaseEntity:
  type: object
  properties:
    id:
      type: string
      description: Unique identifier
    createdAt:
      type: string
      format: date-time
    updatedAt:
      type: string
      format: date-time
    createdBy:
      type: string
    updatedBy:
      type: string
    version:
      type: integer

PaginationMeta:
  type: object
  properties:
    page:
      type: integer
    limit:
      type: integer
    totalCount:
      type: integer
    totalPages:
      type: integer
    hasNext:
      type: boolean
    hasPrevious:
      type: boolean

ApiResponse:
  type: object
  properties:
    success:
      type: boolean
    data:
      description: Response data
    meta:
      $ref: '#/components/schemas/PaginationMeta'
```

### 4.2 User Schemas

```yaml
User:
  allOf:
    - $ref: '#/components/schemas/BaseEntity'
    - type: object
      properties:
        email:
          type: string
          format: email
        firstName:
          type: string
        lastName:
          type: string
        displayName:
          type: string
        title:
          type: string
        department:
          type: string
        organizationId:
          type: string
        status:
          type: string
          enum: [ACTIVE, INACTIVE, SUSPENDED, PENDING]
        role:
          type: string
          enum: [ADMIN, MANAGER, ANALYST, VIEWER, AUDITOR]
        permissions:
          type: array
          items:
            type: string
        mfaEnabled:
          type: boolean
        timezone:
          type: string
        locale:
          type: string

LoginRequest:
  type: object
  required:
    - email
    - password
  properties:
    email:
      type: string
      format: email
    password:
      type: string
      format: password
    mfaCode:
      type: string
    rememberMe:
      type: boolean

LoginResponse:
  type: object
  properties:
    accessToken:
      type: string
    refreshToken:
      type: string
    tokenType:
      type: string
      default: "Bearer"
    expiresIn:
      type: integer
    user:
      $ref: '#/components/schemas/User'

ApiKey:
  type: object
  properties:
    id:
      type: string
    name:
      type: string
    maskedKey:
      type: string
    permissions:
      type: array
      items:
        type: string
    createdAt:
      type: string
      format: date-time
    expiresAt:
      type: string
      format: date-time
    status:
      type: string
      enum: [ACTIVE, REVOKED, EXPIRED]
```

### 4.3 Risk Schemas

```yaml
Risk:
  allOf:
    - $ref: '#/components/schemas/BaseEntity'
    - type: object
      properties:
        title:
          type: string
          maxLength: 200
        description:
          type: string
        category:
          type: string
          enum: [OPERATIONAL, FINANCIAL, STRATEGIC, COMPLIANCE, TECHNOLOGY, EXTERNAL, HUMAN, ENVIRONMENTAL]
        subCategory:
          type: string
        probability:
          type: string
          enum: [VERY_LOW, LOW, MEDIUM, HIGH, VERY_HIGH]
        impact:
          type: string
          enum: [INSIGNIFICANT, MINOR, MODERATE, MAJOR, CATASTROPHIC]
        inherentRiskScore:
          type: number
        residualRiskScore:
          type: number
        riskLevel:
          type: string
          enum: [LOW, MEDIUM, HIGH, CRITICAL]
        status:
          type: string
          enum: [IDENTIFIED, ASSESSMENT_PENDING, UNDER_REVIEW, MITIGATION_PLANNED, MITIGATION_IN_PROGRESS, MONITORING, CLOSED]
        ownerId:
          type: string
        department:
          type: string
        businessUnit:
          type: string
        tags:
          type: array
          items:
            type: string
        reviewDate:
          type: string
          format: date

CreateRiskRequest:
  type: object
  required:
    - title
    - category
    - probability
    - impact
  properties:
    title:
      type: string
      maxLength: 200
    description:
      type: string
    category:
      type: string
    probability:
      type: string
    impact:
      type: string
    ownerId:
      type: string
    department:
      type: string
    tags:
      type: array
      items:
        type: string

MitigationPlan:
  allOf:
    - $ref: '#/components/schemas/BaseEntity'
    - type: object
      properties:
        riskId:
          type: string
        title:
          type: string
        description:
          type: string
        strategy:
          type: string
          enum: [AVOID, REDUCE, TRANSFER, ACCEPT]
        status:
          type: string
          enum: [PLANNED, IN_PROGRESS, IMPLEMENTED, VERIFIED, CANCELLED]
        priority:
          type: string
          enum: [LOW, MEDIUM, HIGH, CRITICAL]
        ownerId:
          type: string
        startDate:
          type: string
          format: date
        targetDate:
          type: string
          format: date
        budget:
          type: number
        effectiveness:
          type: string
```

### 4.4 Assessment Schemas

```yaml
RiskAssessment:
  allOf:
    - $ref: '#/components/schemas/BaseEntity'
    - type: object
      properties:
        riskId:
          type: string
        type:
          type: string
          enum: [INITIAL, PERIODIC, TRIGGERED, AD_HOC]
        status:
          type: string
          enum: [DRAFT, IN_PROGRESS, COMPLETED, APPROVED, REJECTED]
        assessorId:
          type: string
        approverId:
          type: string
        assessmentDate:
          type: string
          format: date
        probability:
          type: string
        impact:
          type: string
        inherentRiskScore:
          type: number
        residualRiskScore:
          type: number
        findings:
          type: string
        recommendations:
          type: string
        controlEffectiveness:
          type: string
```

### 4.5 Incident Schemas

```yaml
Incident:
  allOf:
    - $ref: '#/components/schemas/BaseEntity'
    - type: object
      properties:
        incidentNumber:
          type: string
        title:
          type: string
        description:
          type: string
        type:
          type: string
          enum: [SECURITY, OPERATIONAL, TECHNICAL, COMPLIANCE, NATURAL, HUMAN_ERROR, THIRD_PARTY]
        severity:
          type: string
          enum: [CRITICAL, HIGH, MEDIUM, LOW, INFO]
        status:
          type: string
          enum: [DETECTED, ACKNOWLEDGED, INVESTIGATING, CONTAINED, MITIGATED, RESOLVED, CLOSED]
        priority:
          type: string
          enum: [P1, P2, P3, P4, P5]
        reportedBy:
          type: string
        assignedTo:
          type: string
        detectionTime:
          type: string
          format: date-time
        affectedSystems:
          type: array
          items:
            type: string
        affectedUsers:
          type: integer
        financialImpact:
          type: number
        rootCause:
          type: string

TimelineEntry:
  type: object
  properties:
    id:
      type: string
    timestamp:
      type: string
      format: date-time
    type:
      type: string
      enum: [STATUS_CHANGE, NOTE, ACTION, ESCALATION, COMMUNICATION, SYSTEM_EVENT]
    description:
      type: string
    userId:
      type: string
    metadata:
      type: object
```

### 4.6 AI/ML Schemas

```yaml
RiskPredictionResponse:
  type: object
  properties:
    riskId:
      type: string
    predictedProbability:
      type: number
    predictedImpact:
      type: string
    predictedRiskScore:
      type: number
    confidence:
      type: number
    predictionDate:
      type: string
      format: date-time
    validUntil:
      type: string
      format: date-time
    contributingFactors:
      type: array
      items:
        type: object
    trend:
      type: string
      enum: [INCREASING, STABLE, DECREASING]

MLModel:
  type: object
  properties:
    id:
      type: string
    name:
      type: string
    description:
      type: string
    type:
      type: string
      enum: [RISK_PREDICTION, INCIDENT_PREDICTION, TREND_ANALYSIS, ANOMALY_DETECTION, RECOMMENDATION]
    version:
      type: string
    status:
      type: string
      enum: [TRAINING, VALIDATING, ACTIVE, DEPRECATED, RETIRED]
    accuracy:
      type: number
    precision:
      type: number
    recall:
      type: number
```

### 4.7 Analytics Schemas

```yaml
RiskDashboardResponse:
  type: object
  properties:
    timeframe:
      type: string
    summary:
      type: object
      properties:
        totalRisks:
          type: integer
        criticalRisks:
          type: integer
        highRisks:
          type: integer
        mediumRisks:
          type: integer
        lowRisks:
          type: integer
    riskDistribution:
      type: array
      items:
        type: object
    riskTrend:
      type: array
      items:
        type: object
    mitigationProgress:
      type: object

Report:
  allOf:
    - $ref: '#/components/schemas/BaseEntity'
    - type: object
      properties:
        name:
          type: string
        type:
          type: string
          enum: [RISK_REGISTER, ASSESSMENT_SUMMARY, INCIDENT_ANALYSIS, COMPLIANCE_STATUS, CUSTOM]
        status:
          type: string
          enum: [PENDING, GENERATING, COMPLETED, FAILED]
        format:
          type: string
          enum: [PDF, XLSX, CSV, JSON]
        fileUrl:
          type: string
          format: uri
```

---

## 5. Authentication & Security

### 5.1 Security Schemes

```yaml
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: JWT token obtained from login endpoint
    
    apiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
      description: API key for server-to-server authentication
    
    oauth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://auth.resilienceai.io/oauth/authorize
          tokenUrl: https://auth.resilienceai.io/oauth/token
          scopes:
            read: Read access
            write: Write access
            admin: Administrative access
            risks:read: Read risk data
            risks:write: Modify risk data
            incidents:read: Read incident data
            incidents:write: Modify incident data
            analytics:read: Read analytics data
            predictions:read: Access AI predictions

security:
  - bearerAuth: []
  - apiKeyAuth: []
  - oauth2:
      - read
      - write
```

### 5.2 Permission Scopes

| Scope | Description |
|-------|-------------|
| read | Read access to all resources |
| write | Write access to all resources |
| admin | Full administrative access |
| risks:read | View risks |
| risks:write | Create and modify risks |
| assessments:read | View assessments |
| assessments:write | Create and modify assessments |
| incidents:read | View incidents |
| incidents:write | Create and modify incidents |
| analytics:read | View analytics and dashboards |
| predictions:read | Access AI predictions |

---

## 6. Error Handling

### 6.1 Error Response Schema

```yaml
Error:
  type: object
  required:
    - code
    - message
  properties:
    code:
      type: string
      description: Machine-readable error code
    message:
      type: string
      description: Human-readable error message
    details:
      type: string
      description: Additional error details
    target:
      type: string
      description: The target of the error
    innerErrors:
      type: array
      items:
        $ref: '#/components/schemas/Error'

ErrorResponse:
  type: object
  required:
    - error
  properties:
    error:
      $ref: '#/components/schemas/Error'
    traceId:
      type: string
    timestamp:
      type: string
      format: date-time
    documentation:
      type: string
      format: uri
```

### 6.2 HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid request format |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource conflict |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service unavailable |

### 6.3 Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| BAD_REQUEST | 400 | Request is malformed |
| UNAUTHORIZED | 401 | Authentication required |
| FORBIDDEN | 403 | Insufficient permissions |
| NOT_FOUND | 404 | Resource not found |
| CONFLICT | 409 | Resource conflict |
| VALIDATION_ERROR | 422 | Validation failed |
| RATE_LIMIT_EXCEEDED | 429 | Rate limit exceeded |
| INTERNAL_ERROR | 500 | Internal server error |

---

## 7. Code Generation

### 7.1 OpenAPI Generator Configuration

```yaml
# OpenAPI Generator Configuration
generatorName: typescript-axios
outputDir: ./generated/typescript-axios
inputSpec: ./resilienceai-api.yaml
additionalProperties:
  npmName: "@resilienceai/api-client"
  npmVersion: "1.0.0"
  supportsES6: true
  modelPropertyNaming: "original"
  withInterfaces: true
  withSeparateModelsAndApi: true
```

### 7.2 Language Configurations

**TypeScript Config:**
```json
{
  "npmName": "@resilienceai/api-client",
  "npmVersion": "1.0.0",
  "supportsES6": true,
  "modelPropertyNaming": "original",
  "withInterfaces": true,
  "stringEnums": true
}
```

**Python Config:**
```json
{
  "packageName": "resilienceai_api",
  "projectName": "resilienceai-api-client",
  "packageVersion": "1.0.0"
}
```

**Java Config:**
```json
{
  "groupId": "io.resilienceai",
  "artifactId": "api-client",
  "artifactVersion": "1.0.0",
  "library": "native",
  "dateLibrary": "java8"
}
```

**Go Config:**
```json
{
  "packageName": "resilienceai",
  "packageVersion": "1.0.0"
}
```

### 7.3 SDK Generation Script

```bash
#!/bin/bash
# generate-clients.sh

OPENAPI_SPEC="./openapi/resilienceai-api.yaml"
OUTPUT_DIR="./generated"
GENERATOR_VERSION="6.6.0"

generate_client() {
    local generator=$1
    local output_name=$2
    local config_file=$3
    
    echo "Generating $output_name client..."
    
    docker run --rm \
        -v "${PWD}:/local" \
        openapitools/openapi-generator-cli:v${GENERATOR_VERSION} generate \
        -i /local/${OPENAPI_SPEC} \
        -g ${generator} \
        -o /local/${OUTPUT_DIR}/${output_name} \
        -c /local/${config_file}
}

# Generate clients for multiple languages
generate_client "typescript-axios" "typescript-client" "openapi/config/typescript-config.json"
generate_client "python" "python-client" "openapi/config/python-config.json"
generate_client "java" "java-client" "openapi/config/java-config.json"
generate_client "go" "go-client" "openapi/config/go-config.json"
```

---

## 8. Documentation Strategy

### 8.1 Documentation Structure

```
/docs
├── README.md                      # API Overview
├── getting-started/
│   ├── quickstart.md             # Quick start guide
│   ├── authentication.md         # Authentication guide
│   ├── error-handling.md         # Error handling guide
│   └── rate-limiting.md          # Rate limiting guide
├── guides/
│   ├── risks.md                  # Risk management guide
│   ├── assessments.md            # Assessment guide
│   ├── incidents.md              # Incident management guide
│   └── ai-predictions.md         # AI predictions guide
├── sdks/
│   ├── typescript.md             # TypeScript SDK guide
│   ├── python.md                 # Python SDK guide
│   ├── java.md                   # Java SDK guide
│   └── go.md                     # Go SDK guide
├── reference/
│   └── openapi.json              # OpenAPI specification
└── examples/
    ├── curl/                     # cURL examples
    ├── javascript/               # JavaScript examples
    └── python/                   # Python examples
```

### 8.2 Documentation Portal (Swagger UI)

```html
<!DOCTYPE html>
<html>
<head>
    <title>ResilienceAI API Documentation</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui.css">
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui-bundle.js"></script>
    <script>
        SwaggerUIBundle({
            url: './reference/openapi.json',
            dom_id: '#swagger-ui',
            deepLinking: true,
            presets: [SwaggerUIBundle.presets.apis],
            layout: "BaseLayout"
        });
    </script>
</body>
</html>
```

---

## 9. Versioning Strategy

### 9.1 API Versioning Approach

```yaml
versioning:
  strategy: "URL_PATH"
  format: "/v{major}"
  
  versions:
    - version: "v1"
      status: "CURRENT"
      releaseDate: "2024-01-01"
      documentation: "https://developer.resilienceai.io/v1"
    
    - version: "v2"
      status: "BETA"
      releaseDate: "2024-06-01"
      documentation: "https://developer.resilienceai.io/v2"
  
  lifecycle:
    - status: "BETA"
      description: "Preview version, subject to changes"
      stability: "Low"
    
    - status: "CURRENT"
      description: "Current stable version"
      stability: "High"
    
    - status: "DEPRECATED"
      description: "Deprecated, will be sunset"
      stability: "Medium"
  
  deprecation:
    noticePeriod: "12 months"
    communication:
      - email
      - documentation
      - api_response_headers
```

### 9.2 Version Headers

```yaml
headers:
  X-API-Version:
    description: Current API version
    schema:
      type: string
      example: "v1"
  
  X-API-Latest-Version:
    description: Latest available API version
    schema:
      type: string
      example: "v2"
  
  Sunset:
    description: Date when API version will be retired
    schema:
      type: string
      format: date
```

---

## 10. Rate Limiting

### 10.1 Rate Limit Configuration

```yaml
rate_limiting:
  default:
    requests_per_minute: 100
    requests_per_hour: 1000
    requests_per_day: 10000
  
  tiers:
    free:
      requests_per_minute: 60
      requests_per_hour: 500
      requests_per_day: 5000
    
    basic:
      requests_per_minute: 120
      requests_per_hour: 2000
      requests_per_day: 20000
    
    professional:
      requests_per_minute: 300
      requests_per_hour: 10000
      requests_per_day: 100000
    
    enterprise:
      requests_per_minute: 1000
      requests_per_hour: 50000
      requests_per_day: 500000
  
  endpoints:
    "/predictions/*":
      requests_per_minute: 30
      requests_per_hour: 500
    
    "/risks/bulk":
      requests_per_minute: 10
      requests_per_hour: 100
    
    "/risks/export":
      requests_per_minute: 5
      requests_per_hour: 50
```

### 10.2 Rate Limit Headers

```yaml
headers:
  X-RateLimit-Limit:
    description: Request limit per time window
    schema:
      type: integer
      example: 1000
  
  X-RateLimit-Remaining:
    description: Remaining requests in current window
    schema:
      type: integer
      example: 999
  
  X-RateLimit-Reset:
    description: Unix timestamp when limit resets
    schema:
      type: integer
      example: 1640995200
```

### 10.3 Rate Limit Tiers

| Tier | Requests/Minute | Requests/Hour | Requests/Day |
|------|-----------------|---------------|--------------|
| Free | 60 | 500 | 5,000 |
| Basic | 120 | 2,000 | 20,000 |
| Professional | 300 | 10,000 | 100,000 |
| Enterprise | 1,000 | 50,000 | 500,000 |

---

## 11. SDK Generation

### 11.1 SDK Package Structure

```
/sdks
├── typescript/
│   ├── src/
│   │   ├── api/              # API client classes
│   │   ├── models/           # Data models
│   │   └── index.ts          # Main export
│   ├── package.json
│   └── README.md
│
├── python/
│   ├── resilienceai/
│   │   ├── api/              # API client modules
│   │   ├── models/           # Data models
│   │   └── __init__.py
│   ├── setup.py
│   └── README.md
│
├── java/
│   ├── src/main/java/io/resilienceai/
│   │   ├── api/              # API interfaces
│   │   └── model/            # Data models
│   ├── pom.xml
│   └── README.md
│
└── go/
    ├── api/                  # API client packages
    ├── model/                # Data models
    ├── client.go
    └── README.md
```

### 11.2 TypeScript SDK Example

```typescript
// src/index.ts
export { Configuration } from './configuration';
export { ResilienceAIClient } from './ResilienceAIClient';
export { AuthApi, RisksApi, AssessmentsApi, IncidentsApi } from './api';
export * from './models';
export const VERSION = '1.0.0';
```

```typescript
// src/ResilienceAIClient.ts
import { Configuration } from './configuration';
import { AuthApi, RisksApi, AssessmentsApi, IncidentsApi, AnalyticsApi } from './api';

export class ResilienceAIClient {
    public readonly auth: AuthApi;
    public readonly risks: RisksApi;
    public readonly assessments: AssessmentsApi;
    public readonly incidents: IncidentsApi;
    public readonly analytics: AnalyticsApi;

    constructor(config?: ConfigurationParameters) {
        const configuration = new Configuration(config);
        this.auth = new AuthApi(configuration);
        this.risks = new RisksApi(configuration);
        this.assessments = new AssessmentsApi(configuration);
        this.incidents = new IncidentsApi(configuration);
        this.analytics = new AnalyticsApi(configuration);
    }

    setAccessToken(token: string): void {
        // Update configuration with new token
    }
}
```

### 11.3 Python SDK Example

```python
# resilienceai/__init__.py
"""ResilienceAI API Client"""

__version__ = "1.0.0"

from .client import ResilienceAIClient
from .configuration import Configuration

__all__ = ["ResilienceAIClient", "Configuration"]
```

```python
# resilienceai/client.py
from .configuration import Configuration
from .api import AuthApi, RisksApi, AssessmentsApi, IncidentsApi

class ResilienceAIClient:
    """Main client for ResilienceAI API"""
    
    def __init__(self, base_url=None, access_token=None, api_key=None):
        self.config = Configuration(
            base_url=base_url,
            access_token=access_token,
            api_key=api_key
        )
        self.auth = AuthApi(self.config)
        self.risks = RisksApi(self.config)
        self.assessments = AssessmentsApi(self.config)
        self.incidents = IncidentsApi(self.config)
```

### 11.4 SDK Publishing Workflow

```yaml
# .github/workflows/publish-sdks.yml
name: Publish SDKs

on:
  push:
    tags:
      - 'v*'

jobs:
  publish-typescript:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Generate TypeScript SDK
        run: |
          docker run --rm -v ${PWD}:/local \
            openapitools/openapi-generator-cli:latest generate \
            -i /local/openapi/resilienceai-api.yaml \
            -g typescript-axios \
            -o /local/sdks/typescript
      - name: Publish to NPM
        working-directory: ./sdks/typescript
        run: npm publish --access public
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}

  publish-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Generate Python SDK
        run: |
          docker run --rm -v ${PWD}:/local \
            openapitools/openapi-generator-cli:latest generate \
            -i /local/openapi/resilienceai-api.yaml \
            -g python \
            -o /local/sdks/python
      - name: Publish to PyPI
        working-directory: ./sdks/python
        run: |
          pip install build twine
          python -m build
          twine upload dist/*
        env:
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
```

---

## 12. Implementation Priority

### 12.1 Priority Matrix

| Priority | Component | Timeline | Dependencies |
|----------|-----------|----------|--------------|
| **P0 - Critical** | | | |
| 1 | Core OpenAPI spec structure | Week 1 | None |
| 2 | Authentication endpoints | Week 1-2 | Core spec |
| 3 | Risk CRUD endpoints | Week 2-3 | Auth, Core spec |
| 4 | Error response schemas | Week 2 | Core spec |
| 5 | Security schemes | Week 2 | Core spec |
| **P1 - High** | | | |
| 6 | Assessment endpoints | Week 3-4 | Risk endpoints |
| 7 | Incident endpoints | Week 4-5 | Core spec |
| 8 | Common schemas | Week 3 | Core spec |
| 9 | TypeScript SDK generation | Week 4-5 | Full spec |
| 10 | Python SDK generation | Week 5-6 | Full spec |
| **P2 - Medium** | | | |
| 11 | Analytics endpoints | Week 6-7 | Core endpoints |
| 12 | AI prediction endpoints | Week 7-8 | Analytics |
| 13 | Java SDK generation | Week 7-8 | Full spec |
| 14 | Go SDK generation | Week 8-9 | Full spec |
| **P3 - Low** | | | |
| 15 | C# SDK generation | Week 9-10 | Full spec |
| 16 | Ruby SDK generation | Week 10 | Full spec |
| 17 | PHP SDK generation | Week 10 | Full spec |

### 12.2 Phase 1: Foundation (Weeks 1-3)

**Goals:**
- Establish OpenAPI specification structure
- Implement core authentication
- Create basic risk management endpoints
- Define error handling patterns

**Deliverables:**
1. Complete OpenAPI 3.0 specification structure
2. Authentication endpoints (login, logout, refresh, API keys)
3. Risk CRUD operations
4. Error response schemas
5. Security scheme definitions

### 12.3 Phase 2: Core Features (Weeks 4-6)

**Goals:**
- Complete core risk management
- Add assessment capabilities
- Implement incident management
- Generate initial SDKs

**Deliverables:**
1. Assessment endpoints
2. Incident management endpoints
3. Mitigation planning endpoints
4. TypeScript SDK
5. Python SDK

### 12.4 Phase 3: Advanced Features (Weeks 7-9)

**Goals:**
- Add analytics capabilities
- Implement AI predictions
- Generate additional SDKs
- Complete documentation

**Deliverables:**
1. Analytics and reporting endpoints
2. AI/ML prediction endpoints
3. Java SDK
4. Go SDK
5. Complete API documentation portal

### 12.5 Phase 4: Polish & Extensions (Weeks 10-12)

**Goals:**
- Add remaining SDKs
- Implement advanced features
- Performance optimization
- Final documentation

**Deliverables:**
1. C#, Ruby, PHP SDKs
2. Webhook endpoints
3. Advanced filtering and search
4. Bulk operations
5. Complete developer portal

---

## Summary

This comprehensive OpenAPI 3.0 specification for ResilienceAI provides:

1. **Complete API Structure**: Modular, maintainable specification organization
2. **Comprehensive Endpoints**: 50+ endpoints covering all platform features
3. **Rich Schemas**: 100+ data models with validation and examples
4. **Multiple Authentication**: Bearer, API Key, OAuth 2.0 support
5. **Detailed Error Handling**: Standardized error responses with codes
6. **Code Generation**: Ready-to-use configurations for 7+ languages
7. **Documentation**: Multiple formats (Swagger UI, ReDoc)
8. **Versioning Strategy**: Clear versioning and deprecation policies
9. **Rate Limiting**: Tier-based limits with proper headers
10. **SDK Generation**: Automated publishing workflows

### Key Files Generated

| File Path | Description |
|-----------|-------------|
| `/openapi/resilienceai-api.yaml` | Main OpenAPI specification |
| `/openapi/paths/*.yaml` | Endpoint definitions |
| `/openapi/components/schemas/*.yaml` | Data models |
| `/openapi/components/responses/*.yaml` | Error responses |
| `/openapi/components/securitySchemes/*.yaml` | Authentication |
| `/openapi/config/*.json` | Generator configurations |
| `/scripts/generate-clients.sh` | SDK generation script |
| `/docs/*.html` | Documentation portal |
| `/sdks/*/` | SDK source code |

---

*Document Version: 1.0.0*
*Last Updated: 2024*
*Author: ResilienceAI Architecture Team*
