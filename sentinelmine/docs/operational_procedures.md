# SentinelMine Operational Procedures

This document outlines the standard operational procedures for maintaining, monitoring, and supporting the SentinelMine platform in production environments.

## Table of Contents
- [Routine Operations](#routine-operations)
- [Monitoring Procedures](#monitoring-procedures)
- [Maintenance Tasks](#maintenance-tasks)
- [Backup and Recovery](#backup-and-recovery)
- [Scaling Procedures](#scaling-procedures)
- [Security Operations](#security-operations)
- [Model Management](#model-management)
- [Blockchain Operations](#blockchain-operations)
- [Performance Tuning](#performance-tuning)
- [Incident Management](#incident-management)

## Routine Operations

### Daily Tasks

#### System Health Check
```bash
# Check overall system health
./ops/scripts/health-check.sh

# Verify all services are running
kubectl get pods --all-namespaces | grep -v "Running\|Completed"

# Check resource utilization
kubectl top nodes
kubectl top pods --all-namespaces
```

#### Log Review
```bash
# Aggregate important logs
./ops/scripts/log-summary.sh --priority high

# Check for authentication failures
kubectl logs -n sentinelmine-api -l app=auth-service --since=24h | grep "Authentication failed" | wc -l

# Review prediction service errors
kubectl logs -n sentinelmine-ml -l app=prediction-service --since=24h | grep "ERROR" > /tmp/prediction-errors.log
```

#### Security Scan
```bash
# Run daily security scan
./ops/scripts/security-scan.sh --scope daily
```

### Weekly Tasks

#### Performance Review
```bash
# Generate weekly performance report
./ops/scripts/generate-performance-report.sh --period weekly

# Review API response times
./ops/scripts/api-performance.sh --last-week
```

#### Database Maintenance
```bash
# Run database optimization
kubectl exec -n sentinelmine-storage postgres-0 -- pg_repack -d sentinelmine_db -t predictions
```

#### Storage Cleanup
```bash
# Clean up temporary storage
./ops/scripts/cleanup-temp.sh

# Archive old data
./ops/scripts/archive-data.sh --older-than 90d
```

## Monitoring Procedures

### Alert Handling

1. **Critical Alerts**:
   - Acknowledge alert in monitoring system
   - Notify on-call engineer via dedicated channel
   - Begin remediation within 15 minutes
   - Document incident and resolution

2. **High Priority Alerts**:
   - Acknowledge alert in monitoring system
   - Begin remediation within 1 hour
   - Document actions taken in operations log

3. **Medium Priority Alerts**:
   - Acknowledge alert in monitoring system
   - Schedule remediation within 24 hours
   - Update ticket with planned resolution

### Dashboard Review

#### System Dashboard
- Review CPU, memory, and disk usage trends
- Check network traffic patterns
- Identify resource bottlenecks
- Verify cluster node health

#### Application Dashboard
- Monitor active users and sessions
- Review API request rates and latencies
- Check error rates across services
- Verify prediction model performance

#### Security Dashboard
- Review authentication activity
- Monitor access control events
- Check for unusual patterns
- Verify integrity verification status

## Maintenance Tasks

### Scheduled Maintenance

1. **Prepare Maintenance Window**:
   ```bash
   # Create maintenance announcement
   ./ops/scripts/announce-maintenance.sh --window "2023-11-15T22:00:00Z/2023-11-16T02:00:00Z" \
     --services "API, ML Models" \
     --impact "Brief service interruption" \
     --notification-channels "email,dashboard"
   
   # Enable maintenance mode
   kubectl apply -f ops/kubernetes/maintenance-mode.yaml
   ```

2. **Perform Updates**:
   ```bash
   # Update application components
   helm upgrade frontend infrastructure/charts/frontend \
     --namespace sentinelmine-frontend \
     --values ops/values/frontend-values.yaml
   
   # Update API services
   helm upgrade api infrastructure/charts/api \
     --namespace sentinelmine-api \
     --values ops/values/api-values.yaml
   ```

3. **Validate Updates**:
   ```bash
   # Run post-update tests
   ./ops/scripts/post-update-tests.sh
   
   # Verify services are running
   kubectl get pods --all-namespaces | grep -v "Running\|Completed"
   ```

4. **Complete Maintenance**:
   ```bash
   # Disable maintenance mode
   kubectl delete -f ops/kubernetes/maintenance-mode.yaml
   
   # Send completion notification
   ./ops/scripts/announce-maintenance-complete.sh
   ```

### Certificate Rotation

1. **Prepare New Certificates**:
   ```bash
   # Generate new certificates
   ./security/scripts/generate-certs.sh \
     --key-size 4096 \
     --hash-algorithm sha384 \
     --validity 365 \
     --domains "api.sentinelmine.org,dashboard.sentinelmine.org"
   ```

2. **Deploy New Certificates**:
   ```bash
   # Update certificate secrets
   kubectl apply -f security/tls/new-certificates.yaml
   
   # Reload affected services
   kubectl rollout restart deployment -n sentinelmine-api api-gateway
   kubectl rollout restart deployment -n sentinelmine-frontend frontend
   ```

3. **Verify Certificate Deployment**:
   ```bash
   # Check certificate expiration dates
   ./ops/scripts/verify-certificates.sh
   ```

## Backup and Recovery

### Scheduled Backups

1. **Database Backups**:
   ```bash
   # Run full database backup
   ./ops/scripts/db-backup.sh --type full
   
   # Verify backup integrity
   ./ops/scripts/verify-backup.sh --latest
   
   # Upload to secure storage
   ./ops/scripts/archive-backup.sh --encryption enabled
   ```

2. **Configuration Backups**:
   ```bash
   # Backup Kubernetes configurations
   kubectl get all --all-namespaces -o yaml > /backup/kubernetes-state-$(date +%Y%m%d).yaml
   
   # Backup secrets and configmaps
   ./ops/scripts/backup-configs.sh
   ```

3. **Blockchain State Backup**:
   ```bash
   # Backup blockchain state
   ./ops/blockchain/backup-ledger.sh
   ```

### Recovery Procedures

#### Database Recovery
```bash
# Stop affected services
kubectl scale deployment -n sentinelmine-api prediction-api --replicas=0

# Restore database from backup
./ops/scripts/db-restore.sh --backup-id BACKUP_ID

# Verify data integrity
./ops/scripts/db-verify.sh

# Restart services
kubectl scale deployment -n sentinelmine-api prediction-api --replicas=3
```

#### Complete System Recovery
```bash
# Deploy infrastructure
terraform apply -var-file=environments/production.tfvars

# Restore core Kubernetes components
kubectl apply -f /backup/kubernetes-state.yaml

# Restore data from backups
./ops/scripts/restore-all.sh --environment production
```

## Scaling Procedures

### Horizontal Scaling

1. **Scale API Tier**:
   ```bash
   # Scale API deployments
   kubectl scale deployment -n sentinelmine-api auth-api --replicas=5
   kubectl scale deployment -n sentinelmine-api prediction-api --replicas=5
   
   # Verify scaling operation
   kubectl get pods -n sentinelmine-api
   ```

2. **Scale ML Services**:
   ```bash
   # Scale ML model servers
   kubectl scale deployment -n sentinelmine-ml model-server --replicas=3
   
   # Verify GPU allocation
   kubectl describe nodes | grep -A5 "Allocated resources"
   ```

### Vertical Scaling

1. **Update Resource Requests/Limits**:
   ```bash
   # Apply new resource configuration
   kubectl apply -f ops/kubernetes/resources/high-capacity.yaml
   
   # Monitor for resource allocation
   kubectl top pods -n sentinelmine-api
   ```

2. **Database Scaling**:
   ```bash
   # Scale PostgreSQL resources
   helm upgrade postgresql infrastructure/charts/postgresql \
     --namespace sentinelmine-storage \
     --set resources.requests.cpu=4 \
     --set resources.requests.memory=16Gi
   ```

## Security Operations

### Access Control Management

1. **User Provisioning**:
   ```bash
   # Add new user
   ./ops/scripts/user-management.sh --action create \
     --username jdoe \
     --role analyst \
     --email "jdoe@sentinelmine.org" \
     --mfa required
   
   # Set up temporary credentials
   ./ops/scripts/generate-temp-credentials.sh --username jdoe
   ```

2. **Access Review**:
   ```bash
   # Generate access report
   ./ops/scripts/access-report.sh --full
   
   # Identify inactive users
   ./ops/scripts/inactive-users.sh --days 90
   ```

3. **Role Modifications**:
   ```bash
   # Update user role
   ./ops/scripts/user-management.sh --action update \
     --username jdoe \
     --role senior-analyst
   ```

### Security Patching

1. **Vulnerability Assessment**:
   ```bash
   # Scan for vulnerabilities
   ./ops/scripts/vulnerability-scan.sh --scope full
   
   # Generate remediation plan
   ./ops/scripts/generate-patch-plan.sh
   ```

2. **Apply Security Patches**:
   ```bash
   # Apply critical patches
   ./ops/scripts/apply-patches.sh --priority critical
   
   # Verify patch application
   ./ops/scripts/verify-patches.sh --latest
   ```

## Model Management

### Model Deployment

1. **Test Model Performance**:
   ```bash
   # Evaluate model performance
   ./ops/ml/evaluate-model.sh --model-id threat-classification-v2 \
     --test-dataset validation_dataset_2023Q4
   
   # Compare with currently deployed model
   ./ops/ml/compare-models.sh --model-a threat-classification-v1 \
     --model-b threat-classification-v2
   ```

2. **Deploy New Model**:
   ```bash
   # Deploy model to staging
   ./ops/ml/deploy-model.sh --model-id threat-classification-v2 \
     --environment staging
   
   # Validate model behavior
   ./ops/ml/validate-deployed-model.sh --model-id threat-classification-v2 \
     --environment staging
   
   # Promote to production
   ./ops/ml/promote-model.sh --model-id threat-classification-v2 \
     --from-env staging \
     --to-env production
   ```

3. **Monitor Model Performance**:
   ```bash
   # Set up performance monitoring
   kubectl apply -f ops/kubernetes/model-monitoring.yaml
   
   # Configure alerts for performance degradation
   kubectl apply -f ops/kubernetes/model-alerts.yaml
   ```

### Model Retraining

1. **Prepare Training Data**:
   ```bash
   # Extract and prepare new training data
   ./ops/ml/extract-training-data.sh --time-period "last-quarter" \
     --output-dataset training_dataset_2023Q4
   
   # Validate dataset
   ./ops/ml/validate-dataset.sh --dataset training_dataset_2023Q4
   ```

2. **Initiate Training Job**:
   ```bash
   # Start training job
   ./ops/ml/start-training.sh --model-type threat-classification \
     --dataset training_dataset_2023Q4 \
     --hyperparams ops/ml/configs/threat-classification-hyper.yaml
   ```

3. **Review and Register Model**:
   ```bash
   # Review training results
   ./ops/ml/review-training.sh --job-id JOB_ID
   
   # Register new model version
   ./ops/ml/register-model.sh --job-id JOB_ID --version v3
   ```

## Blockchain Operations

### Chaincode Management

1. **Deploy New Chaincode**:
   ```bash
   # Package chaincode
   ./ops/blockchain/package-chaincode.sh --name audit-log --version 1.2
   
   # Install on peers
   ./ops/blockchain/install-chaincode.sh --package audit-log-1.2.tar.gz
   
   # Approve and commit chaincode
   ./ops/blockchain/approve-chaincode.sh --name audit-log --version 1.2 \
     --sequence 2 --policy "OR('OrgMSP.member')"
   ```

2. **Upgrade Existing Chaincode**:
   ```bash
   # Upgrade chaincode
   ./ops/blockchain/upgrade-chaincode.sh --name verification --version 2.0 \
     --sequence 3
   
   # Verify upgrade
   ./ops/blockchain/query-chaincode.sh --name verification \
     --function "getVersion" --args ""
   ```

### Channel Management

1. **Create New Channel**:
   ```bash
   # Generate channel configuration
   ./ops/blockchain/generate-channel-tx.sh --channel new-verification-channel \
     --orgs "org1,org2"
   
   # Create channel
   ./ops/blockchain/create-channel.sh --channel new-verification-channel
   
   # Join peers to channel
   ./ops/blockchain/join-channel.sh --channel new-verification-channel \
     --peers "peer0.org1,peer0.org2"
   ```

2. **Update Channel Configuration**:
   ```bash
   # Fetch current config
   ./ops/blockchain/fetch-channel-config.sh --channel audit-channel
   
   # Modify configuration
   ./ops/blockchain/modify-channel-config.sh --config config.json \
     --update "BatchTimeout:2s"
   
   # Sign and update channel
   ./ops/blockchain/update-channel.sh --channel audit-channel \
     --config modified_config.json
   ```

## Performance Tuning

### Database Optimization

1. **Analyze Query Performance**:
   ```bash
   # Identify slow queries
   kubectl exec -n sentinelmine-storage postgres-0 -- psql -d sentinelmine_db \
     -c "SELECT query, calls, total_time, mean_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
   
   # Explain problematic queries
   kubectl exec -n sentinelmine-storage postgres-0 -- psql -d sentinelmine_db \
     -c "EXPLAIN ANALYZE SELECT * FROM predictions WHERE created_at > NOW() - INTERVAL '7 days';"
   ```

2. **Create Indexes**:
   ```bash
   # Add indexes for common queries
   kubectl exec -n sentinelmine-storage postgres-0 -- psql -d sentinelmine_db \
     -c "CREATE INDEX idx_predictions_created_at ON predictions(created_at);"
   
   # Verify index usage
   kubectl exec -n sentinelmine-storage postgres-0 -- psql -d sentinelmine_db \
     -c "SELECT indexrelname, idx_scan FROM pg_stat_user_indexes WHERE indexrelname = 'idx_predictions_created_at';"
   ```

3. **Configure Database Parameters**:
   ```bash
   # Apply optimized PostgreSQL settings
   kubectl apply -f ops/storage/postgresql-performance.yaml
   
   # Reload configuration
   kubectl exec -n sentinelmine-storage postgres-0 -- pg_ctl reload
   ```

### API Optimization

1. **Enable Caching**:
   ```bash
   # Configure Redis caching
   kubectl apply -f ops/kubernetes/redis-cache-config.yaml
   
   # Verify cache hit rate
   ./ops/scripts/cache-stats.sh
   ```

2. **Optimize Connection Pooling**:
   ```bash
   # Configure connection pools
   kubectl apply -f ops/kubernetes/connection-pool-config.yaml
   
   # Monitor connection usage
   ./ops/scripts/monitor-connections.sh
   ```

## Incident Management

### Handling Service Disruptions

1. **Incident Detection**:
   ```bash
   # Verify alert accuracy
   ./ops/scripts/verify-alert.sh --alert-id ALERT_ID
   
   # Check affected components
   ./ops/scripts/check-components.sh --service prediction-api
   ```

2. **Initial Response**:
   ```bash
   # Create incident record
   ./ops/scripts/create-incident.sh \
     --severity high \
     --service "prediction-api" \
     --description "Service returning 500 errors"
   
   # Notify incident team
   ./ops/scripts/notify-team.sh --incident-id INC123
   ```

3. **Triage and Resolution**:
   ```bash
   # Collect diagnostic information
   ./ops/scripts/collect-diagnostics.sh --service prediction-api
   
   # Apply temporary fix
   kubectl rollout restart deployment -n sentinelmine-api prediction-api
   
   # Verify service recovery
   ./ops/scripts/verify-service.sh --service prediction-api
   ```

4. **Post-Incident Activities**:
   ```bash
   # Document resolution
   ./ops/scripts/update-incident.sh --incident-id INC123 \
     --status resolved \
     --resolution "Restarted service due to memory leak"
   
   # Schedule post-mortem
   ./ops/scripts/schedule-postmortem.sh --incident-id INC123
   
   # Create preventive action item
   ./ops/scripts/create-action-item.sh \
     --title "Fix memory leak in prediction service" \
     --assignee "engineering-team" \
     --due-date "2023-11-30"
   ```

### Disaster Recovery Activation

1. **Declare Disaster Scenario**:
   ```bash
   # Activate disaster recovery plan
   ./ops/dr/activate-dr.sh --scenario "primary-datacenter-outage"
   
   # Notify stakeholders
   ./ops/dr/notify-dr-activation.sh
   ```

2. **Failover Procedures**:
   ```bash
   # Failover to secondary region
   ./ops/dr/failover.sh --target-region secondary
   
   # Verify services in secondary region
   ./ops/dr/verify-services.sh --region secondary
   ```

3. **Return to Normal Operations**:
   ```bash
   # Assess primary region status
   ./ops/dr/assess-primary.sh
   
   # Sync data from secondary to primary
   ./ops/dr/sync-data.sh --from secondary --to primary
   
   # Failback to primary region
   ./ops/dr/failback.sh --target-region primary
   
   # Verify complete recovery
   ./ops/dr/verify-recovery.sh
   ```

## Appendix: Reference Commands

### Common Troubleshooting Commands

```bash
# Check pod logs
kubectl logs -n NAMESPACE POD_NAME

# Describe resources
kubectl describe pod -n NAMESPACE POD_NAME
kubectl describe svc -n NAMESPACE SERVICE_NAME

# Port-forward to service for direct testing
kubectl port-forward -n NAMESPACE svc/SERVICE_NAME LOCAL_PORT:SERVICE_PORT

# Check resource utilization
kubectl top pod -n NAMESPACE POD_NAME
kubectl top node NODE_NAME

# Exec into container
kubectl exec -it -n NAMESPACE POD_NAME -- /bin/bash

# View events
kubectl get events -n NAMESPACE --sort-by='.lastTimestamp'
```

### Configuration Management

```bash
# View configmaps
kubectl get configmap -n NAMESPACE CONFIG_NAME -o yaml

# Update configmap
kubectl edit configmap -n NAMESPACE CONFIG_NAME

# View secrets (safely)
kubectl get secret -n NAMESPACE SECRET_NAME -o jsonpath='{.data}' | 
  jq 'map_values(@base64d)'

# Create secret
kubectl create secret generic -n NAMESPACE SECRET_NAME \
  --from-literal=key1=value1 \
  --from-literal=key2=value2
``` 