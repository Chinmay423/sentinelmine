FROM golang:1.20-buster AS builder

WORKDIR /app

# Install Hyperledger Fabric dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Hyperledger Fabric CLI
RUN curl -sSL https://raw.githubusercontent.com/hyperledger/fabric/main/scripts/install-fabric.sh | bash -s -- binary

# Copy source code
COPY . .

# Build the application
RUN go mod download
RUN go build -o /sentinel-blockchain-service ./cmd/main.go

# Create a minimal production image
FROM debian:bullseye-slim

# Install SSL certificates and other dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the binary from the builder stage
COPY --from=builder /sentinel-blockchain-service .
COPY --from=builder /app/config ./config
COPY --from=builder /app/chaincode ./chaincode

# Set up environment variables
ENV FABRIC_CFG_PATH=/app/config
ENV PATH=$PATH:/app

# Create a non-root user
RUN useradd -m -r chainuser && chown -R chainuser:chainuser /app
USER chainuser

# Expose the necessary ports
EXPOSE 7050 7051 9443

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:9443/health || exit 1

# Start the service
CMD ["/app/sentinel-blockchain-service"] 