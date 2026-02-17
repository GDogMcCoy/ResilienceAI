# ResilienceAI GraphQL API Design

## Executive Summary

This document provides a comprehensive design for the ResilienceAI GraphQL API, enabling flexible data queries, real-time subscriptions, and federated architecture to support mobile and web clients while migrating from REST-based APIs.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Schema Design](#schema-design)
3. [Type Definitions](#type-definitions)
4. [Resolver Implementation](#resolver-implementation)
5. [Subscriptions](#subscriptions)
6. [DataLoader Implementation](#dataloader-implementation)
7. [Federation Architecture](#federation-architecture)
8. [Authentication & Authorization](#authentication--authorization)
9. [Query Complexity Analysis](#query-complexity-analysis)
10. [Schema Stitching](#schema-stitching)
11. [GraphQL Playground](#graphql-playground)
12. [Client Integration](#client-integration)
13. [Deployment Guide](#deployment-guide)
14. [Implementation Priority](#implementation-priority)

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Client Layer                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Web App   │  │  Mobile App │  │  Dashboard  │  │  Third-party Apps   │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
└─────────┼────────────────┼────────────────┼────────────────────┼────────────┘
          │                │                │                    │
          └────────────────┴────────────────┴────────────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │     API Gateway             │
                    │  (Rate Limiting, Caching)   │
                    └──────────────┬──────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
┌─────────▼──────────┐  ┌──────────▼──────────┐  ┌──────────▼──────────┐
│  GraphQL Gateway   │  │   GraphQL Gateway   │  │   GraphQL Gateway   │
│   (Federation)     │  │    (Federation)     │  │    (Federation)     │
└─────────┬──────────┘  └──────────┬──────────┘  └──────────┬──────────┘
          │                        │                        │
    ┌─────┴─────┐            ┌─────┴─────┐            ┌─────┴─────┐
    │           │            │           │            │           │
┌───▼───┐   ┌───▼───┐    ┌───▼───┐   ┌───▼───┐    ┌───▼───┐   ┌───▼───┐
│Incident│   │ Asset │    │ Threat│   │  User │    │ Report│   │Analytics│
│Service │   │Service│    │Service│   │Service│    │Service│   │Service │
└────────┘   └───────┘    └───────┘   └───────┘    └───────┘   └────────┘
```

### Technology Stack

| Component | Technology |
|-----------|------------|
| GraphQL Server | Graphene (Python) / Apollo Server (Node.js) |
| Federation | Apollo Federation 2.0 |
| Subscriptions | Redis Pub/Sub + WebSockets |
| DataLoader | DataLoader (Python/JS) |
| Authentication | JWT + OAuth 2.0 |
| Complexity | graphql-query-complexity |
| Schema Registry | Apollo Studio / Hive |

---

## Schema Design

### Core Schema Structure

```graphql
# Schema Directives
directive @auth(requires: Role = ADMIN) on FIELD_DEFINITION
directive @rateLimit(max: Int, window: String) on FIELD_DEFINITION
directive @cacheControl(maxAge: Int, scope: CacheScope = PUBLIC) on FIELD_DEFINITION | OBJECT
directive @complexity(multipliers: [String!], value: Int) on FIELD_DEFINITION

directive @deprecated(reason: String) on FIELD_DEFINITION | ENUM_VALUE

enum Role { USER ANALYST MANAGER ADMIN SYSTEM }
enum CacheScope { PUBLIC PRIVATE }

# Scalars
scalar DateTime
scalar JSON
scalar UUID
scalar EmailAddress
scalar URL
scalar GeoPoint

# Interfaces
interface Node { id: ID! }
interface Timestamped { createdAt: DateTime! updatedAt: DateTime! }
interface PaginatedResult { edges: [Edge!]! pageInfo: PageInfo! totalCount: Int! }
interface Edge { node: Node! cursor: String! }

# Input Types
input PaginationInput { first: Int = 20 after: String last: Int before: String }
input DateRangeInput { startDate: DateTime endDate: DateTime }
input SortInput { field: String! direction: SortDirection = DESC }
enum SortDirection { ASC DESC }
input FilterInput { field: String! operator: FilterOperator! value: JSON! }
enum FilterOperator { EQ NEQ GT GTE LT LTE IN NIN CONTAINS STARTS_WITH ENDS_WITH }
```

---

## Type Definitions

### 1. Incident Types

```graphql
type Incident implements Node & Timestamped {
  id: ID!
  incidentId: String! @cacheControl(maxAge: 300)
  title: String!
  description: String
  severity: Severity!
  status: IncidentStatus!
  category: IncidentCategory!
  reporter: User!
  assignee: User
  assets: [Asset!]!
  threats: [Threat!]!
  comments: [Comment!]!
  attachments: [Attachment!]!
  timeline: [TimelineEvent!]!
  metrics: IncidentMetrics
  similarIncidents: [Incident!]!
  createdAt: DateTime!
  updatedAt: DateTime!
  resolvedAt: DateTime
  closedAt: DateTime
  location: GeoPoint
  affectedRegions: [String!]!
}

enum Severity { CRITICAL HIGH MEDIUM LOW INFO }
enum IncidentStatus { DETECTED TRIAGING INVESTIGATING CONTAINED RESOLVED CLOSED REOPENED }
enum IncidentCategory { MALWARE PHISHING DATA_BREACH DDOS INSIDER_THREAT SUPPLY_CHAIN PHYSICAL_SECURITY COMPLIANCE_VIOLATION OTHER }

type IncidentMetrics {
  responseTime: Int
  resolutionTime: Int
  impactScore: Float
  financialImpact: Float
  affectedUsers: Int
}

type IncidentConnection implements PaginatedResult {
  edges: [IncidentEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type IncidentEdge implements Edge {
  node: Incident!
  cursor: String!
}
```

### 2. Asset Types

```graphql
type Asset implements Node & Timestamped {
  id: ID!
  assetId: String!
  name: String!
  type: AssetType!
  status: AssetStatus!
  description: String
  owner: User
  department: Department
  ipAddresses: [String!]
  domains: [String!]
  ports: [Port!]
  vulnerabilities: [Vulnerability!]
  incidents: [Incident!]!
  threats: [Threat!]!
  complianceStatus: ComplianceStatus
  riskScore: Float
  criticality: CriticalityLevel
  createdAt: DateTime!
  updatedAt: DateTime!
}

enum AssetType { SERVER WORKSTATION NETWORK_DEVICE DATABASE APPLICATION CLOUD_SERVICE MOBILE_DEVICE IOT_DEVICE CONTAINER API }
enum AssetStatus { ACTIVE INACTIVE DECOMMISSIONED UNDER_MAINTENANCE COMPROMISED }
enum CriticalityLevel { CRITICAL HIGH MEDIUM LOW }

type Port { number: Int! protocol: String! service: String status: PortStatus! }
enum PortStatus { OPEN CLOSED FILTERED }
```

### 3. Threat Types

```graphql
type Threat implements Node & Timestamped {
  id: ID!
  threatId: String!
  name: String!
  type: ThreatType!
  severity: Severity!
  description: String
  indicators: [Indicator!]!
  mitreTechniques: [MITRETechnique!]
  affectedAssets: [Asset!]!
  relatedIncidents: [Incident!]!
  threatIntelligence: ThreatIntelligence
  status: ThreatStatus!
  firstSeen: DateTime!
  lastSeen: DateTime!
  createdAt: DateTime!
  updatedAt: DateTime!
}

enum ThreatType { MALWARE RANSOMWARE APT BOTNET ZERO_DAY INSIDER SOCIAL_ENGINEERING SUPPLY_CHAIN UNKNOWN }
enum ThreatStatus { ACTIVE MONITORING CONTAINED NEUTRALIZED FALSE_POSITIVE }

type Indicator { type: IndicatorType! value: String! confidence: Float! firstSeen: DateTime! lastSeen: DateTime! }
enum IndicatorType { IP DOMAIN URL HASH_MD5 HASH_SHA1 HASH_SHA256 EMAIL CVE YARA_RULE SIGMA_RULE }

type MITRETechnique { techniqueId: String! name: String! tactic: String! url: URL! }
type ThreatIntelligence { source: String! confidence: Float! reports: [ThreatReport!]! }
type ThreatReport { id: ID! title: String! source: String! publishedAt: DateTime! url: URL }
```

### 4. User Types

```graphql
type User implements Node & Timestamped {
  id: ID!
  userId: String!
  email: EmailAddress!
  username: String!
  firstName: String!
  lastName: String!
  fullName: String!
  avatar: URL
  role: Role!
  permissions: [Permission!]!
  teams: [Team!]!
  assignedIncidents: [Incident!]!
  reportedIncidents: [Incident!]!
  recentActivity: [Activity!]!
  preferences: UserPreferences
  notificationSettings: NotificationSettings
  status: UserStatus!
  lastLoginAt: DateTime
  createdAt: DateTime!
  updatedAt: DateTime!
}

type Permission { resource: String! actions: [Action!]! }
enum Action { CREATE READ UPDATE DELETE EXECUTE ADMIN }
type Team { id: ID! name: String! description: String members: [User!]! lead: User }
type UserPreferences { timezone: String! language: String! dateFormat: String! theme: Theme! }
enum Theme { LIGHT DARK SYSTEM }
type NotificationSettings { emailEnabled: Boolean! pushEnabled: Boolean! smsEnabled: Boolean! incidentAlerts: Boolean! dailyDigest: Boolean! weeklyReport: Boolean! }
enum UserStatus { ACTIVE INACTIVE SUSPENDED PENDING_VERIFICATION }
```

### 5. Report Types

```graphql
type Report implements Node & Timestamped {
  id: ID!
  reportId: String!
  title: String!
  type: ReportType!
  description: String
  content: JSON
  summary: String
  author: User!
  schedule: ReportSchedule
  recipients: [User!]!
  dataSources: [String!]!
  dateRange: DateRange!
  filters: [FilterInput!]
  status: ReportStatus!
  generatedAt: DateTime
  createdAt: DateTime!
  updatedAt: DateTime!
}

enum ReportType { INCIDENT_SUMMARY THREAT_ANALYSIS COMPLIANCE_REPORT RISK_ASSESSMENT EXECUTIVE_DASHBOARD CUSTOM }
type ReportSchedule { frequency: ScheduleFrequency! dayOfWeek: Int dayOfMonth: Int time: String! timezone: String! }
enum ScheduleFrequency { DAILY WEEKLY MONTHLY QUARTERLY }
enum ReportStatus { DRAFT SCHEDULED GENERATING READY FAILED }
```

### 6. Analytics Types

```graphql
type Analytics implements Node {
  id: ID!
  incidentMetrics: IncidentAnalytics!
  threatMetrics: ThreatAnalytics!
  assetMetrics: AssetAnalytics!
  complianceMetrics: ComplianceAnalytics!
  dashboards: [Dashboard!]!
}

type IncidentAnalytics {
  totalIncidents: Int!
  incidentsBySeverity: [SeverityCount!]!
  incidentsByStatus: [StatusCount!]!
  incidentsByCategory: [CategoryCount!]!
  incidentsOverTime: [TimeSeriesData!]!
  avgResolutionTime: Float!
  mttd: Float!
  mttr: Float!
}

type ThreatAnalytics {
  activeThreats: Int!
  threatsByType: [TypeCount!]!
  topThreatActors: [ThreatActor!]!
  threatTrends: [TimeSeriesData!]!
}

type AssetAnalytics {
  totalAssets: Int!
  assetsByType: [TypeCount!]!
  assetsByCriticality: [CriticalityCount!]!
  vulnerabilitySummary: VulnerabilitySummary!
}

type ComplianceAnalytics {
  overallScore: Float!
  frameworks: [FrameworkCompliance!]!
  findingsBySeverity: [SeverityCount!]!
  remediationRate: Float!
}

type Dashboard { id: ID! name: String! widgets: [Widget!]! layout: JSON isDefault: Boolean! }
type Widget { id: ID! type: WidgetType! title: String! query: String! config: JSON }
enum WidgetType { CHART_LINE CHART_BAR CHART_PIE CHART_AREA METRIC_CARD TABLE MAP GAUGE }
```

### 7. Common Types

```graphql
type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

type Comment implements Node & Timestamped {
  id: ID!
  content: String!
  author: User!
  incident: Incident!
  parent: Comment
  replies: [Comment!]!
  createdAt: DateTime!
  updatedAt: DateTime!
}

type Attachment implements Node & Timestamped {
  id: ID!
  filename: String!
  fileType: String!
  fileSize: Int!
  url: URL!
  uploadedBy: User!
  incident: Incident!
  createdAt: DateTime!
}

type TimelineEvent implements Node {
  id: ID!
  type: TimelineEventType!
  description: String!
  actor: User
  metadata: JSON
  timestamp: DateTime!
}

enum TimelineEventType { CREATED STATUS_CHANGED SEVERITY_CHANGED ASSIGNED COMMENT_ADDED ATTACHMENT_ADDED CONTAINMENT_ACTION RESOLUTION_ACTION }

type Activity implements Node {
  id: ID!
  type: ActivityType!
  description: String!
  entityType: String!
  entityId: ID!
  timestamp: DateTime!
}

enum ActivityType { INCIDENT_CREATED INCIDENT_UPDATED INCIDENT_RESOLVED THREAT_DETECTED ASSET_SCANNED REPORT_GENERATED USER_LOGIN USER_LOGOUT }
```


---

## Resolver Implementation

### 1. Query Resolvers

```python
# /app/graphql/resolvers/queries.py
from typing import List, Optional
import strawberry
from strawberry.types import Info
from app.services import IncidentService, AssetService, ThreatService
from app.auth import require_auth, require_permission
from app.dataloaders import DataLoaderRegistry

@strawberry.type
class Query:
    @strawberry.field
    async def node(self, info: Info, id: strawberry.ID) -> Optional[Node]:
        """Fetch any node by its global ID."""
        type_name, db_id = from_global_id(id)
        loaders = DataLoaderRegistry.get_loaders(info.context)
        if type_name == "Incident":
            return await loaders.incident.load(db_id)
        elif type_name == "Asset":
            return await loaders.asset.load(db_id)
        elif type_name == "Threat":
            return await loaders.threat.load(db_id)
        elif type_name == "User":
            return await loaders.user.load(db_id)
        return None
    
    @strawberry.field
    @require_auth
    @require_permission("incident", "read")
    @rate_limit(max=100, window="1m")
    @complexity(multipliers=["first"], value=5)
    async def incidents(
        self, info: Info, first: Optional[int] = 20,
        after: Optional[str] = None, filter: Optional[IncidentFilterInput] = None,
        sort: Optional[List[SortInput]] = None
    ) -> IncidentConnection:
        """Paginated list of incidents with filtering and sorting."""
        service = IncidentService(info.context.db)
        query = service.build_query()
        if filter:
            query = apply_filters(query, filter)
        if sort:
            query = apply_sorting(query, sort)
        total_count = await query.count()
        paginated_query = apply_pagination(query, first, after)
        incidents = await paginated_query.all()
        edges = [IncidentEdge(node=Incident.from_model(inc), cursor=encode_cursor(inc.id)) for inc in incidents]
        page_info = PageInfo(
            has_next_page=len(incidents) == first,
            has_previous_page=after is not None,
            start_cursor=edges[0].cursor if edges else None,
            end_cursor=edges[-1].cursor if edges else None
        )
        return IncidentConnection(edges=edges, page_info=page_info, total_count=total_count)
    
    @strawberry.field
    @require_auth
    @require_permission("incident", "read")
    @cache_control(max_age=60)
    async def incident(self, info: Info, id: Optional[strawberry.ID] = None,
                       incident_id: Optional[str] = None) -> Optional[Incident]:
        """Get a single incident by ID or incidentId."""
        service = IncidentService(info.context.db)
        if id:
            _, db_id = from_global_id(id)
            model = await service.get_by_id(db_id)
        elif incident_id:
            model = await service.get_by_incident_id(incident_id)
        else:
            raise ValueError("Either id or incident_id must be provided")
        return Incident.from_model(model) if model else None
    
    @strawberry.field
    @require_auth
    @require_permission("asset", "read")
    @complexity(multipliers=["first"], value=3)
    async def assets(self, info: Info, first: Optional[int] = 20,
                     after: Optional[str] = None, filter: Optional[AssetFilterInput] = None) -> AssetConnection:
        """Paginated list of assets."""
        service = AssetService(info.context.db)
        assets, total = await service.get_paginated(limit=first, cursor=after, filters=filter)
        return build_connection(assets, total, first, after)
    
    @strawberry.field
    @require_auth
    async def me(self, info: Info) -> User:
        """Get the current authenticated user."""
        user_id = info.context.user_id
        loaders = DataLoaderRegistry.get_loaders(info.context)
        model = await loaders.user.load(user_id)
        return User.from_model(model)
    
    @strawberry.field
    @require_auth
    @require_permission("analytics", "read")
    @cache_control(max_age=300)
    async def analytics(self, info: Info, date_range: DateRangeInput) -> Analytics:
        """Get comprehensive analytics data."""
        service = AnalyticsService(info.context.db)
        data = await service.get_analytics(date_range)
        return Analytics.from_model(data)
    
    @strawberry.field
    @require_auth
    @complexity(value=10)
    async def search(self, info: Info, query: str, types: Optional[List[SearchType]] = None,
                     first: Optional[int] = 20) -> SearchConnection:
        """Global search across all entity types."""
        search_service = SearchService(info.context.search_client)
        results = await search_service.search(query=query, types=types or [SearchType.INCIDENT, SearchType.ASSET, SearchType.THREAT], limit=first)
        edges = []
        for result in results:
            node = await resolve_search_result(info, result)
            if node:
                edges.append(SearchEdge(node=node, cursor=encode_cursor(result.id), score=result.score))
        return SearchConnection(edges=edges, page_info=PageInfo(has_next_page=len(results) == first, has_previous_page=False, start_cursor=edges[0].cursor if edges else None, end_cursor=edges[-1].cursor if edges else None), total_count=len(results))
```

### 2. Mutation Resolvers

```python
# /app/graphql/resolvers/mutations.py
import strawberry
from strawberry.types import Info
from app.services import IncidentService, AssetService, NotificationService
from app.auth import require_auth, require_permission
from app.events import publish_event

@strawberry.type
class Mutation:
    @strawberry.mutation
    @require_auth
    @require_permission("incident", "create")
    @audit_log(action="incident_created")
    async def create_incident(self, info: Info, input: CreateIncidentInput) -> CreateIncidentPayload:
        """Create a new incident."""
        service = IncidentService(info.context.db)
        incident = await service.create(
            title=input.title, description=input.description, severity=input.severity,
            category=input.category, reporter_id=info.context.user_id,
            assignee_id=input.assignee_id, assets=input.asset_ids, location=input.location
        )
        await publish_event(channel="incidents:new", data={
            "incident_id": incident.id, "title": incident.title,
            "severity": incident.severity.value, "created_by": info.context.user_id
        })
        notification_service = NotificationService()
        await notification_service.send_incident_alert(incident)
        return CreateIncidentPayload(incident=Incident.from_model(incident), success=True, message="Incident created successfully")
    
    @strawberry.mutation
    @require_auth
    @require_permission("incident", "update")
    @audit_log(action="incident_updated")
    async def update_incident(self, info: Info, id: strawberry.ID, input: UpdateIncidentInput) -> UpdateIncidentPayload:
        """Update an existing incident."""
        service = IncidentService(info.context.db)
        _, db_id = from_global_id(id)
        current = await service.get_by_id(db_id)
        if not current:
            return UpdateIncidentPayload(incident=None, success=False, message="Incident not found")
        updated = await service.update(incident_id=db_id, **input.to_dict())
        if input.status and input.status != current.status:
            await publish_event(channel=f"incidents:{db_id}:status", data={
                "incident_id": db_id, "old_status": current.status.value,
                "new_status": input.status.value, "changed_by": info.context.user_id
            })
        return UpdateIncidentPayload(incident=Incident.from_model(updated), success=True, message="Incident updated successfully")
    
    @strawberry.mutation
    @require_auth
    @require_permission("incident", "update")
    @audit_log(action="incident_assigned")
    async def assign_incident(self, info: Info, id: strawberry.ID, assignee_id: strawberry.ID) -> AssignIncidentPayload:
        """Assign an incident to a user."""
        service = IncidentService(info.context.db)
        _, incident_db_id = from_global_id(id)
        _, assignee_db_id = from_global_id(assignee_id)
        incident = await service.assign(incident_id=incident_db_id, assignee_id=assignee_db_id, assigned_by=info.context.user_id)
        notification_service = NotificationService()
        await notification_service.send_assignment_notification(incident=incident, assignee_id=assignee_db_id)
        return AssignIncidentPayload(incident=Incident.from_model(incident), success=True, message="Incident assigned successfully")
    
    @strawberry.mutation
    @require_auth
    @require_permission("incident", "update")
    @audit_log(action="incident_resolved")
    async def resolve_incident(self, info: Info, id: strawberry.ID, resolution: str, root_cause: Optional[str] = None) -> ResolveIncidentPayload:
        """Resolve an incident."""
        service = IncidentService(info.context.db)
        _, db_id = from_global_id(id)
        incident = await service.resolve(incident_id=db_id, resolution=resolution, root_cause=root_cause, resolved_by=info.context.user_id)
        await publish_event(channel=f"incidents:{db_id}:resolved", data={
            "incident_id": db_id, "resolved_by": info.context.user_id, "resolution": resolution
        })
        return ResolveIncidentPayload(incident=Incident.from_model(incident), success=True, message="Incident resolved successfully")
    
    @strawberry.mutation
    @require_auth
    @require_permission("asset", "create")
    async def create_asset(self, info: Info, input: CreateAssetInput) -> CreateAssetPayload:
        """Create a new asset."""
        service = AssetService(info.context.db)
        asset = await service.create(name=input.name, type=input.type, description=input.description,
                                     owner_id=input.owner_id, ip_addresses=input.ip_addresses, domains=input.domains)
        return CreateAssetPayload(asset=Asset.from_model(asset), success=True, message="Asset created successfully")
    
    @strawberry.mutation
    @require_auth
    @require_permission("incident", "update")
    async def bulk_update_incidents(self, info: Info, ids: List[strawberry.ID], input: BulkUpdateIncidentInput) -> BulkUpdatePayload:
        """Update multiple incidents at once."""
        service = IncidentService(info.context.db)
        db_ids = [from_global_id(id)[1] for id in ids]
        results = await service.bulk_update(db_ids, **input.to_dict())
        return BulkUpdatePayload(success_count=results.success_count, failure_count=results.failure_count, errors=results.errors, success=True, message=f"Updated {results.success_count} incidents")
```

---

## Subscriptions

### Subscription Implementation

```python
# /app/graphql/resolvers/subscriptions.py
import strawberry
from strawberry.types import Info
from typing import AsyncGenerator, Optional
import json
from app.redis_client import redis_client
from app.auth import require_auth, require_permission

@strawberry.type
class Subscription:
    @strawberry.subscription
    @require_auth
    async def incident_created(self, info: Info, severity: Optional[Severity] = None) -> AsyncGenerator[Incident, None]:
        """Subscribe to new incident creation."""
        pubsub = redis_client.pubsub()
        await pubsub.subscribe("incidents:new")
        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = json.loads(message["data"])
                    if severity and data.get("severity") != severity.value:
                        continue
                    service = IncidentService(info.context.db)
                    incident = await service.get_by_id(data["incident_id"])
                    if incident:
                        yield Incident.from_model(incident)
        finally:
            await pubsub.unsubscribe("incidents:new")
    
    @strawberry.subscription
    @require_auth
    @require_permission("incident", "read")
    async def incident_updated(self, info: Info, id: strawberry.ID) -> AsyncGenerator[IncidentUpdateEvent, None]:
        """Subscribe to updates for a specific incident."""
        _, db_id = from_global_id(id)
        channel = f"incidents:{db_id}"
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(channel)
        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = json.loads(message["data"])
                    yield IncidentUpdateEvent(
                        incident_id=id, field=data["field"], old_value=data["old_value"],
                        new_value=data["new_value"], updated_by=to_global_id("User", data["updated_by"]),
                        updated_at=datetime.fromisoformat(data["updated_at"])
                    )
        finally:
            await pubsub.unsubscribe(channel)
    
    @strawberry.subscription
    @require_auth
    @require_permission("incident", "read")
    async def incident_status_changed(self, info: Info, id: Optional[strawberry.ID] = None) -> AsyncGenerator[StatusChangeEvent, None]:
        """Subscribe to incident status changes."""
        channel = f"incidents:{from_global_id(id)[1]}:status" if id else "incidents:status_changes"
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(channel)
        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = json.loads(message["data"])
                    yield StatusChangeEvent(
                        incident_id=to_global_id("Incident", data["incident_id"]),
                        old_status=IncidentStatus[data["old_status"]],
                        new_status=IncidentStatus[data["new_status"]],
                        changed_by=to_global_id("User", data["changed_by"]),
                        changed_at=datetime.fromisoformat(data["changed_at"]),
                        reason=data.get("reason")
                    )
        finally:
            await pubsub.unsubscribe(channel)
    
    @strawberry.subscription
    @require_auth
    async def alerts(self, info: Info, severity: Optional[Severity] = None,
                     categories: Optional[List[AlertCategory]] = None) -> AsyncGenerator[Alert, None]:
        """Subscribe to real-time alerts."""
        user_id = info.context.user_id
        channel = f"user:{user_id}:alerts"
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(channel)
        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = json.loads(message["data"])
                    if severity and data.get("severity") != severity.value:
                        continue
                    if categories and data.get("category") not in [c.value for c in categories]:
                        continue
                    yield Alert(
                        id=to_global_id("Alert", data["id"]), title=data["title"], message=data["message"],
                        severity=Severity[data["severity"]], category=AlertCategory[data["category"]],
                        entity_type=data.get("entity_type"), entity_id=data.get("entity_id"),
                        created_at=datetime.fromisoformat(data["created_at"])
                    )
        finally:
            await pubsub.unsubscribe(channel)

@strawberry.type
class IncidentUpdateEvent:
    incident_id: strawberry.ID
    field: str
    old_value: Optional[str]
    new_value: str
    updated_by: strawberry.ID
    updated_at: datetime

@strawberry.type
class StatusChangeEvent:
    incident_id: strawberry.ID
    old_status: IncidentStatus
    new_status: IncidentStatus
    changed_by: strawberry.ID
    changed_at: datetime
    reason: Optional[str]

@strawberry.type
class Alert:
    id: strawberry.ID
    title: str
    message: str
    severity: Severity
    category: AlertCategory
    entity_type: Optional[str]
    entity_id: Optional[str]
    created_at: datetime
```

### WebSocket Configuration

```python
# /app/graphql/websocket.py
from fastapi import WebSocket, WebSocketDisconnect
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL
import json

class GraphQLWebSocketHandler:
    def __init__(self, schema):
        self.schema = schema
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def handle(self, websocket: WebSocket):
        await websocket.accept(subprotocol=GRAPHQL_TRANSPORT_WS_PROTOCOL)
        connection_id = str(uuid.uuid4())
        self.active_connections[connection_id] = websocket
        try:
            while True:
                message = await websocket.receive_json()
                await self.process_message(websocket, message, connection_id)
        except WebSocketDisconnect:
            del self.active_connections[connection_id]
        except Exception as e:
            await self.send_error(websocket, str(e))
            del self.active_connections[connection_id]
    
    async def process_message(self, websocket: WebSocket, message: dict, connection_id: str):
        msg_type = message.get("type")
        if msg_type == "connection_init":
            await self.handle_connection_init(websocket, message)
        elif msg_type == "subscribe":
            await self.handle_subscribe(websocket, message, connection_id)
        elif msg_type == "complete":
            await self.handle_complete(websocket, message, connection_id)
        elif msg_type == "ping":
            await websocket.send_json({"type": "pong"})
    
    async def handle_connection_init(self, websocket: WebSocket, message: dict):
        payload = message.get("payload", {})
        token = payload.get("Authorization", "").replace("Bearer ", "")
        try:
            user = await validate_token(token)
            websocket.state.user = user
            await websocket.send_json({"type": "connection_ack"})
        except AuthenticationError:
            await websocket.send_json({"type": "connection_error", "payload": {"message": "Authentication failed"}})
    
    async def handle_subscribe(self, websocket: WebSocket, message: dict, connection_id: str):
        id = message.get("id")
        payload = message.get("payload", {})
        query = payload.get("query")
        variables = payload.get("variables", {})
        result = await self.schema.subscribe(query, variable_values=variables, context_value={"websocket": websocket, "user": websocket.state.user})
        async for item in result:
            await websocket.send_json({"type": "next", "id": id, "payload": {"data": item.data, "errors": item.errors}})
        await websocket.send_json({"type": "complete", "id": id})
```


---

## DataLoader Implementation

### DataLoader Registry

```python
# /app/graphql/dataloaders.py
from typing import List, Dict
from collections import defaultdict
from promise.dataloader import DataLoader
from app.services import IncidentService, AssetService, ThreatService, UserService

class BaseDataLoader(DataLoader):
    def __init__(self, db_session, cache_map=None):
        super().__init__(cache_map=cache_map)
        self.db = db_session
        self.cache = True
    
    def get_cache_key(self, key):
        return str(key)

class IncidentLoader(BaseDataLoader):
    async def batch_load_fn(self, keys: List[str]) -> List[Incident]:
        service = IncidentService(self.db)
        incidents = await service.get_by_ids(keys)
        incident_map = {str(inc.id): inc for inc in incidents}
        return [incident_map.get(str(key)) for key in keys]

class AssetLoader(BaseDataLoader):
    async def batch_load_fn(self, keys: List[str]) -> List[Asset]:
        service = AssetService(self.db)
        assets = await service.get_by_ids(keys)
        asset_map = {str(asset.id): asset for asset in assets}
        return [asset_map.get(str(key)) for key in keys]

class ThreatLoader(BaseDataLoader):
    async def batch_load_fn(self, keys: List[str]) -> List[Threat]:
        service = ThreatService(self.db)
        threats = await service.get_by_ids(keys)
        threat_map = {str(threat.id): threat for threat in threats}
        return [threat_map.get(str(key)) for key in keys]

class UserLoader(BaseDataLoader):
    async def batch_load_fn(self, keys: List[str]) -> List[User]:
        service = UserService(self.db)
        users = await service.get_by_ids(keys)
        user_map = {str(user.id): user for user in users}
        return [user_map.get(str(key)) for key in keys]

class IncidentAssetsLoader(BaseDataLoader):
    async def batch_load_fn(self, incident_ids: List[str]) -> List[List[Asset]]:
        service = IncidentService(self.db)
        relationships = await service.get_assets_for_incidents(incident_ids)
        assets_by_incident = defaultdict(list)
        for rel in relationships:
            assets_by_incident[str(rel.incident_id)].append(rel.asset)
        return [assets_by_incident.get(str(inc_id), []) for inc_id in incident_ids]

class IncidentCommentsLoader(BaseDataLoader):
    async def batch_load_fn(self, incident_ids: List[str]) -> List[List[Comment]]:
        service = IncidentService(self.db)
        comments = await service.get_comments_for_incidents(incident_ids)
        comments_by_incident = defaultdict(list)
        for comment in comments:
            comments_by_incident[str(comment.incident_id)].append(comment)
        return [comments_by_incident.get(str(inc_id), []) for inc_id in incident_ids]

class DataLoaderRegistry:
    def __init__(self, db_session):
        self.db = db_session
        self._loaders: Dict[str, DataLoader] = {}
    
    @property
    def incident(self) -> IncidentLoader:
        if "incident" not in self._loaders:
            self._loaders["incident"] = IncidentLoader(self.db)
        return self._loaders["incident"]
    
    @property
    def asset(self) -> AssetLoader:
        if "asset" not in self._loaders:
            self._loaders["asset"] = AssetLoader(self.db)
        return self._loaders["asset"]
    
    @property
    def threat(self) -> ThreatLoader:
        if "threat" not in self._loaders:
            self._loaders["threat"] = ThreatLoader(self.db)
        return self._loaders["threat"]
    
    @property
    def user(self) -> UserLoader:
        if "user" not in self._loaders:
            self._loaders["user"] = UserLoader(self.db)
        return self._loaders["user"]
    
    @property
    def incident_assets(self) -> IncidentAssetsLoader:
        if "incident_assets" not in self._loaders:
            self._loaders["incident_assets"] = IncidentAssetsLoader(self.db)
        return self._loaders["incident_assets"]
    
    @property
    def incident_comments(self) -> IncidentCommentsLoader:
        if "incident_comments" not in self._loaders:
            self._loaders["incident_comments"] = IncidentCommentsLoader(self.db)
        return self._loaders["incident_comments"]
    
    def clear_all(self):
        for loader in self._loaders.values():
            loader.clear_all()
    
    @staticmethod
    def get_loaders(context) -> "DataLoaderRegistry":
        if not hasattr(context, "loaders"):
            context.loaders = DataLoaderRegistry(context.db)
        return context.loaders

class GraphQLContext:
    def __init__(self, db_session, user_id: str = None, request=None):
        self.db = db_session
        self.user_id = user_id
        self.request = request
        self._loaders: DataLoaderRegistry = None
    
    @property
    def loaders(self) -> DataLoaderRegistry:
        if self._loaders is None:
            self._loaders = DataLoaderRegistry(self.db)
        return self._loaders
    
    def clear_loaders(self):
        if self._loaders:
            self._loaders.clear_all()
```

---

## Federation Architecture

### Federation Gateway

```python
# /app/federation/gateway.py
from strawberry.federation import Schema
from strawberry.federation.schema_directives import Key, External
import httpx

class FederatedGateway:
    def __init__(self):
        self.subgraphs: Dict[str, SubgraphConfig] = {}
        self.supergraph_schema: str = None
    
    def register_subgraph(self, name: str, url: str, schema_sdl: str):
        self.subgraphs[name] = SubgraphConfig(name=name, url=url, schema_sdl=schema_sdl)
    
    async def compose_supergraph(self) -> str:
        composition = SupergraphComposer()
        for subgraph in self.subgraphs.values():
            composition.add_subgraph(subgraph)
        self.composition = await composition.compose()
        self.supergraph_schema = self.composition.to_sdl()
        return self.supergraph_schema

@strawberry.federation.type(keys=["id"])
class Incident:
    id: strawberry.ID
    incident_id: str
    reporter: User = strawberry.federation.field(external=True)
    assignee: User = strawberry.federation.field(external=True)
    assets: List[Asset] = strawberry.federation.field(external=True)
    
    @strawberry.field
    async def resolve_reference(cls, info, representation):
        incident_id = representation.get("id")
        service = IncidentService(info.context.db)
        incident = await service.get_by_id(incident_id)
        return Incident.from_model(incident)

@strawberry.federation.type(keys=["id"], extend=True)
class User:
    id: strawberry.ID = strawberry.federation.field(external=True)
    reported_incidents: List[Incident]
    assigned_incidents: List[Incident]
    incident_stats: IncidentUserStats

# Subgraph Schema Definitions
INCIDENT_SUBGRAPH_SCHEMA = """
    extend type Query {
        incident(id: ID!): Incident
        incidents(first: Int = 20, after: String, filter: IncidentFilterInput): IncidentConnection
    }
    type Incident @key(fields: "id") @key(fields: "incidentId") {
        id: ID!
        incidentId: String!
        title: String!
        reporter: User! @external
        assignee: User @external
        assets: [Asset!]! @external
    }
    extend type User @key(fields: "id") {
        id: ID! @external
        reportedIncidents: [Incident!]!
        assignedIncidents: [Incident!]!
    }
"""

USER_SUBGRAPH_SCHEMA = """
    type User @key(fields: "id") @key(fields: "email") {
        id: ID!
        email: String!
        username: String!
        role: Role!
    }
    extend type Incident @key(fields: "id") {
        id: ID! @external
        reporter: User!
        assignee: User
    }
"""

ASSET_SUBGRAPH_SCHEMA = """
    type Asset @key(fields: "id") @key(fields: "assetId") {
        id: ID!
        assetId: String!
        name: String!
        owner: User! @external
        incidents: [Incident!]! @external
    }
"""
```

---

## Authentication & Authorization

### JWT Authentication

```python
# /app/auth/graphql_auth.py
import jwt
from datetime import datetime, timedelta
from functools import wraps
import strawberry
from strawberry.types import Info

class JWTConfig:
    SECRET_KEY = "your-secret-key"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7

class AuthContext:
    def __init__(self, user_id: Optional[str] = None, permissions: list = None, role: Optional[str] = None):
        self.user_id = user_id
        self.permissions = permissions or []
        self.role = role
        self.is_authenticated = user_id is not None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, JWTConfig.SECRET_KEY, algorithm=JWTConfig.ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWTConfig.SECRET_KEY, algorithms=[JWTConfig.ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token")

def get_auth_context(info: Info) -> AuthContext:
    request = info.context.request
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return AuthContext()
    token = auth_header.replace("Bearer ", "")
    try:
        payload = decode_token(token)
        return AuthContext(user_id=payload.get("sub"), permissions=payload.get("permissions", []), role=payload.get("role"))
    except AuthenticationError:
        return AuthContext()

def require_auth(resolver: Callable) -> Callable:
    @wraps(resolver)
    async def wrapper(self, info: Info, *args, **kwargs):
        auth_context = get_auth_context(info)
        if not auth_context.is_authenticated:
            raise AuthenticationError("Authentication required")
        info.context.auth = auth_context
        info.context.user_id = auth_context.user_id
        return await resolver(self, info, *args, **kwargs)
    return wrapper

def require_permission(resource: str, action: str):
    def decorator(resolver: Callable) -> Callable:
        @wraps(resolver)
        async def wrapper(self, info: Info, *args, **kwargs):
            auth_context = get_auth_context(info)
            if not auth_context.is_authenticated:
                raise AuthenticationError("Authentication required")
            required_permission = f"{resource}:{action}"
            if required_permission not in auth_context.permissions:
                if not has_role_permission(auth_context.role, resource, action):
                    raise AuthorizationError(f"Permission denied: {required_permission} required")
            return await resolver(self, info, *args, **kwargs)
        return wrapper
    return decorator

def has_role_permission(role: str, resource: str, action: str) -> bool:
    role_permissions = {
        "USER": ["incident:read", "asset:read", "threat:read"],
        "ANALYST": ["incident:read", "incident:update", "incident:create", "asset:read", "threat:read", "report:read"],
        "MANAGER": ["incident:*", "asset:*", "threat:*", "report:*", "user:read"],
        "ADMIN": ["*"],
        "SYSTEM": ["*"],
    }
    permissions = role_permissions.get(role, [])
    required = f"{resource}:{action}"
    for permission in permissions:
        if permission == "*" or permission == required:
            return True
        if permission.endswith(":*") and required.startswith(permission[:-1]):
            return True
    return False

@strawberry.type
class AuthMutation:
    @strawberry.mutation
    async def login(self, info: Info, email: str, password: str) -> LoginPayload:
        user_service = UserService(info.context.db)
        user = await user_service.authenticate(email, password)
        if not user:
            return LoginPayload(success=False, message="Invalid credentials", access_token=None, refresh_token=None)
        token_data = {"sub": str(user.id), "email": user.email, "role": user.role.value, "permissions": user.permissions}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        return LoginPayload(success=True, message="Login successful", access_token=access_token, refresh_token=refresh_token, user=User.from_model(user))
    
    @strawberry.mutation
    async def refresh_token(self, info: Info, refresh_token: str) -> RefreshTokenPayload:
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise AuthenticationError("Invalid token type")
            token_data = {"sub": payload["sub"], "email": payload["email"], "role": payload["role"], "permissions": payload["permissions"]}
            new_access_token = create_access_token(token_data)
            return RefreshTokenPayload(success=True, access_token=new_access_token)
        except AuthenticationError as e:
            return RefreshTokenPayload(success=False, message=str(e), access_token=None)

@strawberry.type
class LoginPayload:
    success: bool
    message: str
    access_token: Optional[str]
    refresh_token: Optional[str]
    user: Optional[User]

@strawberry.type
class RefreshTokenPayload:
    success: bool
    message: Optional[str]
    access_token: Optional[str]
```

---

## Query Complexity Analysis

### Complexity Calculator

```python
# /app/graphql/complexity.py
from typing import Dict, Any, Optional
from graphql import parse, visit, Visitor
import strawberry

class ComplexityConfig:
    DEFAULT_COMPLEXITY = 1
    DEFAULT_MULTIPLIER = 10
    MAX_COMPLEXITY = 1000
    MAX_DEPTH = 15
    FIELD_SCORES = {
        "incidents": 5, "assets": 3, "threats": 5, "users": 2, "search": 10, "analytics": 8,
        "comments": 2, "attachments": 2, "timeline": 3, "vulnerabilities": 4,
        "id": 0, "name": 0, "title": 0, "description": 0, "createdAt": 0, "updatedAt": 0,
    }

class ComplexityAnalyzer:
    def __init__(self, config: ComplexityConfig = None):
        self.config = config or ComplexityConfig()
    
    def analyze(self, query: str, variables: Dict[str, Any] = None) -> "ComplexityResult":
        try:
            document = parse(query)
        except Exception as e:
            return ComplexityResult(complexity=0, depth=0, valid=False, error=f"Parse error: {str(e)}")
        visitor = ComplexityVisitor(self.config, variables or {})
        visit(document, visitor)
        return ComplexityResult(
            complexity=visitor.complexity, depth=visitor.max_depth,
            valid=visitor.complexity <= self.config.MAX_COMPLEXITY and visitor.max_depth <= self.config.MAX_DEPTH,
            exceeded_complexity=visitor.complexity > self.config.MAX_COMPLEXITY,
            exceeded_depth=visitor.max_depth > self.config.MAX_DEPTH, details=visitor.details
        )

class ComplexityVisitor(Visitor):
    def __init__(self, config: ComplexityConfig, variables: Dict[str, Any]):
        self.config = config
        self.variables = variables
        self.complexity = 0
        self.max_depth = 0
        self.current_depth = 0
        self.details = []
    
    def enter_field(self, node, key, parent, path, ancestors):
        field_name = node.name.value
        base_complexity = self.config.FIELD_SCORES.get(field_name, self.config.DEFAULT_COMPLEXITY)
        multiplier = 1
        if node.arguments:
            for arg in node.arguments:
                if arg.name.value in ["first", "last"]:
                    multiplier = self._get_argument_value(arg)
                    multiplier = min(multiplier, self.config.DEFAULT_MULTIPLIER)
        field_complexity = base_complexity * multiplier
        self.complexity += field_complexity
        self.details.append({"field": field_name, "base_complexity": base_complexity, "multiplier": multiplier, "total": field_complexity, "depth": self.current_depth})
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
    
    def leave_field(self, node, key, parent, path, ancestors):
        self.current_depth -= 1
    
    def _get_argument_value(self, argument) -> int:
        value = argument.value
        if value.kind == "int_value":
            return int(value.value)
        elif value.kind == "variable":
            return self.variables.get(value.name.value, self.config.DEFAULT_MULTIPLIER)
        return self.config.DEFAULT_MULTIPLIER

@strawberry.type
class ComplexityResult:
    complexity: int
    depth: int
    valid: bool
    exceeded_complexity: bool = False
    exceeded_depth: bool = False
    error: Optional[str] = None
    details: Optional[list] = None

class ComplexityMiddleware:
    def __init__(self, config: ComplexityConfig = None):
        self.analyzer = ComplexityAnalyzer(config)
    
    async def resolve(self, next, root, info, **args):
        if root is not None:
            return await next(root, info, **args)
        query = info.context.get("query")
        variables = info.context.get("variables", {})
        if query:
            result = self.analyzer.analyze(query, variables)
            if not result.valid:
                error_msg = []
                if result.exceeded_complexity:
                    error_msg.append(f"Query complexity {result.complexity} exceeds maximum {self.analyzer.config.MAX_COMPLEXITY}")
                if result.exceeded_depth:
                    error_msg.append(f"Query depth {result.depth} exceeds maximum {self.analyzer.config.MAX_DEPTH}")
                raise ComplexityError("; ".join(error_msg))
            info.context["complexity"] = result.complexity
            info.context["depth"] = result.depth
        return await next(root, info, **args)

class ComplexityError(Exception):
    pass

def complexity(multipliers: list = None, value: int = 1):
    def decorator(resolver):
        resolver._complexity = {"value": value, "multipliers": multipliers or []}
        return resolver
    return decorator
```


---

## Schema Stitching

### Schema Stitching Implementation

```python
# /app/graphql/schema_stitching.py
from typing import List, Dict, Any
from graphql import build_schema, GraphQLSchema

class SchemaStitcher:
    def __init__(self):
        self.schemas: Dict[str, GraphQLSchema] = {}
        self.type_mergers: Dict[str, TypeMerger] = {}
        self.resolver_map: Dict[str, callable] = {}
    
    def add_schema(self, name: str, schema: GraphQLSchema, prefix: str = None):
        self.schemas[name] = {"schema": schema, "prefix": prefix}
    
    def add_type_merger(self, type_name: str, merger: "TypeMerger"):
        self.type_mergers[type_name] = merger
    
    def stitch(self) -> GraphQLSchema:
        all_types, all_queries, all_mutations, all_subscriptions = {}, {}, {}, {}
        for schema_name, schema_config in self.schemas.items():
            schema, prefix = schema_config["schema"], schema_config["prefix"]
            for type_name, type_def in schema.type_map.items():
                if type_name.startswith("__"):
                    continue
                prefixed_name = f"{prefix}_{type_name}" if prefix else type_name
                if prefixed_name in all_types:
                    all_types[prefixed_name] = self._merge_types(all_types[prefixed_name], type_def, prefixed_name)
                else:
                    all_types[prefixed_name] = type_def
            if schema.query_type:
                for field_name, field_def in schema.query_type.fields.items():
                    all_queries[f"{prefix}_{field_name}" if prefix else field_name] = field_def
            if schema.mutation_type:
                for field_name, field_def in schema.mutation_type.fields.items():
                    all_mutations[f"{prefix}_{field_name}" if prefix else field_name] = field_def
        stitched_sdl = self._build_schema_sdl(all_types, all_queries, all_mutations, all_subscriptions)
        return build_schema(stitched_sdl)
    
    def _merge_types(self, existing, new, type_name: str) -> Any:
        if type_name in self.type_mergers:
            return self.type_mergers[type_name].merge(existing, new)
        merged_fields = {**existing.fields, **new.fields}
        return type(existing)(name=type_name, fields=merged_fields, description=existing.description or new.description)

class TypeMerger:
    def merge(self, existing: Any, new: Any) -> Any:
        raise NotImplementedError

class IncidentTypeMerger(TypeMerger):
    def merge(self, existing: Any, new: Any) -> Any:
        merged_fields = {**new.fields, **existing.fields}
        required_fields = ["id", "incidentId", "title", "status"]
        for field in required_fields:
            if field not in merged_fields:
                raise ValueError(f"Required field '{field}' missing in merged Incident type")
        return type(existing)(name="Incident", fields=merged_fields, description="Merged Incident type")

class RemoteSchemaFetcher:
    def __init__(self):
        self.client = httpx.AsyncClient()
    
    async def fetch_schema(self, endpoint: str, headers: dict = None) -> GraphQLSchema:
        introspection_query = """
            query IntrospectionQuery {
                __schema { queryType { name } mutationType { name } subscriptionType { name }
                    types { ...FullType }
                    directives { name description locations args { ...InputValue } }
                }
            }
            fragment FullType on __Type { kind name description fields(includeDeprecated: true) { name description args { ...InputValue } type { ...TypeRef } isDeprecated deprecationReason } inputFields { ...InputValue } interfaces { ...TypeRef } enumValues(includeDeprecated: true) { name description isDeprecated deprecationReason } possibleTypes { ...TypeRef } }
            fragment InputValue on __InputValue { name description type { ...TypeRef } defaultValue }
            fragment TypeRef on __Type { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name } } } } } } } }
        """
        response = await self.client.post(endpoint, json={"query": introspection_query}, headers=headers or {})
        introspection_result = response.json()
        return build_client_schema(introspection_result["data"])

class RESTSchemaAdapter:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    def generate_schema(self) -> GraphQLSchema:
        schema_sdl = """
            type Query { legacyIncident(id: ID!): LegacyIncident legacyIncidents: [LegacyIncident!]! }
            type LegacyIncident { id: ID! legacyId: String! title: String! description: String createdAt: String }
        """
        return build_schema(schema_sdl)
```

---

## GraphQL Playground

### Playground Configuration

```python
# /app/graphql/playground.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import strawberry
from strawberry.fastapi import GraphQLRouter
import json

class PlaygroundConfig:
    DEFAULT_HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}
    DEFAULT_SETTINGS = {
        "editor.cursorShape": "line", "editor.fontSize": 14, "editor.reuseHeaders": True,
        "editor.theme": "dark", "request.credentials": "include", "schema.polling.enable": True,
        "schema.polling.interval": 5000, "tracing.hideTracingResponse": True
    }
    EXAMPLE_QUERIES = {
        "Get Incident": """query GetIncident($id: ID!) { incident(id: $id) { id incidentId title severity status createdAt reporter { id fullName email } } }""",
        "List Incidents": """query ListIncidents($first: Int) { incidents(first: $first) { edges { node { id incidentId title severity status } cursor } pageInfo { hasNextPage endCursor } totalCount } }""",
        "Create Incident": """mutation CreateIncident($input: CreateIncidentInput!) { createIncident(input: $input) { incident { id incidentId title status } success message } }""",
        "Subscribe to New Incidents": """subscription OnIncidentCreated($severity: Severity) { incidentCreated(severity: $severity) { id incidentId title severity createdAt } }"""
    }

def create_playground_html(endpoint: str, subscription_endpoint: str = None) -> str:
    config = PlaygroundConfig()
    tabs = [{"name": name, "query": query.strip()} for name, query in config.EXAMPLE_QUERIES.items()]
    settings_json = json.dumps(config.DEFAULT_SETTINGS)
    tabs_json = json.dumps(tabs)
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8" />
    <title>ResilienceAI GraphQL Playground</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@graphql-playground/react@1.7.27/build/static/css/index.css" />
    <script src="https://cdn.jsdelivr.net/npm/@graphql-playground/react@1.7.27/build/static/js/middleware.js"></script>
</head>
<body>
    <div id="root"></div>
    <script>
        window.addEventListener('load', function() {{
            GraphQLPlayground.init(document.getElementById('root'), {{
                endpoint: '{endpoint}', subscriptionEndpoint: '{subscription_endpoint or endpoint}',
                headers: {json.dumps(config.DEFAULT_HEADERS)}, settings: {settings_json}, tabs: {tabs_json}
            }})
        }})
    </script>
</body>
</html>
"""

def setup_playground(app: FastAPI, graphql_router: GraphQLRouter, path: str = "/playground"):
    @app.get(path, response_class=HTMLResponse)
    async def playground(request: Request):
        endpoint = str(request.base_url) + "graphql"
        subscription_endpoint = endpoint.replace("http", "ws")
        html = create_playground_html(endpoint, subscription_endpoint)
        return HTMLResponse(content=html)
```

---

## Client Integration

### Apollo Client Configuration

```typescript
// client/src/graphql/client.ts
import { ApolloClient, InMemoryCache, HttpLink, split } from '@apollo/client';
import { WebSocketLink } from '@apollo/client/link/ws';
import { getMainDefinition } from '@apollo/client/utilities';
import { setContext } from '@apollo/client/link/context';
import { onError } from '@apollo/client/link/error';
import { RetryLink } from '@apollo/client/link/retry';

const httpLink = new HttpLink({
  uri: process.env.REACT_APP_GRAPHQL_ENDPOINT || 'http://localhost:8000/graphql',
  credentials: 'include',
});

const wsLink = new WebSocketLink({
  uri: process.env.REACT_APP_GRAPHQL_WS_ENDPOINT || 'ws://localhost:8000/graphql',
  options: { reconnect: true, connectionParams: () => ({ Authorization: `Bearer ${localStorage.getItem('access_token')}` }) },
});

const authLink = setContext((_, { headers }) => {
  const token = localStorage.getItem('access_token');
  return { headers: { ...headers, Authorization: token ? `Bearer ${token}` : '' } };
});

const errorLink = onError(({ graphQLErrors, networkError, operation, forward }) => {
  if (graphQLErrors) {
    for (const error of graphQLErrors) {
      console.error('GraphQL Error:', error);
      if (error.extensions?.code === 'UNAUTHENTICATED') return refreshToken().then(() => forward(operation));
      if (error.extensions?.code === 'COMPLEXITY_EXCEEDED') showNotification('error', 'Query too complex. Please simplify your request.');
    }
  }
  if (networkError) console.error('Network Error:', networkError);
});

const retryLink = new RetryLink({ delay: { initial: 300, max: 10000, jitter: true }, attempts: { max: 5, retryIf: (error, operation) => !!error && operation.operationName !== 'login' } });

const splitLink = split(({ query }) => {
  const definition = getMainDefinition(query);
  return definition.kind === 'OperationDefinition' && definition.operation === 'subscription';
}, wsLink, authLink.concat(httpLink));

const cache = new InMemoryCache({
  typePolicies: {
    Query: { fields: { incidents: { keyArgs: ['filter', 'sort'], merge(existing, incoming, { args }) { if (!args?.after) return incoming; return { ...incoming, edges: [...(existing?.edges || []), ...incoming.edges] }; } } } },
    Incident: { keyFields: ['id'], fields: { comments: { merge(existing, incoming) { return incoming; } } } },
  },
});

export const client = new ApolloClient({
  link: errorLink.concat(retryLink).concat(splitLink),
  cache,
  defaultOptions: {
    watchQuery: { fetchPolicy: 'cache-and-network', nextFetchPolicy: 'cache-first' },
    query: { fetchPolicy: 'network-only' },
    mutate: { fetchPolicy: 'no-cache' },
  },
});

async function refreshToken(): Promise<void> {
  const refreshToken = localStorage.getItem('refresh_token');
  if (!refreshToken) { window.location.href = '/login'; return; }
  try {
    const response = await fetch('/graphql', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: `mutation RefreshToken($token: String!) { refreshToken(refreshToken: $token) { success accessToken } }`, variables: { token: refreshToken } }),
    });
    const data = await response.json();
    if (data.data?.refreshToken?.success) localStorage.setItem('access_token', data.data.refreshToken.accessToken);
    else window.location.href = '/login';
  } catch (error) { console.error('Token refresh failed:', error); window.location.href = '/login'; }
}
```

### React Hooks

```typescript
// client/src/graphql/hooks.ts
import { useQuery, useMutation, useSubscription, useLazyQuery } from '@apollo/client';
import { GET_INCIDENT, GET_INCIDENTS, CREATE_INCIDENT, UPDATE_INCIDENT, INCIDENT_CREATED_SUBSCRIPTION, SEARCH } from './queries';

export function useIncidents(variables?: any) {
  return useQuery(GET_INCIDENTS, { variables, notifyOnNetworkStatusChange: true });
}

export function useIncident(id: string) {
  return useQuery(GET_INCIDENT, { variables: { id }, skip: !id });
}

export function useCreateIncident() {
  return useMutation(CREATE_INCIDENT, {
    update(cache, { data }) {
      cache.modify({
        fields: {
          incidents(existing = {}) {
            const newIncident = data?.createIncident?.incident;
            if (newIncident) {
              return { ...existing, edges: [{ __typename: 'IncidentEdge', node: newIncident, cursor: newIncident.id }, ...(existing.edges || [])], totalCount: (existing.totalCount || 0) + 1 };
            }
            return existing;
          },
        },
      });
    },
  });
}

export function useUpdateIncident() {
  return useMutation(UPDATE_INCIDENT);
}

export function useIncidentSubscription(severity?: string) {
  return useSubscription(INCIDENT_CREATED_SUBSCRIPTION, { variables: { severity } });
}

export function useSearch() {
  return useLazyQuery(SEARCH, { fetchPolicy: 'network-only' });
}
```

### GraphQL Queries

```typescript
// client/src/graphql/queries.ts
import { gql } from '@apollo/client';

export const INCIDENT_FRAGMENT = gql`
  fragment IncidentFields on Incident {
    id incidentId title description severity status category createdAt updatedAt resolvedAt
  }
`;

export const USER_FRAGMENT = gql`
  fragment UserFields on User {
    id userId email username fullName avatar role
  }
`;

export const GET_INCIDENTS = gql`
  query GetIncidents($first: Int, $after: String, $filter: IncidentFilterInput, $sort: [SortInput!]) {
    incidents(first: $first, after: $after, filter: $filter, sort: $sort) {
      edges { node { ...IncidentFields reporter { ...UserFields } assignee { ...UserFields } } cursor }
      pageInfo { hasNextPage hasPreviousPage startCursor endCursor } totalCount
    }
  }
  ${INCIDENT_FRAGMENT} ${USER_FRAGMENT}
`;

export const GET_INCIDENT = gql`
  query GetIncident($id: ID!) {
    incident(id: $id) {
      ...IncidentFields reporter { ...UserFields } assignee { ...UserFields }
      assets { id assetId name type status }
      threats { id threatId name type severity }
      comments { id content author { ...UserFields } createdAt }
      timeline { id type description timestamp }
      metrics { responseTime resolutionTime impactScore }
    }
  }
  ${INCIDENT_FRAGMENT} ${USER_FRAGMENT}
`;

export const CREATE_INCIDENT = gql`
  mutation CreateIncident($input: CreateIncidentInput!) {
    createIncident(input: $input) { incident { ...IncidentFields reporter { ...UserFields } } success message }
  }
  ${INCIDENT_FRAGMENT} ${USER_FRAGMENT}
`;

export const UPDATE_INCIDENT = gql`
  mutation UpdateIncident($id: ID!, $input: UpdateIncidentInput!) {
    updateIncident(id: $id, input: $input) { incident { ...IncidentFields } success message }
  }
  ${INCIDENT_FRAGMENT}
`;

export const INCIDENT_CREATED_SUBSCRIPTION = gql`
  subscription OnIncidentCreated($severity: Severity) {
    incidentCreated(severity: $severity) { ...IncidentFields reporter { ...UserFields } }
  }
  ${INCIDENT_FRAGMENT} ${USER_FRAGMENT}
`;

export const ALERTS_SUBSCRIPTION = gql`
  subscription OnAlerts($severity: Severity, $categories: [AlertCategory!]) {
    alerts(severity: $severity, categories: $categories) { id title message severity category entityType entityId createdAt }
  }
`;
```


---

## Deployment Guide

### Docker Configuration

```dockerfile
# Dockerfile.graphql
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
COPY graphql/ ./graphql/
ENV PYTHONPATH=/app
ENV PORT=8000
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Kubernetes Deployment

```yaml
# k8s/graphql-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: graphql-api
  namespace: resilienceai
  labels:
    app: graphql-api
    version: v2.0.0
spec:
  replicas: 3
  selector:
    matchLabels:
      app: graphql-api
  template:
    metadata:
      labels:
        app: graphql-api
        version: v2.0.0
    spec:
      containers:
        - name: graphql-api
          image: resilienceai/graphql-api:v2.0.0
          ports:
            - containerPort: 8000
              name: http
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: url
            - name: REDIS_URL
              valueFrom:
                secretKeyRef:
                  name: redis-credentials
                  key: url
            - name: JWT_SECRET
              valueFrom:
                secretKeyRef:
                  name: jwt-secret
                  key: secret
          resources:
            requests:
              memory: "512Mi"
              cpu: "500m"
            limits:
              memory: "1Gi"
              cpu: "1000m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: graphql-api
  namespace: resilienceai
spec:
  selector:
    app: graphql-api
  ports:
    - port: 80
      targetPort: 8000
      name: http
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: graphql-api
  namespace: resilienceai
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
    nginx.ingress.kubernetes.io/enable-cors: "true"
spec:
  tls:
    - hosts:
        - api.resilienceai.io
      secretName: tls-secret
  rules:
    - host: api.resilienceai.io
      http:
        paths:
          - path: /graphql
            pathType: Prefix
            backend:
              service:
                name: graphql-api
                port:
                  number: 80
          - path: /playground
            pathType: Prefix
            backend:
              service:
                name: graphql-api
                port:
                  number: 80
```

### Environment Configuration

```python
# /app/config/graphql.py
from pydantic import BaseSettings
from typing import List

class GraphQLConfig(BaseSettings):
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str
    REDIS_DB: int = 0
    
    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Complexity
    MAX_QUERY_COMPLEXITY: int = 1000
    MAX_QUERY_DEPTH: int = 15
    DEFAULT_PAGINATION_LIMIT: int = 20
    MAX_PAGINATION_LIMIT: int = 100
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: int = 100
    RATE_LIMIT_BURST: int = 150
    
    # Caching
    CACHE_ENABLED: bool = True
    CACHE_DEFAULT_TTL: int = 300
    CACHE_MAX_SIZE: int = 10000
    
    # Subscriptions
    SUBSCRIPTION_ENABLED: bool = True
    SUBSCRIPTION_KEEPALIVE: int = 30
    
    # Federation
    FEDERATION_ENABLED: bool = False
    FEDERATION_SUBGRAPHS: List[str] = []
    
    # Monitoring
    METRICS_ENABLED: bool = True
    TRACING_ENABLED: bool = True
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_prefix = "GRAPHQL_"

config = GraphQLConfig()
```

---

## Implementation Priority

### Phase 1: Core Foundation (Weeks 1-2)

| Priority | Component | Effort | Impact |
|----------|-----------|--------|--------|
| 1 | Schema Design & Type Definitions | Medium | High |
| 2 | Basic Query Resolvers | Medium | High |
| 3 | JWT Authentication | Low | High |
| 4 | DataLoader Implementation | Medium | High |
| 5 | GraphQL Playground | Low | Medium |

### Phase 2: Core Features (Weeks 3-4)

| Priority | Component | Effort | Impact |
|----------|-----------|--------|--------|
| 6 | Mutation Resolvers | Medium | High |
| 7 | Pagination & Filtering | Medium | High |
| 8 | Query Complexity Analysis | Medium | Medium |
| 9 | Rate Limiting | Low | Medium |
| 10 | Error Handling | Low | Medium |

### Phase 3: Advanced Features (Weeks 5-6)

| Priority | Component | Effort | Impact |
|----------|-----------|--------|--------|
| 11 | Subscriptions | High | High |
| 12 | Redis Pub/Sub | Medium | High |
| 13 | Authorization Layer | Medium | High |
| 14 | Caching Strategy | Medium | Medium |
| 15 | Monitoring & Tracing | Medium | Medium |

### Phase 4: Enterprise Features (Weeks 7-8)

| Priority | Component | Effort | Impact |
|----------|-----------|--------|--------|
| 16 | Federation Architecture | High | Medium |
| 17 | Schema Stitching | High | Low |
| 18 | Performance Optimization | High | Medium |
| 19 | Load Testing | Medium | Medium |
| 20 | Documentation | Medium | High |

---

## Summary

This comprehensive GraphQL API design for ResilienceAI provides:

1. **Flexible Schema Design** - Complete type system with interfaces, unions, and custom scalars
2. **Efficient Data Loading** - DataLoader pattern for N+1 query elimination
3. **Real-time Capabilities** - WebSocket subscriptions for live updates
4. **Security** - JWT authentication, field-level authorization, and query complexity limits
5. **Scalability** - Federation support for microservices architecture
6. **Developer Experience** - GraphQL Playground with examples and documentation
7. **Production Ready** - Monitoring, caching, rate limiting, and deployment configurations

The implementation follows a phased approach, prioritizing core functionality first, then adding advanced features for enterprise use cases.

---

## Key Files Generated

| File Path | Description |
|-----------|-------------|
| `/app/graphql/resolvers/queries.py` | Query resolver implementations |
| `/app/graphql/resolvers/mutations.py` | Mutation resolver implementations |
| `/app/graphql/resolvers/subscriptions.py` | Subscription resolver implementations |
| `/app/graphql/dataloaders.py` | DataLoader registry and implementations |
| `/app/graphql/websocket.py` | WebSocket handler for subscriptions |
| `/app/federation/gateway.py` | Federation gateway configuration |
| `/app/auth/graphql_auth.py` | JWT authentication and authorization |
| `/app/graphql/complexity.py` | Query complexity analysis |
| `/app/graphql/schema_stitching.py` | Schema stitching implementation |
| `/app/graphql/playground.py` | GraphQL Playground configuration |
| `/app/config/graphql.py` | GraphQL configuration settings |
| `Dockerfile.graphql` | Docker configuration |
| `k8s/graphql-deployment.yaml` | Kubernetes deployment manifests |
| `client/src/graphql/client.ts` | Apollo Client configuration |
| `client/src/graphql/hooks.ts` | React hooks for GraphQL operations |
| `client/src/graphql/queries.ts` | GraphQL queries and fragments |
