package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gorilla/mux"
	"github.com/hyperledger/fabric-sdk-go/pkg/core/config"
	"github.com/hyperledger/fabric-sdk-go/pkg/gateway"
)

// Configuration settings
type Config struct {
	Port             string `json:"port"`
	WalletPath       string `json:"walletPath"`
	ConnectionConfig string `json:"connectionConfigPath"`
	ChannelName      string `json:"channelName"`
	ChaincodeName    string `json:"chaincodeName"`
	OrgMSP           string `json:"orgMsp"`
	UserID           string `json:"userId"`
}

// Global variables
var (
	cfg      Config
	contract *gateway.Contract
)

func main() {
	// Initialize logger
	log.SetOutput(os.Stdout)
	log.SetFlags(log.LstdFlags | log.Lshortfile)
	log.Println("Starting SentinelMine Blockchain Service...")

	// Load configuration
	loadConfig()

	// Connect to the blockchain network
	if err := connectToNetwork(); err != nil {
		log.Fatalf("Failed to connect to the blockchain network: %v", err)
	}

	// Set up the HTTP server
	router := setupRouter()
	srv := &http.Server{
		Addr:         ":" + cfg.Port,
		Handler:      router,
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 15 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	// Start the server in a goroutine
	go func() {
		log.Printf("Server listening on port %s", cfg.Port)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Failed to start server: %v", err)
		}
	}()

	// Set up graceful shutdown
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	log.Println("Shutting down server...")

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	if err := srv.Shutdown(ctx); err != nil {
		log.Fatalf("Server forced to shutdown: %v", err)
	}

	log.Println("Server exited properly")
}

// Load configuration from environment variables or config file
func loadConfig() {
	cfg = Config{
		Port:             getEnv("PORT", "9443"),
		WalletPath:       getEnv("WALLET_PATH", "wallet"),
		ConnectionConfig: getEnv("CONNECTION_CONFIG", "config/connection.json"),
		ChannelName:      getEnv("CHANNEL_NAME", "operationschannel"),
		ChaincodeName:    getEnv("CHAINCODE_NAME", "securityops"),
		OrgMSP:           getEnv("ORG_MSP", "SentinelOrgMSP"),
		UserID:           getEnv("USER_ID", "admin"),
	}

	log.Printf("Configuration loaded: Port=%s, Channel=%s, Chaincode=%s", cfg.Port, cfg.ChannelName, cfg.ChaincodeName)
}

// Connect to the Hyperledger Fabric network
func connectToNetwork() error {
	log.Println("Connecting to blockchain network...")

	// The gRPC client connection should be shared by all Gateway connections to this endpoint
	wallet, err := gateway.NewFileSystemWallet(cfg.WalletPath)
	if err != nil {
		return fmt.Errorf("failed to create wallet: %w", err)
	}

	if !wallet.Exists(cfg.UserID) {
		return fmt.Errorf("identity %s not found in wallet", cfg.UserID)
	}

	ccpPath := cfg.ConnectionConfig
	gw, err := gateway.Connect(
		gateway.WithConfig(config.FromFile(ccpPath)),
		gateway.WithIdentity(wallet, cfg.UserID),
	)
	if err != nil {
		return fmt.Errorf("failed to connect to gateway: %w", err)
	}

	network, err := gw.GetNetwork(cfg.ChannelName)
	if err != nil {
		return fmt.Errorf("failed to get network: %w", err)
	}

	contract = network.GetContract(cfg.ChaincodeName)
	log.Println("Successfully connected to the blockchain network")
	return nil
}

// Set up the HTTP router
func setupRouter() *mux.Router {
	router := mux.NewRouter()

	// Health check route
	router.HandleFunc("/health", healthCheckHandler).Methods("GET")

	// API routes
	api := router.PathPrefix("/api").Subrouter()
	api.HandleFunc("/records", getAllRecordsHandler).Methods("GET")
	api.HandleFunc("/records/{id}", getRecordByIDHandler).Methods("GET")
	api.HandleFunc("/records", createRecordHandler).Methods("POST")
	api.HandleFunc("/verify/{id}", verifyRecordHandler).Methods("GET")

	// Middleware for logging
	router.Use(loggingMiddleware)

	return router
}

// Middleware for request logging
func loggingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		startTime := time.Now()
		next.ServeHTTP(w, r)
		log.Printf("%s %s %s", r.Method, r.RequestURI, time.Since(startTime))
	})
}

// API Handlers

// Health check handler
func healthCheckHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{
		"status":    "healthy",
		"timestamp": time.Now().Format(time.RFC3339),
	})
}

// Get all records handler
func getAllRecordsHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	// In a real implementation, we would query the blockchain
	// For this demo, we're returning mock data
	result := []map[string]interface{}{
		{
			"id":          "record001",
			"type":        "prediction",
			"timestamp":   time.Now().Add(-2 * time.Hour).Format(time.RFC3339),
			"hash":        "0x1234567890abcdef",
			"status":      "verified",
			"created_by":  "user-001",
			"data_digest": "sha256:1234567890abcdef",
		},
		{
			"id":          "record002",
			"type":        "threat_assessment",
			"timestamp":   time.Now().Add(-1 * time.Hour).Format(time.RFC3339),
			"hash":        "0xabcdef1234567890",
			"status":      "verified",
			"created_by":  "user-002",
			"data_digest": "sha256:abcdef1234567890",
		},
	}

	json.NewEncoder(w).Encode(map[string]interface{}{
		"records": result,
		"count":   len(result),
	})
}

// Get record by ID handler
func getRecordByIDHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	vars := mux.Vars(r)
	id := vars["id"]

	// Mock response - in a real implementation, we would query the blockchain
	record := map[string]interface{}{
		"id":          id,
		"type":        "prediction",
		"timestamp":   time.Now().Add(-2 * time.Hour).Format(time.RFC3339),
		"hash":        "0x1234567890abcdef",
		"status":      "verified",
		"created_by":  "user-001",
		"data_digest": "sha256:1234567890abcdef",
		"content": map[string]interface{}{
			"prediction_type": "threat_assessment",
			"confidence":      0.92,
			"result":          "High risk detected",
		},
	}

	json.NewEncoder(w).Encode(record)
}

// Create new record handler
func createRecordHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	var data map[string]interface{}
	if err := json.NewDecoder(r.Body).Decode(&data); err != nil {
		http.Error(w, "Invalid request payload", http.StatusBadRequest)
		return
	}

	// Generate mock transaction ID and timestamp
	txID := fmt.Sprintf("tx-%d", time.Now().UnixNano())
	timestamp := time.Now().Format(time.RFC3339)

	// Mock response - in a real implementation, we would submit to the blockchain
	response := map[string]interface{}{
		"transaction_id": txID,
		"timestamp":      timestamp,
		"status":         "success",
		"record_id":      fmt.Sprintf("record%d", time.Now().Unix()),
	}

	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(response)
}

// Verify record handler
func verifyRecordHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	vars := mux.Vars(r)
	id := vars["id"]

	// Mock verification response
	response := map[string]interface{}{
		"record_id":      id,
		"verified":       true,
		"timestamp":      time.Now().Format(time.RFC3339),
		"block_number":   12345,
		"transaction_id": "0xabcdef1234567890",
		"signature":      "304502207d7f95dc8f61466b1ebb7f4a0fff597a2304a2a2a42c0918b62b3ec20479f7f8022100b1643781a0bdb2a88f3c396e9bfca2377ca7b97d38d39f6b6a717e161604be4a",
	}

	json.NewEncoder(w).Encode(response)
}

// Helper function to get environment variable with default value
func getEnv(key, fallback string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return fallback
} 