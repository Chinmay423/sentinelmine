# SentinelMine CI/CD Pipeline

This document describes the continuous integration and continuous deployment (CI/CD) pipeline for the SentinelMine platform, including security controls, environments, and deployment procedures.

## Table of Contents
- [Pipeline Overview](#pipeline-overview)
- [Security Controls](#security-controls)
- [Pipeline Stages](#pipeline-stages)
- [Environments](#environments)
- [Configuration Management](#configuration-management)
- [Deployment Procedures](#deployment-procedures)
- [Rollback Procedures](#rollback-procedures)
- [Monitoring and Alerting](#monitoring-and-alerting)

## Pipeline Overview

The SentinelMine CI/CD pipeline follows security-first design principles to enable secure, automated delivery of code changes from development to production.

![CI/CD Pipeline Flow](assets/pipeline-flow.png)

### Key Principles

1. **Security-First**: Security gates at every stage of the pipeline
2. **Immutable Artifacts**: Build once, deploy to multiple environments
3. **Infrastructure as Code**: All infrastructure defined as code
4. **Reproducibility**: Consistent environments across the pipeline
5. **Audit Trail**: All changes tracked and logged for compliance

## Security Controls

### Code Security

- **Pre-commit Hooks**: Enforce code standards, prevent secrets in code
- **Code Signing**: All commits cryptographically signed
- **Branch Protection**: Protected branches require approvals
- **Secrets Management**: HashiCorp Vault for secure secrets storage

### Build Security

- **Trusted Images**: Use only approved base images
- **Dependency Scanning**: Check for known vulnerabilities
- **SAST**: Static Application Security Testing
- **SCA**: Software Composition Analysis

### Deployment Security

- **RBAC**: Role-based access control for all environments
- **Signed Artifacts**: Cryptographically signed deployment artifacts
- **Least Privilege**: Minimal permissions for deployment processes
- **Secure Configuration**: Secrets injected at runtime

## Pipeline Stages

### 1. Code Submission

```bash
# Developer workflow
git checkout -b feature/new-capability
# Make changes
git add .
git commit -S -m "Add new capability"
git push origin feature/new-capability
# Create pull request
```

### 2. Automated Validation

On pull request:

- Code style validation
- Unit tests
- SAST scans
- Dependency checks

```yaml
# Example validation job
validate:
  script:
    - ./scripts/lint.sh
    - ./scripts/unit-tests.sh
    - ./scripts/sast-scan.sh
    - ./scripts/dependency-check.sh
```

### 3. Build

After PR approval and merge:

- Build container images
- Sign artifacts
- Store in secure registry

```bash
# Example build commands
docker build -t sentinelmine-api:${VERSION} ./src/api
docker build -t sentinelmine-frontend:${VERSION} ./src/frontend
docker build -t sentinelmine-ml:${VERSION} ./src/ml

# Sign images
cosign sign --key ${SIGNING_KEY} sentinelmine-api:${VERSION}
cosign sign --key ${SIGNING_KEY} sentinelmine-frontend:${VERSION}
cosign sign --key ${SIGNING_KEY} sentinelmine-ml:${VERSION}

# Push to registry
docker push sentinelmine-api:${VERSION}
docker push sentinelmine-frontend:${VERSION}
docker push sentinelmine-ml:${VERSION}
```

### 4. Integration Testing

In dev environment:

- Deploy to integration testing environment
- Run integration tests
- Run contract tests
- Security dynamic analysis

```bash
# Deploy to integration environment
kubectl apply -f kubernetes/integration/

# Run integration tests
./scripts/integration-tests.sh

# Run contract tests
./scripts/contract-tests.sh

# Run DAST
./scripts/dast-scan.sh
```

### 5. Staging Deployment

In staging environment:

- Deploy to staging environment
- Run end-to-end tests
- Run performance tests
- Run security compliance checks

```bash
# Deploy to staging
kubectl apply -f kubernetes/staging/

# Run verification
./scripts/e2e-tests.sh
./scripts/performance-tests.sh
./scripts/compliance-check.sh
```

### 6. Approval for Production

Manual approval process:

- Security team approval
- Operations team approval
- Compliance verification

### 7. Production Deployment

Automated blue/green deployment to production:

```bash
# Deploy new version (green environment)
kubectl apply -f kubernetes/production/green/${VERSION}/

# Run smoke tests
./scripts/smoke-tests.sh

# Switch traffic to new version
kubectl apply -f kubernetes/production/traffic-switch.yaml

# Verify deployment
./scripts/verify-deployment.sh
```

## Environments

### Development Environment

- Purpose: Development and feature testing
- Access: Development team
- Configuration: `environments/dev`
- Resources: Minimal resource allocation
- Data: Synthetic test data

### Integration Environment

- Purpose: Integration testing
- Access: Development and QA teams
- Configuration: `environments/integration`
- Resources: Moderate resource allocation
- Data: Anonymized test data

### Staging Environment

- Purpose: Pre-production testing
- Access: QA, Operations, Security teams
- Configuration: `environments/staging`
- Resources: Production-like resources
- Data: Sanitized production-like data

### Production Environment

- Purpose: Live operations
- Access: Operations team only
- Configuration: `environments/production`
- Resources: Fully scaled production resources
- Data: Real production data

### Classified Environment

- Purpose: Classified operations
- Access: Cleared personnel only
- Configuration: Air-gapped systems
- Resources: Hardened infrastructure
- Data: Classified data

## Configuration Management

### Environment Configuration

All environment configuration is stored as code:

```
environments/
├── dev/
│   ├── config.yaml
│   ├── secrets.yaml.enc
│   └── values.yaml
├── integration/
│   ├── config.yaml
│   ├── secrets.yaml.enc
│   └── values.yaml
├── staging/
│   ├── config.yaml
│   ├── secrets.yaml.enc
│   └── values.yaml
└── production/
    ├── config.yaml
    ├── secrets.yaml.enc
    └── values.yaml
```

### Secrets Management

Secrets are managed using HashiCorp Vault:

```bash
# Store a secret
vault kv put secret/sentinelmine/production/api DB_PASSWORD=secure-password

# Retrieve a secret
vault kv get secret/sentinelmine/production/api

# Use in deployment
vault kv get -format=json secret/sentinelmine/production/api | \
  jq -r '.data.data.DB_PASSWORD' | \
  kubectl create secret generic api-secrets \
  --from-literal=DB_PASSWORD=- \
  --dry-run=client -o yaml | \
  kubectl apply -f -
```

## Deployment Procedures

### Regular Deployment

Regular deployments occur through the standard pipeline:

1. Code changes merged to main branch
2. CI/CD pipeline builds and tests
3. Deployment to staging and verification
4. Approval for production
5. Automated deployment to production

### Emergency Deployment

For critical fixes:

1. Create a hotfix branch from production tag
2. Implement fix and submit PR
3. Run expedited pipeline with critical tests
4. Emergency approval process
5. Deploy to production with extra monitoring

```bash
# Create hotfix branch
git checkout -b hotfix/critical-fix production-v1.2.3

# Apply fix, commit, and push
git add .
git commit -S -m "Fix critical issue"
git push origin hotfix/critical-fix

# Run expedited pipeline
./scripts/expedited-pipeline.sh --branch hotfix/critical-fix
```

### Classified Deployment

For classified environment:

1. Export deployment artifacts to secure media
2. Physical transport to air-gapped environment
3. Verification of artifact signatures
4. Manual deployment in classified environment
5. Verification of deployment

## Rollback Procedures

### Automated Rollback

If deployment verification fails:

```bash
# Automatic rollback to previous version
kubectl apply -f kubernetes/production/blue/${PREVIOUS_VERSION}/

# Switch traffic back to previous version
kubectl apply -f kubernetes/production/traffic-switch-rollback.yaml
```

### Manual Rollback

If issues are detected post-deployment:

```bash
# Get current deployment versions
kubectl get deployments -n sentinelmine -o wide

# Rollback specific service to previous version
kubectl rollout undo deployment/api-service -n sentinelmine

# Verify rollback
kubectl rollout status deployment/api-service -n sentinelmine
```

### Database Rollbacks

For database changes:

```bash
# Apply database rollback migration
./scripts/db-migrate.sh --rollback --version ${PREVIOUS_VERSION}

# Verify database state
./scripts/db-verify.sh
```

## Monitoring and Alerting

### Deployment Monitoring

- Real-time metrics during deployment
- Automatic canary analysis
- Error rate monitoring
- Performance baseline comparison

```bash
# Monitor deployment progress
./scripts/monitor-deployment.sh --version ${VERSION}
```

### Post-Deployment Verification

- Automated tests after deployment
- Security verification
- User experience monitoring
- Business metric validation

```bash
# Run post-deployment verification
./scripts/post-deploy-verify.sh --version ${VERSION}
```

### Alerting

Alert channels:

- Operations team chat
- On-call alerts
- Security team alerts
- Stakeholder notifications

```yaml
# Example alert configuration
alerts:
  deployment_failed:
    description: "Production deployment failed"
    severity: critical
    recipients:
      - ops-team
      - security-team
      - stakeholders
  rollback_initiated:
    description: "Automatic rollback initiated"
    severity: critical
    recipients:
      - ops-team
      - security-team
      - stakeholders
``` 