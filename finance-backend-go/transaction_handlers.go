package main

import (
	"fmt"
	"log"
	"net/http"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

// Transaction request/response structures
type CreateTransactionRequest struct {
	Description     string     `json:"description" binding:"required,max=255"`
	Amount          float64    `json:"amount" binding:"required"`
	TransactionDate *time.Time `json:"transaction_date"`
}

type TransactionResponse struct {
	ID               uint      `json:"id"`
	Description      string    `json:"description"`
	Amount           float64   `json:"amount"`
	TransactionDate  time.Time `json:"transaction_date"`
	CategoryID       *uint     `json:"category_id"`
	CategoryName     string    `json:"category_name,omitempty"`
	UserID           uint      `json:"user_id"`
	CreatedAt        time.Time `json:"created_at"`
	UpdatedAt        time.Time `json:"updated_at"`
	AIConfidence     float64   `json:"ai_confidence,omitempty"`
	PredictionMethod string    `json:"prediction_method,omitempty"`
}

// JWT Middleware
func JWTMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		// Get token from Authorization header
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.JSON(http.StatusUnauthorized, ErrorResponse{
				Error:   "missing_token",
				Message: "Token authorization diperlukan",
			})
			c.Abort()
			return
		}

		// Check Bearer format
		tokenParts := strings.SplitN(authHeader, " ", 2)
		if len(tokenParts) != 2 || tokenParts[0] != "Bearer" {
			c.JSON(http.StatusUnauthorized, ErrorResponse{
				Error:   "invalid_token_format",
				Message: "Format token harus 'Bearer <token>'",
			})
			c.Abort()
			return
		}

		tokenString := tokenParts[1]

		// Validate token
		claims, err := validateJWT(tokenString)
		if err != nil {
			c.JSON(http.StatusUnauthorized, ErrorResponse{
				Error:   "invalid_token",
				Message: "Token tidak valid atau sudah expired",
			})
			c.Abort()
			return
		}

		// Set user info in context
		c.Set("user_id", claims.UserID)
		c.Set("username", claims.Username)

		c.Next()
	}
}

// CreateTransaction handles creating a new transaction with AI categorization
func CreateTransaction(c *gin.Context) {
	var req CreateTransactionRequest

	// Bind JSON request
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "validation_error",
			Message: err.Error(),
		})
		return
	}

	// Get user ID from JWT token (set by middleware)
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, ErrorResponse{
			Error:   "unauthorized",
			Message: "User ID tidak ditemukan",
		})
		return
	}

	// Call AI service to get category prediction
	predictedCategory, confidence, err := GetCategoryWithConfidence(req.Description)
	if err != nil {
		// Log error but don't fail the transaction
		log.Printf("AI categorization failed: %v", err)
		predictedCategory = "Lainnya"
		confidence = 0.0
	}

	// Find or create category in database
	categoryID, categoryName, predictionMethod, err := findOrCreateCategory(userID.(uint), predictedCategory)
	if err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "category_error",
			Message: "Gagal menentukan kategori transaksi",
		})
		return
	}

	// Set default transaction date if not provided
	transactionDate := time.Now()
	if req.TransactionDate != nil {
		transactionDate = *req.TransactionDate
	}

	// Create new transaction
	transaction := Transaction{
		Description:     req.Description,
		Amount:          req.Amount,
		TransactionDate: transactionDate,
		UserID:          userID.(uint),
		CategoryID:      &categoryID,
	}

	if err := DB.Create(&transaction).Error; err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "Gagal menyimpan transaksi",
		})
		return
	}

	// Return response with AI categorization info
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
		PredictionMethod: predictionMethod,
	}

	c.JSON(http.StatusCreated, gin.H{
		"message":     "Transaksi berhasil dibuat dengan kategorisasi otomatis",
		"transaction": response,
		"ai_info": gin.H{
			"predicted_category": predictedCategory,
			"confidence":         confidence,
			"method":             predictionMethod,
		},
	})
}

// findOrCreateCategory finds existing category or creates new one
func findOrCreateCategory(userID uint, categoryName string) (uint, string, string, error) {
	var category Category
	var predictionMethod string = "ai_categorization"

	// First, try to find existing category (user's personal or system category)
	err := DB.Where("name = ? AND (user_id = ? OR user_id IS NULL)", categoryName, userID).First(&category).Error
	if err == nil {
		// Category exists
		return category.ID, category.Name, predictionMethod, nil
	}

	// If category doesn't exist, create it as user's personal category
	if err == gorm.ErrRecordNotFound {
		newCategory := Category{
			Name:   categoryName,
			UserID: userID,
		}

		if err := DB.Create(&newCategory).Error; err != nil {
			return 0, "", predictionMethod, fmt.Errorf("failed to create category: %w", err)
		}

		return newCategory.ID, newCategory.Name, predictionMethod + "_new_category", nil
	}

	// Other database error
	return 0, "", predictionMethod, fmt.Errorf("database error finding category: %w", err)
}

// GetTransactions handles fetching all transactions for logged-in user
func GetTransactions(c *gin.Context) {
	// Get user ID from JWT token (set by middleware)
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, ErrorResponse{
			Error:   "unauthorized",
			Message: "User ID tidak ditemukan",
		})
		return
	}

	// Query parameters for filtering
	categoryID := c.Query("category_id")
	startDate := c.Query("start_date")
	endDate := c.Query("end_date")

	// Build query
	query := DB.Where("user_id = ?", userID).Preload("Category")

	// Apply filters
	if categoryID != "" {
		query = query.Where("category_id = ?", categoryID)
	}

	if startDate != "" {
		if parsedDate, err := time.Parse("2006-01-02", startDate); err == nil {
			query = query.Where("transaction_date >= ?", parsedDate)
		}
	}

	if endDate != "" {
		if parsedDate, err := time.Parse("2006-01-02", endDate); err == nil {
			// Add 23:59:59 to include the whole day
			endDateTime := parsedDate.Add(23*time.Hour + 59*time.Minute + 59*time.Second)
			query = query.Where("transaction_date <= ?", endDateTime)
		}
	}

	// Get transactions
	var transactions []Transaction
	if err := query.Order("transaction_date DESC, created_at DESC").Find(&transactions).Error; err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "Gagal mengambil data transaksi",
		})
		return
	}

	// Convert to response format
	var responseTransactions []TransactionResponse
	for _, transaction := range transactions {
		var categoryName string
		if transaction.Category != nil {
			categoryName = transaction.Category.Name
		}

		responseTransactions = append(responseTransactions, TransactionResponse{
			ID:               transaction.ID,
			Description:      transaction.Description,
			Amount:           transaction.Amount,
			TransactionDate:  transaction.TransactionDate,
			CategoryID:       transaction.CategoryID,
			CategoryName:     categoryName,
			UserID:           transaction.UserID,
			CreatedAt:        transaction.CreatedAt,
			UpdatedAt:        transaction.UpdatedAt,
			AIConfidence:     0.0,      // Historical transactions don't have AI confidence
			PredictionMethod: "manual", // Historical transactions are manual
		})
	}

	// Calculate total amount
	var totalAmount float64
	for _, transaction := range transactions {
		totalAmount += transaction.Amount
	}

	c.JSON(http.StatusOK, gin.H{
		"message":      "Data transaksi berhasil diambil",
		"transactions": responseTransactions,
		"total_count":  len(responseTransactions),
		"total_amount": totalAmount,
		"filters": gin.H{
			"category_id": categoryID,
			"start_date":  startDate,
			"end_date":    endDate,
		},
	})
}
