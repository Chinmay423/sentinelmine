package main

import (
	"encoding/json"
	"fmt"
	"time"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

// SecurityOpsContract provides functions for managing security predictions and verifications
type SecurityOpsContract struct {
	contractapi.Contract
}

// SecurityRecord represents a security prediction or assessment record
type SecurityRecord struct {
	ID            string                 `json:"id"`
	Type          string                 `json:"type"`
	CreatedAt     string                 `json:"created_at"`
	CreatedBy     string                 `json:"created_by"`
	Content       map[string]interface{} `json:"content"`
	Hash          string                 `json:"hash"`
	PreviousHash  string                 `json:"previous_hash"`
	Status        string                 `json:"status"`
	Verification  *Verification          `json:"verification,omitempty"`
	AuditHistory  []AuditEntry           `json:"audit_history,omitempty"`
	Classification string                 `json:"classification"`
	Department    string                 `json:"department"`
}

// Verification represents verification details of a record
type Verification struct {
	VerifiedAt   string `json:"verified_at"`
	VerifiedBy   string `json:"verified_by"`
	Status       string `json:"status"`
	BlockNumber  uint64 `json:"block_number"`
	TransactionID string `json:"transaction_id"`
}

// AuditEntry represents an audit log entry
type AuditEntry struct {
	Timestamp string `json:"timestamp"`
	UserID    string `json:"user_id"`
	Action    string `json:"action"`
	Details   string `json:"details"`
}

// InitLedger initializes the ledger with sample data
func (s *SecurityOpsContract) InitLedger(ctx contractapi.TransactionContextInterface) error {
	// Sample records
	records := []SecurityRecord{
		{
			ID:            "record001",
			Type:          "threat_assessment",
			CreatedAt:     time.Now().Format(time.RFC3339),
			CreatedBy:     "system",
			Content:       map[string]interface{}{"threat_level": "medium", "confidence": 0.82},
			Hash:          "0x1234567890abcdef",
			PreviousHash:  "",
			Status:        "verified",
			Classification: "confidential",
			Department:    "intelligence",
			AuditHistory:  []AuditEntry{},
		},
	}

	for _, record := range records {
		recordJSON, err := json.Marshal(record)
		if err != nil {
			return fmt.Errorf("failed to marshal record: %v", err)
		}

		err = ctx.GetStub().PutState(record.ID, recordJSON)
		if err != nil {
			return fmt.Errorf("failed to put record %s to world state: %v", record.ID, err)
		}
	}

	return nil
}

// CreateRecord creates a new security record on the ledger
func (s *SecurityOpsContract) CreateRecord(ctx contractapi.TransactionContextInterface, id string, recordType string, createdBy string, content string, hash string, classification string, department string) error {
	// Check if record already exists
	exists, err := s.RecordExists(ctx, id)
	if err != nil {
		return err
	}
	if exists {
		return fmt.Errorf("record %s already exists", id)
	}

	// Parse content from JSON string
	var contentMap map[string]interface{}
	err = json.Unmarshal([]byte(content), &contentMap)
	if err != nil {
		return fmt.Errorf("failed to parse content JSON: %v", err)
	}

	// Create new record
	record := SecurityRecord{
		ID:            id,
		Type:          recordType,
		CreatedAt:     time.Now().Format(time.RFC3339),
		CreatedBy:     createdBy,
		Content:       contentMap,
		Hash:          hash,
		PreviousHash:  "",
		Status:        "created",
		Classification: classification,
		Department:    department,
		AuditHistory: []AuditEntry{
			{
				Timestamp: time.Now().Format(time.RFC3339),
				UserID:    createdBy,
				Action:    "create",
				Details:   "Record created",
			},
		},
	}

	recordJSON, err := json.Marshal(record)
	if err != nil {
		return fmt.Errorf("failed to marshal record: %v", err)
	}

	return ctx.GetStub().PutState(id, recordJSON)
}

// VerifyRecord updates a record with verification information
func (s *SecurityOpsContract) VerifyRecord(ctx contractapi.TransactionContextInterface, id string, verifiedBy string) error {
	record, err := s.GetRecord(ctx, id)
	if err != nil {
		return err
	}

	// Update verification information
	txID := ctx.GetStub().GetTxID()
	
	verification := Verification{
		VerifiedAt:    time.Now().Format(time.RFC3339),
		VerifiedBy:    verifiedBy,
		Status:        "verified",
		TransactionID: txID,
		BlockNumber:   0, // In a real implementation, we would get this from the blockchain
	}

	record.Status = "verified"
	record.Verification = &verification
	record.AuditHistory = append(record.AuditHistory, AuditEntry{
		Timestamp: time.Now().Format(time.RFC3339),
		UserID:    verifiedBy,
		Action:    "verify",
		Details:   "Record verified",
	})

	recordJSON, err := json.Marshal(record)
	if err != nil {
		return fmt.Errorf("failed to marshal record: %v", err)
	}

	return ctx.GetStub().PutState(id, recordJSON)
}

// GetRecord retrieves a record by ID
func (s *SecurityOpsContract) GetRecord(ctx contractapi.TransactionContextInterface, id string) (*SecurityRecord, error) {
	recordJSON, err := ctx.GetStub().GetState(id)
	if err != nil {
		return nil, fmt.Errorf("failed to read record %s from world state: %v", id, err)
	}
	if recordJSON == nil {
		return nil, fmt.Errorf("record %s does not exist", id)
	}

	var record SecurityRecord
	err = json.Unmarshal(recordJSON, &record)
	if err != nil {
		return nil, fmt.Errorf("failed to unmarshal record JSON: %v", err)
	}

	return &record, nil
}

// GetAllRecords returns all records in the world state
func (s *SecurityOpsContract) GetAllRecords(ctx contractapi.TransactionContextInterface) ([]*SecurityRecord, error) {
	resultsIterator, err := ctx.GetStub().GetStateByRange("", "")
	if err != nil {
		return nil, fmt.Errorf("failed to get records: %v", err)
	}
	defer resultsIterator.Close()

	var records []*SecurityRecord
	for resultsIterator.HasNext() {
		queryResponse, err := resultsIterator.Next()
		if err != nil {
			return nil, fmt.Errorf("failed to get next record: %v", err)
		}

		var record SecurityRecord
		err = json.Unmarshal(queryResponse.Value, &record)
		if err != nil {
			return nil, fmt.Errorf("failed to unmarshal record: %v", err)
		}
		records = append(records, &record)
	}

	return records, nil
}

// RecordExists returns true if the record with given ID exists
func (s *SecurityOpsContract) RecordExists(ctx contractapi.TransactionContextInterface, id string) (bool, error) {
	recordJSON, err := ctx.GetStub().GetState(id)
	if err != nil {
		return false, fmt.Errorf("failed to read from world state: %v", err)
	}

	return recordJSON != nil, nil
}

// UpdateRecord updates an existing record
func (s *SecurityOpsContract) UpdateRecord(ctx contractapi.TransactionContextInterface, id string, content string, updatedBy string) error {
	record, err := s.GetRecord(ctx, id)
	if err != nil {
		return err
	}

	// Parse content from JSON string
	var contentMap map[string]interface{}
	err = json.Unmarshal([]byte(content), &contentMap)
	if err != nil {
		return fmt.Errorf("failed to parse content JSON: %v", err)
	}

	// Update record
	record.Content = contentMap
	record.AuditHistory = append(record.AuditHistory, AuditEntry{
		Timestamp: time.Now().Format(time.RFC3339),
		UserID:    updatedBy,
		Action:    "update",
		Details:   "Record content updated",
	})

	recordJSON, err := json.Marshal(record)
	if err != nil {
		return fmt.Errorf("failed to marshal record: %v", err)
	}

	return ctx.GetStub().PutState(id, recordJSON)
}

// GetRecordsByType returns all records of a specific type
func (s *SecurityOpsContract) GetRecordsByType(ctx contractapi.TransactionContextInterface, recordType string) ([]*SecurityRecord, error) {
	allRecords, err := s.GetAllRecords(ctx)
	if err != nil {
		return nil, err
	}

	var filteredRecords []*SecurityRecord
	for _, record := range allRecords {
		if record.Type == recordType {
			filteredRecords = append(filteredRecords, record)
		}
	}

	return filteredRecords, nil
}

// GetRecordHistory returns the history of a record
func (s *SecurityOpsContract) GetRecordHistory(ctx contractapi.TransactionContextInterface, id string) ([]AuditEntry, error) {
	record, err := s.GetRecord(ctx, id)
	if err != nil {
		return nil, err
	}

	return record.AuditHistory, nil
}

func main() {
	chaincode, err := contractapi.NewChaincode(&SecurityOpsContract{})
	if err != nil {
		fmt.Printf("Error creating SecurityOps chaincode: %v", err)
		return
	}

	if err := chaincode.Start(); err != nil {
		fmt.Printf("Error starting SecurityOps chaincode: %v", err)
	}
} 