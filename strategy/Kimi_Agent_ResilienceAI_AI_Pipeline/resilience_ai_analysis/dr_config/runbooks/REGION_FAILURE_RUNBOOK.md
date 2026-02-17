# Region Failure Runbook

## Overview

This runbook provides step-by-step instructions for responding to a complete region failure in ResilienceAI.

**Last Updated:** 2024-01-15  
**Owner:** Operations Team  
**Review Frequency:** Quarterly  

---

## Detection

### Symptoms
- Multiple services reporting unhealthy in primary region
- Health checks failing for > 2 minutes
- Increased error rates from primary region
- Alert: `PrimaryRegionUnhealthy`

### Validation
1. Check primary region health dashboard: https://monitoring.resilienceai.io/primary
2. Verify DR region is healthy: https://monitoring.resilienceai.io/dr
3. Confirm issue is not isolated to single service

---

## Response

### Immediate Actions (0-5 minutes)

1. **Acknowledge Incident**
   ```bash
   # Acknowledge in PagerDuty
   pd incident:ack -i <incident_id>
   
   # Post in Slack
   /incident acknowledge <incident_id>
   ```

2. **Assess Impact**
   - Check affected services
   - Determine customer impact
   - Estimate severity (P1/P2/P3)

3. **Initiate Incident Bridge**
   - Join Zoom bridge: https://zoom.us/j/incident-bridge
   - Invite on-call team members
   - Assign Incident Commander

### Failover Execution (5-15 minutes)

1. **Update DNS (Route53)**
   ```bash
   # Switch traffic to DR region
   aws route53 change-resource-record-sets \
     --hosted-zone-id Z1234567890ABC \
     --change-batch file://dns-failover.json
   ```

2. **Promote DR Database**
   ```bash
   # Promote read replica to primary
   aws rds promote-read-replica \
     --db-instance-identifier resilienceai-dr-db \
     --region us-west-2
   
   # Wait for promotion
   aws rds wait db-instance-available \
     --db-instance-identifier resilienceai-dr-db \
     --region us-west-2
   ```

3. **Scale DR Infrastructure**
   ```bash
   # Scale EKS node groups
   aws eks update-nodegroup-config \
     --cluster-name resilienceai-dr \
     --nodegroup-name general \
     --scaling-config minSize=3,maxSize=20,desiredSize=5 \
     --region us-west-2
   ```

### Verification (15-20 minutes)

1. **Verify DNS Propagation**
   ```bash
   # Check DNS resolution
   dig api.resilienceai.io +short
   
   # Expected: Should resolve to DR ALB
   ```

2. **Verify Service Health**
   ```bash
   # Check health endpoints
   curl https://api.resilienceai.io/health
   curl https://api.resilienceai.io/health/ready
   curl https://api.resilienceai.io/health/deep
   ```

3. **Verify Database Connectivity**
   ```bash
   # Test database connection
   psql -h dr.db.resilienceai.io -U admin -d resilienceai -c "SELECT 1"
   ```

4. **Check Error Rates**
   - Monitor Datadog dashboard
   - Verify error rate < 1%
   - Check response times < 500ms

---

## Communication

### Internal
- Post updates in #incidents every 15 minutes
- Notify executives for P1 incidents
- Update status page

### External
- Update status.resilienceai.io
- Send customer notification if > 30 minutes
- Post on Twitter if > 1 hour

---

## Recovery

### Failback to Primary (when primary is restored)

1. **Verify Primary Health**
   ```bash
   # Check all services in primary
   ./scripts/verify-region-health.sh us-east-1
   ```

2. **Sync Data**
   ```bash
   # Ensure data consistency
   ./scripts/verify-data-sync.sh
   ```

3. **Execute Failback**
   ```bash
   # Switch DNS back to primary
   ./scripts/failback-to-primary.sh
   ```

4. **Verify Failback**
   - Monitor traffic distribution
   - Verify error rates
   - Confirm customer impact resolved

---

## Post-Incident

### Within 24 Hours
- [ ] Complete incident timeline
- [ ] Document root cause
- [ ] Calculate RTO/RPO achieved
- [ ] Identify improvement opportunities

### Within 48 Hours
- [ ] Schedule post-mortem meeting
- [ ] Draft post-mortem document
- [ ] Create follow-up action items

### Within 1 Week
- [ ] Complete post-mortem
- [ ] Update runbooks based on lessons learned
- [ ] Implement preventive measures

---

## Escalation

| Time | Action | Contact |
|------|--------|---------|
| 0 min | Acknowledge | On-call Engineer |
| 5 min | Escalate if not acknowledged | Engineering Manager |
| 15 min | Escalate if not resolved | CTO |
| 30 min | Executive notification | CEO |

---

## References

- DR Architecture Diagram
- Failover Controller Documentation
- Communication Plan
- Incident Response Framework

---

## Revision History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2024-01-15 | 1.0 | Initial version | Ops Team |
