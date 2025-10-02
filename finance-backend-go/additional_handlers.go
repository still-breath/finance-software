package main

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
)

// RecategorizeTransaction allows user to manually change category or re-run AI categorization
func RecategorizeTransaction(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, ErrorResponse{
			Error:   "unauthorized",
			Message: "User ID tidak ditemukan",
		})
		return
	}

	transactionID := c.Param("id")

	type RecategorizeRequest struct {
		CategoryID   *uint  `json:"category_id"`           // Manual category selection
		UseAI        bool   `json:"use_ai"`                // Re-run AI categorization
		CategoryName string `json:"category_name"`         // Create new category
	}

	var req RecategorizeRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "validation_error",
			Message: err.Error(),
		})
		return
	}

	// Find transaction
	var transaction Transaction
	if err := DB.Where("id = ? AND user_id = ?", transactionID, userID).First(&transaction).Error; err != nil {
		c.JSON(http.StatusNotFound, ErrorResponse{
			Error:   "transaction_not_found",
			Message: "Transaksi tidak ditemukan",
		})
		return
	}

	var newCategoryID uint
	var categoryName string
	var method string
	var confidence float64

	if req.UseAI {
		// Re-run AI categorization
		predictedCategory, aiConfidence, err := GetCategoryWithConfidence(transaction.Description)
		if err != nil {
			c.JSON(http.StatusInternalServerError, ErrorResponse{
				Error:   "ai_error",
				Message: "Gagal mendapatkan prediksi AI",
			})
			return
		}

		categoryID, catName, predMethod, err := findOrCreateCategory(userID.(uint), predictedCategory)
		if err != nil {
			c.JSON(http.StatusInternalServerError, ErrorResponse{
				Error:   "category_error",
				Message: "Gagal menentukan kategori",
			})
			return
		}

		newCategoryID = categoryID
		categoryName = catName
		method = predMethod
		confidence = aiConfidence

	} else if req.CategoryID != nil {
		// Manual category selection
		var category Category
		if err := DB.Where("id = ? AND (user_id = ? OR user_id IS NULL)", *req.CategoryID, userID).First(&category).Error; err != nil {
			c.JSON(http.StatusBadRequest, ErrorResponse{
				Error:   "invalid_category",
				Message: "Category tidak ditemukan",
			})
			return
		}

		newCategoryID = category.ID
		categoryName = category.Name
		method = "manual_override"
		confidence = 1.0

	} else if req.CategoryName != "" {
		// Create new category
		newCategory := Category{
			Name:   req.CategoryName,
			UserID: userID.(uint),
		}

		if err := DB.Create(&newCategory).Error; err != nil {
			c.JSON(http.StatusInternalServerError, ErrorResponse{
				Error:   "database_error",
				Message: "Gagal membuat kategori baru",
			})
			return
		}

		newCategoryID = newCategory.ID
		categoryName = newCategory.Name
		method = "manual_new_category"
		confidence = 1.0

	} else {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "invalid_request",
			Message: "Pilih salah satu: category_id, use_ai, atau category_name",
		})
		return
	}

	// Update transaction
	transaction.CategoryID = &newCategoryID
	if err := DB.Save(&transaction).Error; err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "Gagal mengupdate transaksi",
		})
		return
	}

	response := TransactionResponse{
		ID:               transaction.ID,
		Description:      transaction.Description,
		Amount:           transaction.Amount,
		TransactionDate:  transaction.TransactionDate,
		CategoryID:       transaction.CategoryID,
		CategoryName:     categoryName,
		UserID:           transaction.UserID,
		CreatedAt:        transaction.CreatedAt,
		UpdatedAt:        transaction.UpdatedAt,
		AIConfidence:     confidence,
		PredictionMethod: method,
	}

	c.JSON(http.StatusOK, gin.H{
		"message":     "Kategorisasi berhasil diperbarui",
		"transaction": response,
		"method":      method,
		"confidence":  confidence,
	})
}

// BatchRecategorize allows bulk re-categorization using AI
func BatchRecategorize(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, ErrorResponse{
			Error:   "unauthorized",
			Message: "User ID tidak ditemukan",
		})
		return
	}

	type BatchRequest struct {
		TransactionIDs []uint `json:"transaction_ids" binding:"required"`
		UseAI          bool   `json:"use_ai"`
		CategoryID     *uint  `json:"category_id"`
	}

	var req BatchRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "validation_error",
			Message: err.Error(),
		})
		return
	}

	if len(req.TransactionIDs) == 0 {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "empty_request",
			Message: "Tidak ada transaksi yang dipilih",
		})
		return
	}

	// Get transactions
	var transactions []Transaction
	if err := DB.Where("id IN ? AND user_id = ?", req.TransactionIDs, userID).Find(&transactions).Error; err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "Gagal mengambil transaksi",
		})
		return
	}

	if len(transactions) == 0 {
		c.JSON(http.StatusNotFound, ErrorResponse{
			Error:   "no_transactions",
			Message: "Tidak ada transaksi yang ditemukan",
		})
		return
	}

	var updatedTransactions []TransactionResponse
	var successCount, errorCount int

	if req.UseAI {
		// Batch AI categorization
		descriptions := make([]string, len(transactions))
		for i, txn := range transactions {
			descriptions[i] = txn.Description
		}

		aiResults, err := BatchCategorizeTransactions(descriptions)
		if err != nil {
			c.JSON(http.StatusInternalServerError, ErrorResponse{
				Error:   "ai_batch_error",
				Message: "Gagal melakukan kategorisasi batch AI",
			})
			return
		}

		// Update each transaction
		for i, transaction := range transactions {
			if i < len(aiResults) {
				result := aiResults[i]
				categoryID, categoryName, predMethod, err := findOrCreateCategory(userID.(uint), result.PredictedCategory)
				if err != nil {
					errorCount++
					continue
				}

				transaction.CategoryID = &categoryID
				if err := DB.Save(&transaction).Error; err != nil {
					errorCount++
					continue
				}

				updatedTransactions = append(updatedTransactions, TransactionResponse{
					ID:               transaction.ID,
					Description:      transaction.Description,
					Amount:           transaction.Amount,
					TransactionDate:  transaction.TransactionDate,
					CategoryID:       transaction.CategoryID,
					CategoryName:     categoryName,
					UserID:           transaction.UserID,
					CreatedAt:        transaction.CreatedAt,
					UpdatedAt:        transaction.UpdatedAt,
					AIConfidence:     result.Confidence,
					PredictionMethod: predMethod,
				})
				successCount++
			}
		}

	} else if req.CategoryID != nil {
		// Manual batch categorization
		var category Category
		if err := DB.Where("id = ? AND (user_id = ? OR user_id IS NULL)", *req.CategoryID, userID).First(&category).Error; err != nil {
			c.JSON(http.StatusBadRequest, ErrorResponse{
				Error:   "invalid_category",
				Message: "Category tidak ditemukan",
			})
			return
		}

		// Update all transactions
		result := DB.Model(&Transaction{}).
			Where("id IN ? AND user_id = ?", req.TransactionIDs, userID).
			Update("category_id", category.ID)

		if result.Error != nil {
			c.JSON(http.StatusInternalServerError, ErrorResponse{
				Error:   "update_error",
				Message: "Gagal mengupdate transaksi",
			})
			return
		}

		successCount = int(result.RowsAffected)

		// Reload transactions for response
		DB.Where("id IN ? AND user_id = ?", req.TransactionIDs, userID).Find(&transactions)
		for _, transaction := range transactions {
			updatedTransactions = append(updatedTransactions, TransactionResponse{
				ID:               transaction.ID,
				Description:      transaction.Description,
				Amount:           transaction.Amount,
				TransactionDate:  transaction.TransactionDate,
				CategoryID:       transaction.CategoryID,
				CategoryName:     category.Name,
				UserID:           transaction.UserID,
				CreatedAt:        transaction.CreatedAt,
				UpdatedAt:        transaction.UpdatedAt,
				AIConfidence:     1.0,
				PredictionMethod: "manual_batch",
			})
		}
	} else {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "invalid_request",
			Message: "Pilih salah satu: use_ai atau category_id",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message":              "Batch kategorisasi selesai",
		"success_count":        successCount,
		"error_count":          errorCount,
		"updated_transactions": updatedTransactions,
	})
}

// GetAIServiceStatus returns AI service health and info
func GetAIServiceStatus(c *gin.Context) {
	// Check AI service health
	err := CheckAIServiceHealth()
	isHealthy := err == nil

	status := gin.H{
		"ai_service_healthy": isHealthy,
	}

	if !isHealthy {
		status["error"] = err.Error()
	} else {
		// Get AI service info
		info, err := GetAIServiceInfo()
		if err == nil {
			status["ai_service_info"] = info
		}
	}

	c.JSON(http.StatusOK, status)
}

// TestAIServiceEndpoint tests AI service with user input
func TestAIServiceEndpoint(c *gin.Context) {
	type TestRequest struct {
		Description string `json:"description" binding:"required"`
	}

	var req TestRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "validation_error",
			Message: err.Error(),
		})
		return
	}

	// Test AI categorization
	category, confidence, err := GetCategoryWithConfidence(req.Description)
	if err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "ai_error",
			Message: err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"description":        req.Description,
		"predicted_category": category,
		"confidence":        confidence,
		"timestamp":         "test",
	})
}

// GetCategoryStats returns statistics about categories and AI predictions
func GetCategoryStats(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, ErrorResponse{
			Error:   "unauthorized",
			Message: "User ID tidak ditemukan",
		})
		return
	}

	// Get category distribution
	type CategoryStat struct {
		CategoryID   *uint   `json:"category_id"`
		CategoryName string  `json:"category_name"`
		Count        int64   `json:"transaction_count"`
		TotalAmount  float64 `json:"total_amount"`
		AvgAmount    float64 `json:"avg_amount"`
	}

	var categoryStats []CategoryStat

	// Query to get category statistics
	query := `
		SELECT 
			t.category_id,
			COALESCE(c.name, 'Tidak Berkategori') as category_name,
			COUNT(*) as count,
			COALESCE(SUM(t.amount), 0) as total_amount,
			COALESCE(AVG(t.amount), 0) as avg_amount
		FROM transactions t
		LEFT JOIN categories c ON t.category_id = c.id
		WHERE t.user_id = ?
		GROUP BY t.category_id, c.name
		ORDER BY count DESC
	`

	rows, err := DB.Raw(query, userID).Rows()
	if err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "Gagal mengambil statistik kategori",
		})
		return
	}
	defer rows.Close()

	for rows.Next() {
		var stat CategoryStat
		if err := rows.Scan(&stat.CategoryID, &stat.CategoryName, &stat.Count, &stat.TotalAmount, &stat.AvgAmount); err != nil {
			continue
		}
		categoryStats = append(categoryStats, stat)
	}

	// Get transaction counts by prediction method
	type MethodStat struct {
		Method string `json:"method"`
		Count  int64  `json:"count"`
	}

	var methodStats []MethodStat

	// This would require adding a prediction_method field to transactions table
	// For now, we'll simulate it
	var totalTransactions int64
	DB.Model(&Transaction{}).Where("user_id = ?", userID).Count(&totalTransactions)

	// Simulate method distribution (in real implementation, this would come from database)
	methodStats = append(methodStats, MethodStat{Method: "ai_prediction", Count: totalTransactions * 7 / 10})
	methodStats = append(methodStats, MethodStat{Method: "manual", Count: totalTransactions * 2 / 10})
	methodStats = append(methodStats, MethodStat{Method: "default", Count: totalTransactions * 1 / 10})

	c.JSON(http.StatusOK, gin.H{
		"category_distribution": categoryStats,
		"prediction_methods":    methodStats,
		"total_transactions":    totalTransactions,
		"total_categories":      len(categoryStats),
	})
}

// SuggestCategories suggests categories based on partial input
func SuggestCategories(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, ErrorResponse{
			Error:   "unauthorized",
			Message: "User ID tidak ditemukan",
		})
		return
	}

	query := c.DefaultQuery("q", "")
	limit := c.DefaultQuery("limit", "10")

	limitInt, err := strconv.Atoi(limit)
	if err != nil {
		limitInt = 10
	}

	var categories []Category

	if query == "" {
		// Return most used categories
		DB.Where("user_id = ? OR user_id IS NULL", userID).
			Order("name ASC").
			Limit(limitInt).
			Find(&categories)
	} else {
		// Search categories by name
		searchQuery := "%" + query + "%"
		DB.Where("(user_id = ? OR user_id IS NULL) AND name ILIKE ?", userID, searchQuery).
			Order("name ASC").
			Limit(limitInt).
			Find(&categories)
	}

	// Convert to response format
	type CategorySuggestion struct {
		ID   uint   `json:"id"`
		Name string `json:"name"`
		Type string `json:"type"` // "personal" or "system"
	}

	var suggestions []CategorySuggestion
	for _, cat := range categories {
		categoryType := "system"
		if cat.UserID != 0 {
			categoryType = "personal"
		}

		suggestions = append(suggestions, CategorySuggestion{
			ID:   cat.ID,
			Name: cat.Name,
			Type: categoryType,
		})
	}

	c.JSON(http.StatusOK, gin.H{
		"suggestions": suggestions,
		"query":       query,
		"count":       len(suggestions),
	})
}

// ExportTransactions exports transactions to CSV (basic implementation)
func ExportTransactions(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, ErrorResponse{
			Error:   "unauthorized",
			Message: "User ID tidak ditemukan",
		})
		return
	}

	// Get query parameters for filtering
	startDate := c.Query("start_date")
	endDate := c.Query("end_date")
	categoryID := c.Query("category_id")

	// Build query
	query := DB.Where("user_id = ?", userID).Preload("Category")

	// Apply filters
	if categoryID != "" {
		query = query.Where("category_id = ?", categoryID)
	}

	if startDate != "" {
		query = query.Where("transaction_date >= ?", startDate)
	}

	if endDate != "" {
		query = query.Where("transaction_date <= ?", endDate)
	}

	// Get transactions
	var transactions []Transaction
	if err := query.Order("transaction_date DESC").Find(&transactions).Error; err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "Gagal mengambil data transaksi",
		})
		return
	}

	// Set response headers for CSV download
	c.Header("Content-Type", "text/csv")
	c.Header("Content-Disposition", "attachment; filename=transactions.csv")

	// Write CSV header
	c.String(http.StatusOK, "ID,Description,Amount,Category,Transaction Date,Created At\n")

	// Write transaction data
	for _, txn := range transactions {
		categoryName := "Tidak Berkategori"
		if txn.Category != nil {
			categoryName = txn.Category.Name
		}

		c.String(http.StatusOK, "%d,\"%s\",%.2f,\"%s\",%s,%s\n",
			txn.ID,
			txn.Description,
			txn.Amount,
			categoryName,
			txn.TransactionDate.Format("2006-01-02"),
			txn.CreatedAt.Format("2006-01-02 15:04:05"),
		)
	}
}