# SentinelMine Troubleshooting Guide

This document provides guidance for diagnosing and resolving common issues that may be encountered in the SentinelMine platform.

## Table of Contents
- [General Troubleshooting Approach](#general-troubleshooting-approach)
- [Frontend Issues](#frontend-issues)
- [API Services](#api-services)
- [Authentication Problems](#authentication-problems)
- [Database Issues](#database-issues)
- [Machine Learning Services](#machine-learning-services)
- [Blockchain Component](#blockchain-component)
- [Kubernetes Cluster](#kubernetes-cluster)
- [Performance Problems](#performance-problems)
- [Network Issues](#network-issues)
- [Security Alerts](#security-alerts)
- [Common Error Codes](#common-error-codes)

## General Troubleshooting Approach

### Diagnostics Collection

When troubleshooting any issue, start by gathering relevant information:

```bash
# Collect system-wide diagnostics
./ops/scripts/collect-diagnostics.sh --scope system

# Check service status
kubectl get pods --all-namespaces | grep -v "Running\|Completed"

# Check recent events
kubectl get events --sort-by='.lastTimestamp'

# Review recent logs
./ops/scripts/aggregate-logs.sh --time "30m" --priority error
```

### Root Cause Analysis

Follow these steps to identify root causes:

1. **Identify affected components**:
   - Determine which services or components are experiencing issues
   - Check if the issue is isolated or system-wide

2. **Timeline analysis**:
   - Identify when the issue started
   - Correlate with recent changes or deployments

3. **Pattern recognition**:
   - Look for similar past incidents
   - Check if the issue occurs under specific conditions

4. **Impact assessment**:
   - Determine severity and user impact
   - Identify affected functionalities

## Frontend Issues

### Blank or Broken UI

**Symptoms:**
- Dashboard or pages not loading
- Blank screens
- JavaScript console errors

**Troubleshooting Steps:**

1. **Check browser console errors**:
   ```bash
   # Review frontend logs
   kubectl logs -n sentinelmine-frontend -l app=frontend --tail=100
   ```

2. **Verify API connectivity**:
   ```bash
   # Test API endpoints from frontend pod
   kubectl exec -it -n sentinelmine-frontend $(kubectl get pods -n sentinelmine-frontend -l app=frontend -o name | head -1) -- curl -s http://api-gateway.sentinelmine-api:8080/health
   ```

3. **Check for build issues**:
   ```bash
   # Verify build artifacts
   kubectl exec -it -n sentinelmine-frontend $(kubectl get pods -n sentinelmine-frontend -l app=frontend -o name | head -1) -- ls -la /usr/share/nginx/html
   ```

**Resolution:**

- If API connectivity fails, troubleshoot API services
- For build issues:
  ```bash
  # Rebuild and redeploy frontend
  ./ops/scripts/rebuild-frontend.sh
  ```
- For configuration issues:
  ```bash
  # Apply correct configuration
  kubectl apply -f ops/kubernetes/frontend-config.yaml
  ```

### Authentication UI Issues

**Symptoms:**
- Login form not working
- MFA screens not appearing
- Session expiration problems

**Troubleshooting Steps:**

1. **Check auth flow logs**:
   ```bash
   kubectl logs -n sentinelmine-frontend -l app=frontend --tail=100 | grep "auth"
   ```

2. **Test auth API endpoints**:
   ```bash
   kubectl exec -it -n sentinelmine-frontend $(kubectl get pods -n sentinelmine-frontend -l app=frontend -o name | head -1) -- curl -s http://auth-service.sentinelmine-api:8080/health
   ```

**Resolution:**

- Clear browser local storage and cookies
- Verify token handling in frontend code
- Check CORS configuration:
  ```bash
  kubectl get cm -n sentinelmine-api api-gateway-config -o yaml
  ```

## API Services

### API Service Not Responding

**Symptoms:**
- HTTP 503 errors
- API requests timing out
- Service unavailable in health checks

**Troubleshooting Steps:**

1. **Check pod status**:
   ```bash
   kubectl get pods -n sentinelmine-api
   kubectl describe pod -n sentinelmine-api $(kubectl get pods -n sentinelmine-api -l app=api-gateway -o name | head -1)
   ```

2. **Check resource utilization**:
   ```bash
   kubectl top pod -n sentinelmine-api
   ```

3. **Review logs for errors**:
   ```bash
   kubectl logs -n sentinelmine-api -l app=api-gateway --tail=100
   ```

**Resolution:**

- If pods are in CrashLoopBackOff:
  ```bash
  # Check for configuration issues
  kubectl get cm -n sentinelmine-api api-gateway-config -o yaml
  
  # Check for resource constraints
  kubectl describe pod -n sentinelmine-api $(kubectl get pods -n sentinelmine-api -l app=api-gateway -o name | head -1) | grep -A5 "Limits:"
  ```

- If resource utilization is high:
  ```bash
  # Scale up deployment
  kubectl scale deployment -n sentinelmine-api api-gateway --replicas=5
  ```

- If configuration is incorrect:
  ```bash
  # Apply correct configuration
  kubectl apply -f ops/kubernetes/api-gateway-config.yaml
  ```

### API Returns Errors

**Symptoms:**
- HTTP 4xx or 5xx status codes
- Unexpected API responses
- Error messages in API responses

**Troubleshooting Steps:**

1. **Check specific error codes**:
   ```bash
   kubectl logs -n sentinelmine-api -l app=api-gateway --tail=100 | grep "ERROR"
   kubectl logs -n sentinelmine-api -l app=prediction-api --tail=100 | grep "ERROR"
   ```

2. **Verify dependent services**:
   ```bash
   # Check database connectivity
   kubectl exec -it -n sentinelmine-api $(kubectl get pods -n sentinelmine-api -l app=api-gateway -o name | head -1) -- curl -s http://postgresql.sentinelmine-storage:5432 -v
   
   # Check ML service connectivity
   kubectl exec -it -n sentinelmine-api $(kubectl get pods -n sentinelmine-api -l app=prediction-api -o name | head -1) -- curl -s http://ml-service.sentinelmine-ml:8080/health
   ```

**Resolution:**

- For database connectivity issues:
  ```bash
  # Check database service and endpoints
  kubectl get svc -n sentinelmine-storage postgresql
  kubectl get endpoints -n sentinelmine-storage postgresql
  ```

- For dependent service issues:
  ```bash
  # Restart dependent services if needed
  kubectl rollout restart deployment -n sentinelmine-ml ml-service
  ```

- For configuration issues:
  ```bash
  # Apply correct configuration
  kubectl apply -f ops/kubernetes/prediction-api-config.yaml
  ```

## Authentication Problems

### Login Failures

**Symptoms:**
- Users unable to log in
- Authentication errors
- MFA issues

**Troubleshooting Steps:**

1. **Check auth service logs**:
   ```bash
   kubectl logs -n sentinelmine-api -l app=auth-service --tail=100 | grep "login"
   ```

2. **Verify database connectivity**:
   ```bash
   kubectl exec -it -n sentinelmine-api $(kubectl get pods -n sentinelmine-api -l app=auth-service -o name | head -1) -- curl -s postgresql.sentinelmine-storage:5432 -v
   ```

3. **Check MFA service**:
   ```bash
   kubectl logs -n sentinelmine-api -l app=mfa-service --tail=100
   ```

**Resolution:**

- If database connectivity issues:
  ```bash
  # Check database credentials
  kubectl get secret -n sentinelmine-api db-credentials -o jsonpath='{.data.password}' | base64 --decode
  
  # Verify database user permissions
  kubectl exec -it -n sentinelmine-storage postgres-0 -- psql -d sentinelmine_db -c "SELECT rolname, rolcanlogin FROM pg_roles;"
  ```

- If MFA issues:
  ```bash
  # Check MFA configuration
  kubectl get cm -n sentinelmine-api mfa-config -o yaml
  
  # Reset MFA for specific user (admin only)
  ./ops/scripts/reset-mfa.sh --username affected_user
  ```

### Token Validation Failures

**Symptoms:**
- "Invalid token" errors
- Premature session expiration
- Authentication required errors on protected endpoints

**Troubleshooting Steps:**

1. **Check JWT configuration**:
   ```bash
   kubectl get cm -n sentinelmine-api auth-config -o yaml | grep -A5 "jwt:"
   ```

2. **Verify clock synchronization**:
   ```bash
   kubectl exec -it -n sentinelmine-api $(kubectl get pods -n sentinelmine-api -l app=auth-service -o name | head -1) -- date
   kubectl exec -it -n sentinelmine-frontend $(kubectl get pods -n sentinelmine-frontend -l app=frontend -o name | head -1) -- date
   ```

**Resolution:**

- If JWT configuration issues:
  ```bash
  # Apply correct JWT configuration
  kubectl apply -f ops/kubernetes/auth-jwt-config.yaml
  ```

- If clock synchronization issues:
  ```bash
  # Sync clocks on nodes
  kubectl get nodes -o name | xargs -I{} kubectl debug {} -it --image=busybox -- ntpd -dnq
  ```

## Database Issues

### Database Connection Failures

**Symptoms:**
- "Could not connect to database" errors
- Connection timeout errors
- Connection pool exhaustion

**Troubleshooting Steps:**

1. **Check database pod status**:
   ```bash
   kubectl get pods -n sentinelmine-storage
   kubectl describe pod -n sentinelmine-storage postgres-0
   ```

2. **Verify connectivity**:
   ```bash
   kubectl exec -it -n sentinelmine-storage postgres-0 -- pg_isready
   ```

3. **Check connection count**:
   ```bash
   kubectl exec -it -n sentinelmine-storage postgres-0 -- psql -d sentinelmine_db -c "SELECT count(*) FROM pg_stat_activity;"
   ```

**Resolution:**

- If PostgreSQL is down:
  ```bash
  # Check PostgreSQL logs
  kubectl logs -n sentinelmine-storage postgres-0
  
  # If data corruption is suspected
  ./ops/scripts/db-restore.sh --latest-backup
  ```

- If connection pool exhaustion:
  ```bash
  # Increase connection pool size
  kubectl apply -f ops/kubernetes/db-connection-pool-config.yaml
  
  # Terminate idle connections
  kubectl exec -it -n sentinelmine-storage postgres-0 -- psql -d sentinelmine_db -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND state_change < NOW() - INTERVAL '1 hour';"
  ```

### Database Performance Issues

**Symptoms:**
- Slow query responses
- High database CPU/memory usage
- Transaction timeouts

**Troubleshooting Steps:**

1. **Identify slow queries**:
   ```bash
   kubectl exec -it -n sentinelmine-storage postgres-0 -- psql -d sentinelmine_db -c "SELECT query, calls, total_time, mean_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
   ```

2. **Check database resources**:
   ```bash
   kubectl top pod -n sentinelmine-storage postgres-0
   ```

3. **Analyze table statistics**:
   ```bash
   kubectl exec -it -n sentinelmine-storage postgres-0 -- psql -d sentinelmine_db -c "SELECT schemaname, relname, n_live_tup, n_dead_tup, last_vacuum, last_analyze FROM pg_stat_user_tables ORDER BY n_dead_tup DESC;"
   ```

**Resolution:**

- For slow queries:
  ```bash
  # Add indexes for common queries
  kubectl exec -it -n sentinelmine-storage postgres-0 -- psql -d sentinelmine_db -c "CREATE INDEX idx_predictions_created_at ON predictions(created_at);"
  
  # Analyze tables
  kubectl exec -it -n sentinelmine-storage postgres-0 -- psql -d sentinelmine_db -c "ANALYZE predictions;"
  ```

- For resource constraints:
  ```bash
  # Increase PostgreSQL resources
  kubectl apply -f ops/kubernetes/db-resources-high.yaml
  ```

- For maintenance needs:
  ```bash
  # Run VACUUM and ANALYZE
  kubectl exec -it -n sentinelmine-storage postgres-0 -- psql -d sentinelmine_db -c "VACUUM ANALYZE;"
  ```

## Machine Learning Services

### Model Prediction Failures

**Symptoms:**
- Prediction API returns errors
- Models fail to generate predictions
- Timeout errors from ML services

**Troubleshooting Steps:**

1. **Check ML service logs**:
   ```bash
   kubectl logs -n sentinelmine-ml -l app=model-server --tail=100
   ```

2. **Verify model availability**:
   ```bash
   kubectl exec -it -n sentinelmine-ml $(kubectl get pods -n sentinelmine-ml -l app=model-server -o name | head -1) -- ls -la /models/
   ```

3. **Check resource utilization**:
   ```bash
   kubectl top pod -n sentinelmine-ml
   ```

**Resolution:**

- If models are missing:
  ```bash
  # Restore models from backup
  ./ops/ml/restore-models.sh
  
  # Redeploy model server with correct models
  kubectl apply -f ops/kubernetes/model-server-config.yaml
  ```

- If resource constraints:
  ```bash
  # Increase resources for ML services
  kubectl apply -f ops/kubernetes/ml-resources-high.yaml
  ```

- If prediction service configuration issues:
  ```bash
  # Apply correct prediction service configuration
  kubectl apply -f ops/kubernetes/prediction-service-config.yaml
  ```

### Model Training Issues

**Symptoms:**
- Training jobs fail
- Model quality metrics decrease
- Training takes longer than expected

**Troubleshooting Steps:**

1. **Check training job logs**:
   ```bash
   kubectl logs -n sentinelmine-ml -l job-name=model-training-job
   ```

2. **Verify training data**:
   ```bash
   kubectl exec -it -n sentinelmine-ml $(kubectl get pods -n sentinelmine-ml -l app=data-prep -o name | head -1) -- ls -la /data/training/
   ```

3. **Check GPU availability**:
   ```bash
   kubectl exec -it -n sentinelmine-ml $(kubectl get pods -n sentinelmine-ml -l app=model-server -o name | head -1) -- nvidia-smi
   ```

**Resolution:**

- If training data issues:
  ```bash
  # Verify data integrity
  ./ops/ml/verify-training-data.sh --dataset recent_training_data
  
  # Regenerate training data if needed
  ./ops/ml/regenerate-training-data.sh
  ```

- If GPU issues:
  ```bash
  # Check GPU driver status
  kubectl exec -it -n sentinelmine-ml $(kubectl get pods -n sentinelmine-ml -l app=model-server -o name | head -1) -- nvidia-smi
  
  # Restart GPU driver if needed
  ./ops/scripts/restart-gpu-drivers.sh
  ```

## Blockchain Component

### Chaincode Invocation Failures

**Symptoms:**
- Chaincode operations fail
- "Endorsement failure" errors
- Timeout during blockchain operations

**Troubleshooting Steps:**

1. **Check peer logs**:
   ```bash
   kubectl logs -n sentinelmine-blockchain -l app=peer0-org1 --tail=100
   ```

2. **Verify chaincode status**:
   ```bash
   ./ops/blockchain/query-chaincode.sh --name audit-log --function "getStatus" --args ""
   ```

3. **Check peer status**:
   ```bash
   kubectl exec -it -n sentinelmine-blockchain $(kubectl get pods -n sentinelmine-blockchain -l app=peer0-org1 -o name | head -1) -- peer node status
   ```

**Resolution:**

- If chaincode issues:
  ```bash
  # Upgrade chaincode
  ./ops/blockchain/upgrade-chaincode.sh --name audit-log --version 1.2 --sequence 2
  
  # Verify chaincode installation
  ./ops/blockchain/list-installed-chaincode.sh
  ```

- If peer issues:
  ```bash
  # Restart peer
  kubectl rollout restart deployment -n sentinelmine-blockchain peer0-org1
  
  # Verify peer joined channels
  ./ops/blockchain/list-channels.sh
  ```

### Blockchain Network Synchronization Issues

**Symptoms:**
- Blocks not being committed
- Ledger height discrepancies between peers
- Consensus failures

**Troubleshooting Steps:**

1. **Check block heights across peers**:
   ```bash
   ./ops/blockchain/get-block-height.sh --channel auditchannel --peer peer0.org1
   ./ops/blockchain/get-block-height.sh --channel auditchannel --peer peer0.org2
   ```

2. **Verify orderer status**:
   ```bash
   kubectl logs -n sentinelmine-blockchain -l app=orderer0 --tail=100
   ```

3. **Check network connectivity**:
   ```bash
   kubectl exec -it -n sentinelmine-blockchain $(kubectl get pods -n sentinelmine-blockchain -l app=peer0-org1 -o name | head -1) -- ping -c 3 orderer0.sentinelmine-blockchain
   ```

**Resolution:**

- If orderer issues:
  ```bash
  # Restart orderer
  kubectl rollout restart deployment -n sentinelmine-blockchain orderer0
  
  # Check orderer configuration
  kubectl get cm -n sentinelmine-blockchain orderer-config -o yaml
  ```

- If peer synchronization issues:
  ```bash
  # Reset peer ledger (caution: use only if necessary)
  ./ops/blockchain/reset-peer.sh --peer peer0.org1
  
  # Rejoin channel
  ./ops/blockchain/join-channel.sh --channel auditchannel --peer peer0.org1
  ```

## Kubernetes Cluster

### Node Issues

**Symptoms:**
- Node status NotReady
- Pods stuck in Pending state
- Node resource exhaustion

**Troubleshooting Steps:**

1. **Check node status**:
   ```bash
   kubectl get nodes
   kubectl describe node PROBLEM_NODE
   ```

2. **Check node logs**:
   ```bash
   kubectl debug node/PROBLEM_NODE -it --image=ubuntu
   ```

3. **Check resource usage**:
   ```bash
   kubectl top node
   ```

**Resolution:**

- If node is NotReady:
  ```bash
  # Check kubelet status
  ssh admin@PROBLEM_NODE "sudo systemctl status kubelet"
  
  # Restart kubelet if needed
  ssh admin@PROBLEM_NODE "sudo systemctl restart kubelet"
  ```

- If node is resource constrained:
  ```bash
  # Drain node for maintenance
  kubectl drain PROBLEM_NODE --ignore-daemonsets
  
  # After maintenance, uncordon node
  kubectl uncordon PROBLEM_NODE
  ```

### Pod Scheduling Issues

**Symptoms:**
- Pods stuck in Pending state
- Insufficient resources errors
- Taint/Toleration conflicts

**Troubleshooting Steps:**

1. **Describe pending pods**:
   ```bash
   kubectl describe pod -n NAMESPACE PENDING_POD
   ```

2. **Check resource requests vs. availability**:
   ```bash
   kubectl describe nodes | grep -A5 "Allocated resources"
   ```

3. **Check for taints**:
   ```bash
   kubectl get nodes -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints
   ```

**Resolution:**

- If insufficient resources:
  ```bash
  # Adjust resource requests
  kubectl apply -f ops/kubernetes/resources-adjusted.yaml
  
  # Add more nodes if needed
  ./ops/scripts/add-worker-node.sh
  ```

- If taint issues:
  ```bash
  # Add appropriate tolerations to pod
  kubectl apply -f ops/kubernetes/tolerations-updated.yaml
  
  # Or remove taint if appropriate
  kubectl taint nodes PROBLEM_NODE key:effect-
  ```

## Performance Problems

### High CPU/Memory Usage

**Symptoms:**
- Node or pod CPU/memory at >90%
- Application slowness
- OOMKilled pods

**Troubleshooting Steps:**

1. **Identify resource usage**:
   ```bash
   kubectl top pods --all-namespaces | sort -k3 -nr | head -10
   kubectl top nodes
   ```

2. **Profile high-usage pods**:
   ```bash
   # For CPU issues
   kubectl exec -it -n NAMESPACE HIGH_CPU_POD -- ps aux --sort=-%cpu
   
   # For memory issues
   kubectl exec -it -n NAMESPACE HIGH_MEM_POD -- ps aux --sort=-%mem
   ```

**Resolution:**

- If pod resource constraints:
  ```bash
  # Increase resource limits
  kubectl apply -f ops/kubernetes/high-resources.yaml
  ```

- If memory leaks suspected:
  ```bash
  # Collect heap dumps for analysis
  ./ops/scripts/collect-heap-dump.sh --pod HIGH_MEM_POD --namespace NAMESPACE
  
  # Restart affected service
  kubectl rollout restart deployment -n NAMESPACE DEPLOYMENT_NAME
  ```

### Slow API Responses

**Symptoms:**
- High API latency
- Timeouts in client applications
- Slow dashboard loading

**Troubleshooting Steps:**

1. **Check API latency metrics**:
   ```bash
   # Query Prometheus for API latency
   ./ops/scripts/query-metrics.sh --metric "http_request_duration_seconds" --filter "service=api-gateway"
   ```

2. **Check dependent service latency**:
   ```bash
   # Query latency of database calls
   ./ops/scripts/query-metrics.sh --metric "database_query_duration_seconds" --filter "service=api-gateway"
   ```

3. **Check connection pooling**:
   ```bash
   kubectl get cm -n sentinelmine-api api-connection-pool -o yaml
   ```

**Resolution:**

- If database latency:
  ```bash
  # Optimize database queries
  kubectl apply -f ops/kubernetes/db-optimization-config.yaml
  ```

- If API service resource constraints:
  ```bash
  # Scale up API services
  kubectl scale deployment -n sentinelmine-api api-gateway --replicas=5
  ```

- If caching issues:
  ```bash
  # Configure or optimize Redis caching
  kubectl apply -f ops/kubernetes/redis-cache-config.yaml
  ```

## Network Issues

### Internal Service Communication Problems

**Symptoms:**
- Services unable to communicate
- Connection refused errors
- DNS resolution failures

**Troubleshooting Steps:**

1. **Test service connectivity**:
   ```bash
   kubectl exec -it -n sentinelmine-api $(kubectl get pods -n sentinelmine-api -l app=api-gateway -o name | head -1) -- curl -s http://prediction-api.sentinelmine-api:8080/health
   ```

2. **Check DNS resolution**:
   ```bash
   kubectl exec -it -n sentinelmine-api $(kubectl get pods -n sentinelmine-api -l app=api-gateway -o name | head -1) -- nslookup prediction-api.sentinelmine-api
   ```

3. **Verify service endpoints**:
   ```bash
   kubectl get endpoints -n sentinelmine-api prediction-api
   ```

**Resolution:**

- If DNS issues:
  ```bash
  # Check CoreDNS pods
  kubectl get pods -n kube-system -l k8s-app=kube-dns
  
  # Restart CoreDNS if needed
  kubectl rollout restart deployment -n kube-system coredns
  ```

- If service endpoint issues:
  ```bash
  # Verify service selector matches pod labels
  kubectl get svc -n sentinelmine-api prediction-api -o yaml
  kubectl get pods -n sentinelmine-api --show-labels | grep prediction-api
  ```

### External Connectivity Issues

**Symptoms:**
- External services unreachable
- Ingress controller errors
- SSL/TLS certificate errors

**Troubleshooting Steps:**

1. **Check ingress status**:
   ```bash
   kubectl get ingress --all-namespaces
   kubectl describe ingress -n sentinelmine-frontend frontend-ingress
   ```

2. **Verify TLS certificates**:
   ```bash
   kubectl get secret -n sentinelmine-frontend tls-cert -o yaml
   ```

3. **Check ingress controller logs**:
   ```bash
   kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx
   ```

**Resolution:**

- If certificate issues:
  ```bash
  # Renew certificates
  ./security/scripts/renew-certificates.sh
  
  # Apply new certificates
  kubectl apply -f security/tls/new-certificates.yaml
  ```

- If ingress controller issues:
  ```bash
  # Restart ingress controller
  kubectl rollout restart deployment -n ingress-nginx ingress-nginx-controller
  ```

## Security Alerts

### Suspicious Authentication Attempts

**Symptoms:**
- Multiple failed login attempts
- Logins from unusual locations
- Unusual access patterns

**Troubleshooting Steps:**

1. **Check authentication logs**:
   ```bash
   kubectl logs -n sentinelmine-api -l app=auth-service --since=24h | grep "Authentication failed" | sort | uniq -c
   ```

2. **Check source IP addresses**:
   ```bash
   kubectl logs -n sentinelmine-api -l app=auth-service --since=24h | grep "source_ip" | sort | uniq -c
   ```

**Resolution:**

- If brute force attacks suspected:
  ```bash
  # Enable rate limiting
  kubectl apply -f security/rate-limiting-strict.yaml
  
  # Block suspicious IPs
  ./security/scripts/block-ip.sh --ip SUSPICIOUS_IP
  ```

- If compromised account suspected:
  ```bash
  # Lock account
  ./ops/scripts/user-management.sh --action lock --username SUSPICIOUS_USER
  
  # Force password reset
  ./ops/scripts/user-management.sh --action reset-password --username SUSPICIOUS_USER
  ```

### Data Integrity Issues

**Symptoms:**
- Blockchain verification failures
- Data validation errors
- Unexpected data modifications

**Troubleshooting Steps:**

1. **Verify blockchain records**:
   ```bash
   ./ops/blockchain/verify-record.sh --id RECORD_ID
   ```

2. **Check audit logs**:
   ```bash
   kubectl logs -n sentinelmine-api -l app=audit-service --since=24h | grep RECORD_ID
   ```

3. **Compare database records with blockchain**:
   ```bash
   ./ops/scripts/compare-records.sh --id RECORD_ID
   ```

**Resolution:**

- If blockchain verification failures:
  ```bash
  # Investigate specific transaction
  ./ops/blockchain/get-transaction.sh --txid TRANSACTION_ID
  
  # Resubmit verification request
  ./ops/blockchain/submit-verification.sh --id RECORD_ID
  ```

- If data corruption:
  ```bash
  # Restore data from verified backup
  ./ops/scripts/restore-record.sh --id RECORD_ID
  
  # Generate audit report
  ./ops/scripts/generate-audit-report.sh --record RECORD_ID
  ```

## Common Error Codes

### Error Code Reference

| Error Code | Description | Troubleshooting |
|------------|-------------|-----------------|
| AUTH-001 | Invalid credentials | Check username/password, account lock status |
| AUTH-002 | MFA verification failed | Verify MFA configuration, check time synchronization |
| AUTH-003 | Token expired | Refresh token or log in again |
| API-001 | Missing required parameters | Check API request format |
| API-002 | Rate limit exceeded | Reduce request frequency or increase rate limits |
| API-003 | Insufficient permissions | Verify user role and permissions |
| DB-001 | Database connection failed | Check database service, credentials, network |
| DB-002 | Query timeout | Optimize query, check indexes, check database load |
| ML-001 | Model not found | Verify model deployment, check model path |
| ML-002 | Prediction error | Check input data format, model health |
| BC-001 | Chaincode invocation failed | Check chaincode status, peer availability |
| BC-002 | Blockchain consensus failed | Check orderer status, network connectivity |

### Resolving Common Errors

| Error | Resolution |
|-------|------------|
| AUTH-001 | `./ops/scripts/unlock-account.sh --username USER` |
| AUTH-002 | `./ops/scripts/reset-mfa.sh --username USER` |
| API-001 | Review API documentation and correct request format |
| DB-001 | `./ops/scripts/verify-db-connection.sh` |
| ML-001 | `./ops/ml/redeploy-model.sh --model MODEL_ID` |
| BC-001 | `./ops/blockchain/reinstall-chaincode.sh --name CHAINCODE_NAME` 