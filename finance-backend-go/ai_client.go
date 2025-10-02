package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

// AI service request/response structures
type AIRequest struct {
	Description string `json:"description"`
}

type AIResponse struct {
	Description       string  `json:"description"`
	PredictedCategory string  `json:"predicted_category"`
	Confidence        float64 `json:"confidence"`
	PredictionMethod  string  `json:"prediction_method,omitempty"`
	Timestamp         string  `json:"timestamp,omitempty"`
}

type AIErrorResponse struct {
	Error   string `json:"error"`
	Message string `json:"message"`
}

// HTTP client for AI service
var aiClient = &http.Client{
	Timeout: 10 * time.Second,
}

// GetCategoryWithConfidence returns both category and confidence score
func GetCategoryWithConfidence(description string) (string, float64, error) {
	if description == "" {
		return "Lainnya", 0.0, nil
	}

	// Get AI service URL from environment
	aiServiceURL := getEnv("AI_SERVICE_URL", "http://localhost:5000")
	endpoint := aiServiceURL + "/categorize"

	// Create request payload
	requestData := AIRequest{
		Description: description,
	}

	// Marshal to JSON
	jsonData, err := json.Marshal(requestData)
	if err != nil {
		return "Lainnya", 0.0, fmt.Errorf("failed to marshal request: %w", err)
	}

	// Create HTTP request
	req, err := http.NewRequest("POST", endpoint, bytes.NewBuffer(jsonData))
	if err != nil {
		return "Lainnya", 0.0, fmt.Errorf("failed to create request: %w", err)
	}

	// Set headers
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Accept", "application/json")

	// Send request
	resp, err := aiClient.Do(req)
	if err != nil {
		return "Lainnya", 0.0, fmt.Errorf("failed to send request: %w", err)
	}
	defer resp.Body.Close()

	// Read response body
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "Lainnya", 0.0, fmt.Errorf("failed to read response: %w", err)
	}

	// Check status code
	if resp.StatusCode != http.StatusOK {
		var errorResp AIErrorResponse
		if err := json.Unmarshal(body, &errorResp); err == nil {
			return "Lainnya", 0.0, fmt.Errorf("AI service error (%d): %s", resp.StatusCode, errorResp.Message)
		}
		return "Lainnya", 0.0, fmt.Errorf("AI service error (%d): %s", resp.StatusCode, string(body))
	}

	// Parse response
	var aiResp AIResponse
	if err := json.Unmarshal(body, &aiResp); err != nil {
		return "Lainnya", 0.0, fmt.Errorf("failed to parse response: %w", err)
	}

	// Validate response
	if aiResp.PredictedCategory == "" {
		return "Lainnya", 0.0, nil
	}

	return aiResp.PredictedCategory, aiResp.Confidence, nil
}

// GetCategoryFromAI calls the AI service to predict transaction category
func GetCategoryFromAI(description string) (string, error) {
	category, _, err := GetCategoryWithConfidence(description)
	return category, err
}

// BatchCategorizeTransactions categorizes multiple transactions at once
func BatchCategorizeTransactions(descriptions []string) ([]AIResponse, error) {
	if len(descriptions) == 0 {
		return []AIResponse{}, nil
	}

	// Get AI service URL from environment
	aiServiceURL := getEnv("AI_SERVICE_URL", "http://localhost:5000")
	endpoint := aiServiceURL + "/categorize/batch"

	// Create batch request payload
	type BatchRequest struct {
		Transactions []AIRequest `json:"transactions"`
	}

	var transactions []AIRequest
	for _, desc := range descriptions {
		transactions = append(transactions, AIRequest{Description: desc})
	}

	requestData := BatchRequest{
		Transactions: transactions,
	}

	// Marshal to JSON
	jsonData, err := json.Marshal(requestData)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal batch request: %w", err)
	}

	// Create HTTP request
	req, err := http.NewRequest("POST", endpoint, bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("failed to create batch request: %w", err)
	}

	// Set headers
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Accept", "application/json")

	// Send request
	resp, err := aiClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to send batch request: %w", err)
	}
	defer resp.Body.Close()

	// Read response body
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read batch response: %w", err)
	}

	// Check status code
	if resp.StatusCode != http.StatusOK {
		var errorResp AIErrorResponse
		if err := json.Unmarshal(body, &errorResp); err == nil {
			return nil, fmt.Errorf("AI service batch error (%d): %s", resp.StatusCode, errorResp.Message)
		}
		return nil, fmt.Errorf("AI service batch error (%d): %s", resp.StatusCode, string(body))
	}

	// Parse batch response
	type BatchResponse struct {
		Results        []AIResponse `json:"results"`
		TotalProcessed int          `json:"total_processed"`
		Timestamp      string       `json:"timestamp"`
	}

	var batchResp BatchResponse
	if err := json.Unmarshal(body, &batchResp); err != nil {
		return nil, fmt.Errorf("failed to parse batch response: %w", err)
	}

	return batchResp.Results, nil
}

// CheckAIServiceHealth checks if the AI service is healthy
func CheckAIServiceHealth() error {
	aiServiceURL := getEnv("AI_SERVICE_URL", "http://localhost:5000")
	endpoint := aiServiceURL + "/health"

	req, err := http.NewRequest("GET", endpoint, nil)
	if err != nil {
		return fmt.Errorf("failed to create health check request: %w", err)
	}

	resp, err := aiClient.Do(req)
	if err != nil {
		return fmt.Errorf("AI service unreachable: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("AI service unhealthy: status %d", resp.StatusCode)
	}

	return nil
}

// GetAIServiceInfo returns information about the AI service
func GetAIServiceInfo() (map[string]interface{}, error) {
	aiServiceURL := getEnv("AI_SERVICE_URL", "http://localhost:5000")
	endpoint := aiServiceURL + "/health"

	req, err := http.NewRequest("GET", endpoint, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create info request: %w", err)
	}

	resp, err := aiClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to get AI service info: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read info response: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("AI service info error: status %d", resp.StatusCode)
	}

	var info map[string]interface{}
	if err := json.Unmarshal(body, &info); err != nil {
		return nil, fmt.Errorf("failed to parse info response: %w", err)
	}

	return info, nil
}

// TestAIService tests the AI service with a sample transaction
func TestAIService() error {
	testDescription := "Beli nasi ayam di warteg"

	category, confidence, err := GetCategoryWithConfidence(testDescription)
	if err != nil {
		return fmt.Errorf("AI service test failed: %w", err)
	}

	if category == "" {
		return fmt.Errorf("AI service returned empty category")
	}

	// Log test result
	fmt.Printf("AI Service Test - Description: '%s' -> Category: '%s' (Confidence: %.3f)\n",
		testDescription, category, confidence)

	return nil
}
