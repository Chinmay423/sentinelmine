# SentinelMine Infrastructure Setup Guide

This document provides detailed instructions for setting up the infrastructure required to deploy and operate the SentinelMine platform in various environments.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Air-Gapped Deployment](#air-gapped-deployment)
- [Hybrid Deployment](#hybrid-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Kubernetes Cluster Setup](#kubernetes-cluster-setup)
- [Database Configuration](#database-configuration)
- [Hyperledger Fabric Network Setup](#hyperledger-fabric-network-setup)
- [Load Balancer Configuration](#load-balancer-configuration)
- [Monitoring Stack Deployment](#monitoring-stack-deployment)
- [Backup Infrastructure](#backup-infrastructure)

## Prerequisites

### Hardware Requirements
- **Production Environment**:
  - Minimum 8 nodes for Kubernetes cluster (4 for control plane, 4 for worker nodes)
  - Each node: 16+ CPU cores, 64GB+ RAM, 500GB+ SSD storage
  - Network: 10Gbps interconnect minimum
  - Hardware Security Modules (HSMs) for cryptographic operations

- **Staging/Testing Environment**:
  - Minimum 4 nodes (2 for control plane, 2 for worker nodes)
  - Each node: 8+ CPU cores, 32GB+ RAM, 250GB+ SSD storage

### Software Requirements
- Ubuntu Server 20.04 LTS or RHEL 8.x for all nodes
- Kubernetes v1.24+ with containerd runtime
- Helm v3.8+
- PostgreSQL 14+
- Redis 6.2+
- Hyperledger Fabric v2.4+
- ELK Stack 8.x (Elasticsearch, Logstash, Kibana)
- Prometheus and Grafana for monitoring

### Network Requirements
- Isolated security zones with strict firewall rules
- Dedicated network segments for:
  - Frontend traffic
  - API traffic
  - Database traffic
  - Blockchain network
  - Management/monitoring traffic
- For air-gapped environments: Secure data diodes for one-way transfer

## Air-Gapped Deployment

Air-gapped deployments provide the highest level of security by physically isolating the production environment from external networks.

### Setup Process
1. **Prepare Offline Package Repository**:
   ```bash
   # On internet-connected system
   wget -r -np -R "index.html*" https://packages.sentinelmine.org/air-gapped-bundle/v1.0.0/
   
   # Transfer to air-gapped environment using approved media
   ```

2. **Configure Local Repository**:
   ```bash
   # On air-gapped system
   sudo mkdir -p /opt/sentinelmine/repo
   sudo cp -r packages.sentinelmine.org/air-gapped-bundle/v1.0.0/* /opt/sentinelmine/repo/
   
   # Create repository configuration
   cat <<EOF > /etc/apt/sources.list.d/sentinelmine-local.list
   deb [trusted=yes] file:/opt/sentinelmine/repo ./
   EOF
   
   sudo apt update
   ```

3. **Network Configuration**:
   - Implement physical network isolation
   - Configure data diodes for one-way data transfer if necessary
   - Establish strict access controls for maintenance

4. **Proceed with standard cluster setup** (see [Kubernetes Cluster Setup](#kubernetes-cluster-setup))

## Hybrid Deployment

Hybrid deployments maintain critical components in isolated environments while allowing selected components to interact with external systems.

### Setup Process
1. **Network Segmentation**:
   - Establish DMZ for external-facing components
   - Implement strict firewall rules between zones
   - Configure secure API gateways for cross-zone communication

2. **Component Distribution**:
   - Deploy sensitive ML models and data storage in isolated segments
   - Position API gateways and access control services in DMZ
   - Configure secure channels between segments

3. **Proceed with standard cluster setup** (see [Kubernetes Cluster Setup](#kubernetes-cluster-setup))

## Cloud Deployment

Cloud deployments leverage managed services while maintaining security through proper configuration.

### Setup Process
1. **Cloud Provider Setup**:
   ```bash
   # Example for AWS (use appropriate commands for other providers)
   aws cloudformation deploy \
     --template-file infrastructure/cloud/aws-template.yaml \
     --stack-name sentinelmine-infrastructure \
     --parameter-overrides Environment=production \
     --capabilities CAPABILITY_IAM
   ```

2. **Network Security**:
   - Implement Virtual Private Cloud (VPC) with private subnets
   - Configure Security Groups with minimum required access
   - Set up VPN or Direct Connect for secure administration

3. **Proceed with standard cluster setup** (see [Kubernetes Cluster Setup](#kubernetes-cluster-setup))

## Kubernetes Cluster Setup

### Initialize Kubernetes Cluster
```bash
# Initialize control plane
sudo kubeadm init --control-plane-endpoint="control.sentinelmine.local:6443" \
  --upload-certs \
  --pod-network-cidr=192.168.0.0/16 \
  --service-cidr=10.96.0.0/12

# Set up kubectl for admin user
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# Install Calico network plugin
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml

# Join worker nodes (command provided by kubeadm init output)
# sudo kubeadm join control.sentinelmine.local:6443 --token <token> --discovery-token-ca-cert-hash <hash>
```

### Deploy Core Infrastructure Components
```bash
# Create namespaces
kubectl create namespace sentinelmine-frontend
kubectl create namespace sentinelmine-api
kubectl create namespace sentinelmine-ml
kubectl create namespace sentinelmine-blockchain
kubectl create namespace sentinelmine-storage
kubectl create namespace sentinelmine-monitoring

# Deploy storage classes
kubectl apply -f infrastructure/kubernetes/storage-classes.yaml

# Apply network policies
kubectl apply -f infrastructure/kubernetes/network-policies.yaml

# Deploy secrets management
kubectl apply -f infrastructure/kubernetes/vault-config.yaml
```

## Database Configuration

### PostgreSQL Setup
```bash
# Create persistent volumes
kubectl apply -f infrastructure/storage/postgresql-pv.yaml

# Deploy PostgreSQL with encryption
helm install postgresql infrastructure/charts/postgresql \
  --namespace sentinelmine-storage \
  --values infrastructure/values/postgresql-values.yaml \
  --set postgresql.encryption.enabled=true \
  --set postgresql.audit.enabled=true
```

### Redis Cache Setup
```bash
# Deploy Redis with TLS
helm install redis infrastructure/charts/redis \
  --namespace sentinelmine-storage \
  --values infrastructure/values/redis-values.yaml \
  --set redis.tls.enabled=true
```

## Hyperledger Fabric Network Setup

```bash
# Generate crypto material
./infrastructure/blockchain/generate-crypto.sh

# Deploy Certificate Authority
kubectl apply -f infrastructure/blockchain/fabric-ca.yaml

# Deploy orderer nodes
kubectl apply -f infrastructure/blockchain/fabric-orderers.yaml

# Deploy peer nodes
kubectl apply -f infrastructure/blockchain/fabric-peers.yaml

# Create channels
./infrastructure/blockchain/create-channel.sh auditchannel
./infrastructure/blockchain/create-channel.sh predictionchannel

# Deploy chaincode
./infrastructure/blockchain/deploy-chaincode.sh audit-chaincode
./infrastructure/blockchain/deploy-chaincode.sh prediction-verification-chaincode
```

## Load Balancer Configuration

```bash
# Deploy Nginx Ingress Controller
helm install nginx-ingress infrastructure/charts/ingress-nginx \
  --namespace sentinelmine-frontend \
  --values infrastructure/values/ingress-values.yaml

# Configure TLS
kubectl apply -f infrastructure/tls/certificates.yaml

# Apply ingress rules
kubectl apply -f infrastructure/kubernetes/ingress-rules.yaml
```

## Monitoring Stack Deployment

```bash
# Deploy Prometheus and Grafana
helm install monitoring infrastructure/charts/kube-prometheus-stack \
  --namespace sentinelmine-monitoring \
  --values infrastructure/values/monitoring-values.yaml

# Deploy ELK Stack
helm install elasticsearch infrastructure/charts/elasticsearch \
  --namespace sentinelmine-monitoring \
  --values infrastructure/values/elasticsearch-values.yaml

helm install logstash infrastructure/charts/logstash \
  --namespace sentinelmine-monitoring \
  --values infrastructure/values/logstash-values.yaml

helm install kibana infrastructure/charts/kibana \
  --namespace sentinelmine-monitoring \
  --values infrastructure/values/kibana-values.yaml

# Configure log aggregation
kubectl apply -f infrastructure/monitoring/fluentd-config.yaml
```

## Backup Infrastructure

```bash
# Deploy Velero for Kubernetes backup
helm install velero infrastructure/charts/velero \
  --namespace sentinelmine-backup \
  --values infrastructure/values/velero-values.yaml

# Configure database backups
kubectl apply -f infrastructure/backup/postgresql-backup-job.yaml

# Configure blockchain state backup
kubectl apply -f infrastructure/backup/fabric-backup-job.yaml

# Set up backup schedules
kubectl apply -f infrastructure/backup/backup-schedules.yaml
```

## Post-Installation Verification

```bash
# Verify all pods are running
kubectl get pods --all-namespaces

# Run security compliance checks
./infrastructure/scripts/compliance-check.sh

# Verify high availability
./infrastructure/scripts/ha-test.sh

# Test backup and recovery
./infrastructure/scripts/backup-recovery-test.sh
```

## Additional Resources

- [System Architecture Documentation](./system_architecture.md)
- [Security Configuration Guide](./security_configuration.md)
- [Operational Procedures](./operational_procedures.md)
- [Troubleshooting Guide](./troubleshooting.md)